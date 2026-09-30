"""Loss accounting for deterministic experiments and actual HTTP recovery workloads."""
from collections import deque
import json
from pathlib import Path
import statistics
from pydantic import BaseModel, Field, model_validator
from labcore.runtime import AppleContainer


class Experiment(BaseModel):
    events: int = Field(default=60,ge=10,le=500)
    queueCapacity: int = Field(default=100,ge=5,le=1000)
    outageStart: int = Field(default=15,ge=0)
    outageEnd: int = Field(default=45,ge=1)
    crashAt: int = Field(default=30,ge=0)
    drainPerTick: int = Field(default=3,ge=1,le=20)
    @model_validator(mode="after")
    def ordered(self):
        if not self.outageStart <= self.crashAt < self.outageEnd < self.events:
            raise ValueError("Require outageStart <= crashAt < outageEnd < events")
        return self


def simulate(config, durable=True, arrivals=None):
    c = Experiment.model_validate(config)
    queue = deque()
    accepted, rejected, delivered, lost = [], [], [], []
    timeline, latencies = [], []
    counts = arrivals or [1] * c.events
    if len(counts) != c.events or any(not isinstance(n,int) or n<0 or n>20 for n in counts):
        raise ValueError("Arrival profile must contain events integer counts between 0 and 20")
    next_id = 0
    for tick in range(c.events + c.events * 20 + 1):
        if tick == c.crashAt and not durable:
            lost.extend(x[0] for x in queue)
            queue.clear()
        if tick < c.events:
            for _ in range(counts[tick]):
                event = (next_id,tick)
                next_id += 1
                if len(queue) < c.queueCapacity:
                    queue.append(event)
                    accepted.append(event[0])
                else:
                    rejected.append(event[0])
        available = not c.outageStart <= tick < c.outageEnd
        if available:
            for _ in range(min(c.drainPerTick,len(queue))):
                identity, created = queue.popleft()
                delivered.append(identity)
                latencies.append(tick-created)
        timeline.append({"tick":tick,"queue_depth":len(queue),"delivered":len(delivered),"sink_available":int(available)})
        if tick >= c.events and not queue:
            break
    lost = sorted(set(accepted)-set(delivered))
    return {"mode":"deterministic simulation", "policy":"durable" if durable else "volatile", "config":c.model_dump(),
            "accepted":len(accepted),"rejected":len(rejected),"delivered_unique":len(set(delivered)),
            "lost":len(lost),"duplicates":len(delivered)-len(set(delivered)),
            "recovery_ratio":len(set(delivered))/len(accepted) if accepted else 1,
            "latency_ticks_mean":statistics.mean(latencies) if latencies else 0,
            "peak_queue":max(x["queue_depth"] for x in timeline),"timeline":timeline,
            "lost_ids":lost, "delivery_ids":delivered,
            "diagnosis":"volatile queue lost accepted records at crash" if lost else "all accepted records delivered"}


def public_arrivals(path, events):
    import pandas as pd
    frame = pd.read_csv(path)
    if "value" not in frame:
        raise ValueError("Public arrival profile needs a numeric value column (e.g. NAB data)")
    values = pd.to_numeric(frame["value"],errors="coerce").dropna().iloc[:events]
    if len(values) < events:
        raise ValueError("Not enough numeric observations")
    lo,hi = float(values.min()),float(values.max())
    return [1 + round(4*(float(v)-lo)/(hi-lo)) if hi>lo else 1 for v in values]


def live(root: Path, config, durable=True):
    c = Experiment.model_validate(config)
    result = AppleContainer().run("python:3.12-slim", ["python", "/work/live_experiment.py", json.dumps(c.model_dump()), "durable" if durable else "volatile"],
                                  mounts=[(root/"workloads","/work","ro")], timeout=60, memory_mb=256)
    if result.returncode:
        raise RuntimeError(result.stderr or result.reason)
    report = json.loads(result.stdout.strip().splitlines()[-1])
    report.update({"mode":"live HTTP queue / Apple Container", "duration_s":result.duration_s,
                   "scope":"Instrumented Python queue workload; not a measurement of the OTel Collector", "config":c.model_dump()})
    return report
