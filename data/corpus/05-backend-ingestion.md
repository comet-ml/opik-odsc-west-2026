# Backend ingestion

The Opik backend does not insert rows into ClickHouse one at a time. It relies on
ClickHouse's `async_insert` mechanism, where the server buffers incoming rows and writes
them out as larger parts. The buffer window is adaptive, bounded by a configurable minimum
and maximum busy timeout, and an insert is also forced once the buffered data reaches
`async_insert_max_data_size`. Opik's analytics connection sets `wait_for_async_insert = 1`,
which means an insert call returning successfully guarantees the rows are actually in the
table rather than merely queued in the buffer.
