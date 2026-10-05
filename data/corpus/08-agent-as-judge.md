# Agent as a Judge

Instead of mapping each prompt variable to a specific trace field, a rule can include
`{{trace}}` in its prompt. The judge then reads the trace itself using tools: `read` to read
the trace or a span, `jq` to pull out a path, `search` to find text anywhere in the trace,
`get_trace_spans` to list spans, and `get_attachment` to fetch an attached file. Because the
judge decides what to read, the same rule works whatever shape your traces have, with no
variable mapping to fill in.

Cost is bounded two ways: Opik truncates the trace it puts in the prompt and points the judge
at targeted reads, and you can set a hard "Max cost per evaluation (USD)" after which the
judge wraps up and returns what it has. Agent as a Judge requires a model that supports tool
calling; on a model that does not, the rule falls back to a single call with a truncated trace.
