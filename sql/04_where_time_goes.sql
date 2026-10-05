-- Module 2's lesson, asked of the whole project at once.
--
-- In the notebook we read one trace's span tree and found the reranker costing ~690 ms that
-- end-to-end timing could not see. Here we ask which step owns the latency, and which owns
-- the spend, across every trace.

-- Per-step distribution. Percentiles are per name, so nesting does not distort them.
SELECT
    name                                    AS step,
    type,
    count()                                 AS calls,
    round(quantile(0.50)(duration), 2)      AS p50_ms,
    round(quantile(0.95)(duration), 2)      AS p95_ms,
    round(sum(total_estimated_cost), 4)     AS cost_usd
FROM opik.spans
WHERE workspace_id = {workspace_id:String}
  AND project_id   = {project_id:String}
  AND duration IS NOT NULL
GROUP BY step, type
ORDER BY p50_ms DESC;

-- Share of total time, counting leaf spans only.
--
-- A span tree double-counts if you sum it naively: `generate_answer` wraps
-- `chat_completion_create` and both carry ~the same duration. Only leaves represent time
-- actually spent, so attribution has to exclude any span that is some other span's parent.
--
-- The tree is stored flat — parentage is just a column — so "find the leaves" is an
-- anti-join against the same table rather than a recursive walk.
SELECT
    name                                            AS leaf_step,
    count()                                         AS calls,
    round(sum(duration) / 1000, 1)                  AS total_seconds,
    round(100.0 * sum(duration) / sum(sum(duration)) OVER (), 2) AS pct_of_time
FROM opik.spans
WHERE workspace_id = {workspace_id:String}
  AND project_id   = {project_id:String}
  AND duration IS NOT NULL
  AND id NOT IN (
      SELECT DISTINCT parent_span_id
      FROM opik.spans
      WHERE workspace_id = {workspace_id:String}
        AND project_id   = {project_id:String}
        AND parent_span_id != ''
  )
GROUP BY leaf_step
ORDER BY total_seconds DESC;
