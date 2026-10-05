-- How the data physically sits on disk.
--
-- The ReplacingMergeTree / FINAL semantics are covered in the talk, not here: whether you can
-- observe an unmerged duplicate depends on background merge scheduling, so it is not something
-- to demonstrate live. What IS stable is the physical layout, and that is what actually drives
-- the engineering decisions.

-- Parts are the unit merges work on. Part count is what background merges fight to keep down;
-- part size is what the merge ceiling is measured against. When individual parts grow past that
-- ceiling, merges stop keeping up — which is the pressure that makes partitioning necessary.
SELECT
    table,
    count()                                          AS active_parts,
    sum(rows)                                        AS rows,
    formatReadableSize(sum(bytes_on_disk))           AS on_disk,
    formatReadableSize(max(bytes_on_disk))           AS largest_part,
    formatReadableSize(sum(data_uncompressed_bytes)) AS uncompressed,
    round(sum(data_uncompressed_bytes) / sum(data_compressed_bytes), 1) AS compression_ratio
FROM system.parts
WHERE database = 'opik' AND table IN ('traces', 'spans') AND active
GROUP BY table
ORDER BY sum(bytes_on_disk) DESC;

-- Where the bytes actually are, column by column.
--
-- Two things show up here.
--
-- First, compression is per column and varies enormously with what the column holds. `name`
-- compresses ~9x because it repeats across every trace; `id` barely compresses at all. It is a
-- UUIDv7: a timestamp prefix keeps ids sortable by time, and the remaining bits are random, so
-- there is little to compress. In this dataset `id` is the single largest column on disk.
--
-- Second, a caveat worth stating out loud: this seeded data has tiny input/output payloads. In
-- production those columns dominate the table instead, by a wide margin. That is precisely why
-- the schema carries `truncated_input` / `truncated_output` and `input_slim` / `output_slim` —
-- so the common read paths never touch the full payload.
--
-- Which is the argument for a column store. An analytical question about latency or cost reads
-- timestamps, ids and numbers, and never pays for the payload columns sitting beside them. In a
-- row store the payload comes along whether you asked for it or not.
SELECT
    column,
    type,
    formatReadableSize(sum(column_data_compressed_bytes))      AS compressed,
    formatReadableSize(sum(column_data_uncompressed_bytes))    AS uncompressed,
    round(100.0 * sum(column_data_compressed_bytes) / sum(sum(column_data_compressed_bytes)) OVER (), 1) AS pct_of_table
FROM system.parts_columns
WHERE database = 'opik' AND table = 'spans' AND active
GROUP BY column, type
ORDER BY sum(column_data_compressed_bytes) DESC
LIMIT 12;
