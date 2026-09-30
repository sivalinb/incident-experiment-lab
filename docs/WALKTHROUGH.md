# Learning walkthrough

## Guided experiment

1. Run Compare volatile and durable queues in simulation mode.
2. Inspect lost_ids, delivered IDs, recovery ratios, and backlog charts.
3. Reduce queue capacity to force admission rejection. Notice that rejected events are not counted as accepted-event loss.
4. Fetch NAB taxi or CPU observations and enable the public arrival profile in simulation mode. The first values are rescaled to 1–5 arrivals per tick.
5. Switch to Live Apple Container. The worker opens a real HTTP sink, starts a broker child process, forces 503 responses, kills the broker, and restarts it.
6. Compare volatile memory storage with SQLite WAL persistence using the same injected timeline.

## Questions to answer in your portfolio write-up

1. What concrete failure does this experiment expose?
2. Which checks happen before execution, and which need runtime observations?
3. Which input, configuration, image, and model versions were used?
4. What did the positive and negative controls demonstrate?
5. Where could the measurements be misleading?
6. Which follow-up experiment would challenge your conclusion?

## Suggested demonstration

Record a three-minute walkthrough: explain the failure in one sentence, run a baseline, introduce one deliberate change, inspect the evidence, and explain the tradeoff. Include the downloadable report and the command needed to reproduce it. Prefer measured operational behavior over an unsupported claim of production readiness.

## Next extensions

Add one extension only after retaining a passing baseline: more realistic public workloads, an additional failure mode, stricter provenance, a larger evaluation set, or a runtime-version comparison. Preserve fixture/live distinctions and document negative results. The other four repositories in this portfolio can reuse the report schema without creating a runtime dependency on each other.
