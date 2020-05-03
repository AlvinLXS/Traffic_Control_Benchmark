# Traffic_Control_Benchmark
Benchmark for traffic control algorithms

## Implement the baseline method in SUMO
1. To implement **fix** method in SUMO, run
```
python baseline_result.py --sumo_cfg [sumocfg_dir] fix --green-time [green_time]
```
`[sumocfg_dir]` is the directory of SUMO config file.

`[green_time]` is the duration of the green light of each traffic light.

2. To implement **webster** method in SUMO, run
```
python baseline_result.py --sumo_cfg [sumocfg_dir] webster
```
`[sumocfg_dir]` is the directory of SUMO config file.

3. To implement **actuated** method in SUMO, run
```
python baseline_result.py --sumo_cfg [sumocfg_dir] actuated --minDur [minDur] --maxDur [maxDur]
```
`[sumocfg_dir]` is the directory of SUMO config file.

`[minDur]` is the minimum duration of green light for each phase of each traffic light.

`[maxDur]` is the maximum duration of green light for each phase of each traffic light.

## Parse the tripinfo file and plot the result
To parse the tripinfo file and plot the result, run
```
python result_plot.py --method_1 [name_of_method_1] --tripinfo_dir_1 [tripinfo_dir_1] --method_2 [name_of_method_2] --tripinfo_dir_2 [tripinfo_dir_2]
```
`[name_of_method_1]` and `[name_of_method_1]` are the names of method 1 and method 2 respectively.

`[tripinfo_dir_1]` and `[tripinfo_dir_2]` are the directories of the tripinfo file of method 1 and method 2 respectively.

Below is an example:

![](./result_plot.png)
