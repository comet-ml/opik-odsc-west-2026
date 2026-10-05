# The @track decorator

Wrapping a Python function with `@track` logs every call to Opik. Nested calls to other
tracked functions automatically become nested spans, so a single entry point produces a
whole trace tree rather than one flat record. The decorator captures the function's inputs
and outputs by default. You can disable that with `capture_input=False` or
`capture_output=False`, exclude specific arguments with `ignore_arguments`, and attach
`tags` and `metadata`.
