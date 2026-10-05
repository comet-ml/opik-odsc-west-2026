# How the SDK sends data

The Python SDK does not send one HTTP request per span. Messages accumulate in a background
batcher and are flushed either when the batch fills or when a timer expires. Span and trace
creation batches hold at most 1000 messages and flush every 2.0 seconds. A batch is also
split early if it would exceed a 50 MB memory limit. Because sending is asynchronous, a
short-lived script should call `opik.flush_tracker()` before exiting so buffered messages
are not lost.
