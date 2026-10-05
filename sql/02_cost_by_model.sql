-- Spend and token usage per model.
--
-- Cost lives on spans, never on traces: it belongs to the call that actually spent the
-- money. A trace's cost is the sum of its spans.
--
-- `usage` is a Map(String, Int32), so tokens are read by key rather than as columns —
-- providers disagree about which counters exist, and a map absorbs that without a
-- migration per provider.

SELECT
    provider,
    model,
    count()                                     AS calls,
    round(sum(total_estimated_cost), 4)         AS total_cost_usd,
    round(avg(total_estimated_cost), 8)         AS avg_cost_usd,
    sum(usage['prompt_tokens'])                 AS prompt_tokens,
    sum(usage['completion_tokens'])             AS completion_tokens,
    round(quantile(0.95)(duration))             AS p95_ms
FROM opik.spans
WHERE workspace_id = {workspace_id:String}
  AND project_id   = {project_id:String}
  AND type         = 'llm'
  AND model != ''
GROUP BY provider, model
ORDER BY total_cost_usd DESC;
