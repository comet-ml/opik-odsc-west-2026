# The ClickHouse schema

Traces and spans are stored in ClickHouse using the `ReplacingMergeTree` engine, versioned
by the `last_updated_at` column. Replacing semantics matter because a trace is written more
than once: it is created when execution starts and updated when it ends. The `traces` table
is ordered by `(workspace_id, project_id, id)`. That ordering is the whole performance story
for the common access pattern, which is always scoped to one workspace and one project.
Deduplication happens at merge time, so a query that must not see duplicates uses `FINAL`,
which costs more than a plain scan.
