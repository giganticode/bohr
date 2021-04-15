Ideally, the added heurstics improve the metrics on all test datasets, which can be seen in the comment by the Github bot to the submitted PR. 
In this case the PR can be merged, and the set of heuristics will be updated 🎉

However, metrics might not improve or become worse on some (or even all) test datasets despite heursistics being reasonable. 
We suggest to follow the next steps to debug the heuristics.

1. If the metrics haven't changed, make sure that BOHR 'saw' the added heuristic(s). 
Check that `metrics/<task_name>/analysis_<dataset_name>.json` file has changed for any dataset and now has entries for the newly added heurstic(s).

1. BOHR 'saw' the heuristic but it doesn't cover enough datapoints to have a significant impact on the metrics. 
See how the coverage has increased for different datasets by checking the following file:
`metrics/<task_name>/<corresponding-heuristic-group>/heuristic_metrics_<dataset_name>.json`. 
If you see that the coverage value is less than expected, there might be a bug in your heuristic. Note! Some heuristics can be designed to have zero coverage on the test set(s). However, adding such heuristics can still lead to the increase of performance by improving the weights of those heuristics that are fired on the test set(s).

1. Check also `metrics/<task_name>/analysis_<dataset_names>.json` for suspicious values of 'Polarity', 'Coverage', 'Conflicts', 'Correct', 'Icorrent', 'Emp. Accuracy' values (TODO: elaborate more)

1. Have all the metrics on all the test datasets got worse or are there some that have improved? TODO how do we handle this case?

1. If there seems to be no bug in your heuristic and all the metrics consistently got worse, use *BOHR debugging suite* to inspect individual data points:

```shell
git checkout new-heuristic-branch
dvc pull
dvc checkout
bohr debug <task-name> <dataset-name> 
```

This will show you the datapoints whose probabilistic label had been changed the most. The example output of the command:

![image](https://user-images.githubusercontent.com/2955794/114852200-d95f4000-9de2-11eb-9476-2dd23ac09bc9.png)

To see a single datapoint in detail and how each fired heuristic contributed to its label, run the following command:

```shell
bohr debug <task-name> <dataset-name> <datapoint-id>
```

![image](https://user-images.githubusercontent.com/2955794/114852453-14fa0a00-9de3-11eb-8d90-858bf625060b.png)



