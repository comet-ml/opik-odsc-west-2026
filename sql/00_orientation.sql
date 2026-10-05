-- Find the ids everything else needs.
--
-- `projects` lives in MySQL, not ClickHouse: the analytics store holds only the
-- high-volume, append-heavy entities. So you resolve a project name to an id in the
-- app, and ClickHouse only ever sees the id. That split is deliberate — one store for
-- transactional state, one for analytics.

SELECT
    workspace_id,
    project_id,
    count()                     AS traces,
    min(start_time)::Date       AS oldest,
    max(start_time)::Date       AS newest,
    dateDiff('day', min(start_time), max(start_time)) AS days
FROM opik.traces
GROUP BY workspace_id, project_id
ORDER BY traces DESC;
