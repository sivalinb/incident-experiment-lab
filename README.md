# Incident Experiment Lab

[![Verify](https://github.com/sivalinb/incident-experiment-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/sivalinb/incident-experiment-lab/actions/workflows/ci.yml)

A queue configuration can look resilient while losing accepted events after a crash. This project compares recovery policies using explicit event identities and delivery accounting.

Python · Streamlit · Pkl · Apple Container · evaluation evidence · OpenTelemetry

## Start here

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py --server.port 8503
```

The interface opens at http://127.0.0.1:8503. Portable demos work without a model, API key, Pkl executable, or container runtime. The configuration fallback is a checked export whose source hash must match the committed Pkl source. Every report identifies its mode.

## Walkthrough

1. Run Compare volatile and durable queues in simulation mode.
2. Inspect lost_ids, delivered IDs, recovery ratios, and backlog charts.
3. Reduce queue capacity to force admission rejection. Notice that rejected events are not counted as accepted-event loss.
4. Fetch NAB taxi or CPU observations and enable the public arrival profile in simulation mode. The first values are rescaled to 1–5 arrivals per tick.
5. Switch to Live Apple Container. The worker opens a real HTTP sink, starts a broker child process, forces 503 responses, kills the broker, and restarts it.
6. Compare volatile memory storage with SQLite WAL persistence using the same injected timeline.

## Architecture

Pkl failure timeline → validated experiment → deterministic simulator or real HTTP broker/sink → downstream outage → broker process crash/restart → drain → accepted/delivered/rejected/duplicate accounting.

The Streamlit UI calls pure Python engines; each repository vendors a small `labcore` package so cloning this repository is sufficient. No sibling repository is required.

## CLI and checks

```bash
python scripts/run.py
python scripts/run.py --live
pytest -q
python scripts/evaluate.py
python scripts/export_config.py   # requires pkl on PATH or PKL_BIN
```

## Observed verification

22 automated tests passed locally. A real broker-process crash lost 15/60 accepted records with a volatile queue; SQLite WAL recovered 60/60 in the same experiment. See [verified results and evidence](docs/VALIDATION.md) for settings, provenance, and limitations.

## Documentation

- [Setup and live runtime](docs/SETUP.md)
- [Architecture and decisions](docs/ARCHITECTURE.md)
- [Learning walkthrough](docs/WALKTHROUGH.md)
- [Evaluation methodology](docs/EVALUATION.md)
- [Public sources and licenses](docs/DATA_SOURCES.md)
- [Observability and AI](docs/OPERATIONS.md)
- [Security and limitations](docs/SECURITY.md)
- [Verified results](docs/VALIDATION.md)

MIT-licensed project code. External datasets and references retain their own terms. Public inputs are fetched explicitly and kept under ignored `artifacts/`; no private production telemetry is included.
