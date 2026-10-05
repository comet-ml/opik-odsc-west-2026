-- Error rate over time.
--
-- `error_info` is a JSON string, empty when the trace succeeded. Storing it as a string
-- rather than parsed columns keeps ingestion cheap; you pay the parsing cost only in the
-- rare queries that need the contents, as the second query below does.

SELECT
    toDate(start_time)                                  AS day,
    count()                                             AS traces,
    countIf(error_info != '')                           AS errors,
    round(100.0 * countIf(error_info != '') / count(), 2) AS error_pct
FROM opik.traces
WHERE workspace_id = {workspace_id:String}
  AND project_id   = {project_id:String}
  AND source       = 'sdk'
GROUP BY day
ORDER BY day;

-- Which errors, and what they cost you in wasted latency.
SELECT
    JSONExtractString(error_info, 'exception_type')  AS exception,
    count()                                          AS occurrences,
    round(avg(duration))                             AS avg_ms_before_failing
FROM opik.traces
WHERE workspace_id = {workspace_id:String}
  AND project_id   = {project_id:String}
  AND error_info != ''
GROUP BY exception
ORDER BY occurrences DESC;
