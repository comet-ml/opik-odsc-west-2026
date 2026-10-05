# Scopes an online rule can target

Online evaluation rules are not limited to whole traces. A rule can target a trace, a single
span, or a conversation thread, and each scope supports both an LLM-as-a-judge evaluator and
a user-defined Python metric. Thread rules always read the conversation through a `{{context}}`
variable and have no mapping to configure.

Sampling applies to production data logged through the SDK. Traces produced by experiments are
always scored when the rule matches, and thread and span rules never run on experiment,
playground or optimization data at all.
