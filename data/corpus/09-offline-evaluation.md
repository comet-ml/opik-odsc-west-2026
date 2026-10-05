# Offline evaluation

Offline evaluation runs a task over a fixed dataset and scores the results, producing an
experiment you can compare against previous runs. The `evaluate()` function takes a dataset,
a task callable, and a list of scoring metrics. The task receives a dict with the dataset
item's content and returns a dict that the metrics then score. Useful arguments include
`nb_samples` to run on a subset, `task_threads` to control concurrency, and
`scoring_key_mapping` when the task's output keys do not match what a metric expects.
