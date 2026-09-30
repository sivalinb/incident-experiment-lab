# Architecture

## Data flow

Pkl failure timeline → validated experiment → deterministic simulator or real HTTP broker/sink → downstream outage → broker process crash/restart → drain → accepted/delivered/rejected/duplicate accounting.

## Implementation decisions

The simulator is a discrete-step queue model with a bounded queue, controlled draining, an outage interval, and a crash event. It preserves accepted-event identities and drains after production stops. The live worker is an independent standard-library HTTP workload. The durable broker commits each accepted event to SQLite before acknowledging; a drain thread sends records to the sink and removes acknowledged rows. Killing the broker tests persistence of accepted records. A crash between sink acceptance and queue deletion may duplicate delivery, so duplicates are explicitly reported. The live chart's accepted-minus-delivered value includes lost records and is labeled accordingly.

## Modules

`app.py` renders Streamlit controls and stores the current report in session state. `engine.py` contains domain logic and typed runtime models. `config/` stores Pkl source and its verified export. `labcore/runtime.py` issues argument-array subprocess calls, captures bounded output, and scopes cleanup to generated job names. `labcore/observability.py` writes event metadata and experiment reports. `labcore/ai.py` retrieves reference evidence and optionally synthesizes a cited answer. `data/sources.json` declares the public inputs and their terms. `workloads/` contains trusted workload entrypoints, where needed. `tests/` covers failure cases and Streamlit workflows.

## Trust boundaries

UI uploads and downloaded source content are data. They do not become system commands or Pkl modules. The sandbox project explicitly permits user Python inside a VM. Other tools execute only checked-in workload entrypoints. Subprocess calls use argument lists without a shell. Source URLs come from a fixed HTTPS catalogue with redirects disabled. Model responses are advisory and cannot trigger container actions.

## Persistence and reproducibility

Run artifacts are local and ignored by Git. Reports retain the mode, input/contract settings, source/config hashes where applicable, raw observations, and calculated decisions. Reproduce a finding by saving the report, pinning runtime/image/model versions, rerunning with the same workload, and comparing independent trials. Generated configuration and dependency versions are committed. For formal benchmarks replace mutable image tags with verified OCI digests.
