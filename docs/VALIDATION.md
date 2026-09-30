# Verified results

Verified on 2026-09-30 UTC (2026-09-29 Mountain Time). This page reports observed development checks, not production reliability guarantees. The committed JSON evidence contains synthetic workloads, public-source metadata, and measured results. Secrets, local usernames, and source-cache contents are excluded.

## Portable checks

- `pytest -q`: **22 passed**, including the Streamlit primary workflow.
- `python scripts/evaluate.py`: all domain checks passed; retrieval hit@3 was 1.0 on five authored questions, and the unrelated-question abstention check passed.
- Pkl 0.32.1: valid configuration tests passed; invalid CPU allocation is rejected by the Python test suite.
- `ruff check .`: passed.

[portable-checks.json](evidence/portable-checks.json) preserves command results. The five retrieval questions are a small diagnostic suite, not a broad RAG quality benchmark. The default reviewer performs deterministic retrieval; no LLM is required for portable checks.

[Environment and OCI digests](evidence/environment.json) identify the tested dependencies and live image revisions. [GitHub Actions](https://github.com/sivalinb/incident-experiment-lab/actions) independently reports the current portable CI status. Ordinary Linux CI does not run Apple Container workloads.

## Real HTTP queue experiment

The lab created an HTTP broker and sink inside a Linux VM, returned HTTP 503 during a downstream outage, killed/restarted the broker process, and then drained its backlog.

| Queue policy | Accepted | Unique delivered | Lost | Duplicates observed |
|---|---:|---:|---:|---:|
| Volatile memory | 60 | 45 | 15 | 0 |
| SQLite WAL | 60 | 60 | 0 | 0 |

The delivered and lost IDs and timeline are in [live-recovery.json](evidence/live-recovery.json). This trial tests the checked-in Python queue implementation. It is not a test of OpenTelemetry Collector's persistent queue implementation. A process restart also does not establish durability through a VM power cut or storage corruption. Zero duplicates in one trial is not an exactly-once guarantee.

## Public arrival data

The separate deterministic simulation rescaled a public NAB NYC taxi time series into arrivals. One tested durable configuration accepted 145 records, rejected 22 when capacity was exhausted, and lost none of the accepted records. See [public-consumption.json](evidence/public-consumption.json). The live HTTP experiment uses its own fixed arrival schedule; do not label the simulation as a live taxi workload.

## Reproduce

Run `python scripts/run.py --live`. Use the interface to adjust capacity, drain rate, outage window, restart point, and durable/volatile policy for the simulation. Compare accepted/delivered/lost/rejected records before interpreting recovery ratios.

## Public source verification

All ten catalogue entries downloaded successfully during verification, including USGS, NAB CPU/taxi, GSM8K, OpenMetrics, OTel semantic conventions, Pkl/Container releases, Apple runtime resource documentation, and node_exporter documentation. [public-sources.json](evidence/public-sources.json) records retrieval times, byte counts, hashes, URLs, and upstream terms. Documentation and release metadata are reference material, not empirical workload measurements. Downloaded source contents remain untracked and are not relicensed by this repository.
