-- Latency percentiles per day.
--
-- Note the WHERE clause: workspace_id and project_id are the first two columns of the
-- ORDER BY, so this prunes by primary key instead of scanning the table. Every query in
-- this pack leads with them. Drop them and you are reading everything.
--
-- `duration` is stored, not computed at query time.
--
-- source = 'sdk' is what "production traffic" means here. Traces from experiments, the
-- playground and optimization runs share the table and would otherwise pollute the numbers.

SELECT
    toDate(start_time)                      AS day,
    count()                                 AS traces,
    round(quantile(0.50)(duration))         AS p50_ms,
    round(quantile(0.90)(duration))         AS p90_ms,
    round(quantile(0.95)(duration))         AS p95_ms,
    round(quantile(0.99)(duration))         AS p99_ms,
    round(max(duration))                    AS max_ms
FROM opik.traces
WHERE workspace_id = {workspace_id:String}
  AND project_id   = {project_id:String}
  AND source       = 'sdk'
  AND duration IS NOT NULL
GROUP BY day
ORDER BY day;
