# Security and limitations

Simulation timing uses ticks; live timing uses monotonic seconds. Public NAB data only shapes a workload and does not provide ground truth for the injected incident. The live HTTP broker and sink run in one VM with a real child-process crash; this does not test a physical host failure or a full VM power loss. OpenTelemetry instrumentation measures orchestration and exports traces optionally. The existing Collector-focused lab can be extended using this experiment schema, but no unimplemented Collector experiment is claimed here.

## Shared boundaries

The app is intended for a trusted local user. It has no multi-user authentication or tenant isolation at the Streamlit layer. Public deployment requires a separate access-control and execution-service design. The Pkl evaluator only loads the repository's trusted module. Public sources are allowlisted and not executed. Input sizes, resource settings, subprocess output, and execution durations are bounded where implemented. The detailed report distinguishes active enforcement from documentation and experimental assumptions.

Source and model content may include misleading instructions; retrieval and model outputs have no authority to change application policy. Citation membership alone does not prove correctness. Never publish private production logs or credentials as example data. Report suspected security defects privately through the repository owner's GitHub contact channels; do not include working credentials in an issue.
