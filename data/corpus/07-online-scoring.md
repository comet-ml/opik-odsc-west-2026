# Online scoring rules

An online scoring rule runs an LLM-as-a-judge against production traces as they arrive and
writes the verdict back onto the trace as a feedback score. Rules are defined in the UI or
through the REST API. Opik ships three built-in LLM-as-a-judge metrics for trace rules:
Hallucination, Moderation and Answer Relevance. You can also write your own prompt, using
mustache-style `{{variable_name}}` placeholders, and define the scores it returns.

Every rule has a sampling rate: the percentage of production traces that get scored. At
100% every production trace is scored. Lower rates exist because each evaluation is itself
a model call and therefore a real cost.
