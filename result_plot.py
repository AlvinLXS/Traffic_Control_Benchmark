#!/usr/bin/env python
# encoding: utf-8
"""
@author:  Howe Liu
@time:    2020.4.23
@file:    result_plot.py
"""

import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from xml.etree import ElementTree as et
from multiprocessing.pool import Pool  # 进程池
from multiprocessing import cpu_count

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--method_1', type=str, required=False,
                        default='webster',
                        help='The name of the method(1)')
    parser.add_argument('--tripinfo_dir_1', type=str, required=False,
                        default='./3X3grid_webster/output/3X3grid_tripinfo.xml',
                        help='The directory of the tripinfo file(1)')
    parser.add_argument('--method_2', type=str, required=False,
                        default='actuated',
                        help='The name of the method(2)')
    parser.add_argument('--tripinfo_dir_2', type=str, required=False,
                        default='./3X3grid_actuated/output/3X3grid_tripinfo.xml',
                        help='The directory of the tripinfo file(2)')
    args = parser.parse_args()
    return args

def parse_tripinfo(tripinfo_path):
    """解析tripinfo文件

    解析tripinfo.xml文件, 将信息转换为pd.DataFrame以便进一步处理

    Args:
        tripinfo_path: tripinfo.xml的路径

    Returns: tripinfo_df (pd.DataFrame): tripinfo的解析结果, 包含id,
    出发时间(depart), 到达时间(arrival)

    """
    tripinfo = et.ElementTree(file=str(tripinfo_path))
    ids, departs, arrivals,departDelay,duration,routeLength,waitingTime,stopTime,timeLoss =[], [], [], [], [], [], [], [], []
    for elem in tripinfo.iter(tag='tripinfo'):
        ids.append(float(elem.attrib['id']))
        departs.append(float(elem.attrib['depart']))
        arrivals.append(float(elem.attrib['arrival']))
        departDelay.append(float(elem.attrib['departDelay']))
        duration.append(float(elem.attrib['duration']))
        routeLength.append(float(elem.attrib['routeLength']))
        waitingTime.append(float(elem.attrib['waitingTime']))
        stopTime.append(float(elem.attrib['stopTime']))
        timeLoss.append(float(elem.attrib['timeLoss']))

    trip_df = pd.DataFrame(
        {'id': ids, 'depart': departs, 'arrival': arrivals,'departDelay':departDelay,'duration':duration,'routeLength':routeLength,
         'waitingTime':waitingTime,'stopTime':stopTime,'timeLoss':timeLoss}).astype(
        {'id': int, 'depart': int, 'arrival': int,'departDelay':float,'duration':int,'routeLength':float,
         'waitingTime':float,'stopTime':int,'timeLoss':float})
    trip_df['speed'] = trip_df['routeLength']/trip_df['duration']
    trip_df = trip_df.set_index('id').sort_index()
    print(f'parse tripinfo {tripinfo_path} finished')
    return trip_df

def get_speed(para):
    time_stamp = para[0]
    tripinfo_df = para[1]
    df_temp = tripinfo_df[(time_stamp >= tripinfo_df['depart']) & (time_stamp < tripinfo_df['arrival'])]
    return df_temp['speed'].mean()

def count_innet_vehs(tripinfo_df):
    """计算随时间变化的在网车辆数

    Args:
        tripinfo_df (pd.DataFrame): 解析tripinfo得到的pd.df

    Returns:
        innet_num (pd.Series): 按时间排列的在网车辆数

    """
    # Init run time df
    run_time = tripinfo_df['arrival'].max() + 1
    run_df = pd.DataFrame(
        {'time': range(run_time), 'depart': np.zeros(run_time),
         'arrival': np.zeros(run_time),'speed':np.zeros(run_time)})
    run_df = run_df.set_index('time')

    # Count depart/arrival numbers in tripinfo_df and assign them
    # to run_df
    depart_val = tripinfo_df['depart'].value_counts()
    run_df['depart'].loc[depart_val.index] = depart_val.values
    arrival_val = tripinfo_df['arrival'].value_counts()
    run_df['arrival'].loc[arrival_val.index] = arrival_val.values

    # Count numbers of car in traffic networkcumsum
    innet_num = run_df.cumsum()['depart'] - run_df.cumsum()['arrival']

    speed = []
    p = Pool(processes=cpu_count())
    res = p.map(get_speed,([(time_stamp,tripinfo_df) for time_stamp in range(run_time)]))
    p.close()
    p.join()
    for item in res:
        speed.append(item)
    run_df['speed'] = np.array(speed)
    run_df['speed'].fillna(method='ffill', inplace=True)
    # time_var指随时间变化的量，速度和在网车辆数
    time_var = pd.DataFrame({'time_range':range(run_time),'innet_num':innet_num,'speed':run_df['speed']})

    return time_var,tripinfo_df['waitingTime'].mean(),tripinfo_df['timeLoss'].mean(),tripinfo_df['stopTime'].mean()

def plot_result(args):
    tripinfo_df_1 = parse_tripinfo(args.tripinfo_dir_1)
    var_time_1, waitingTime_1, timeLoss_1, stopTime_1 = count_innet_vehs(tripinfo_df_1)
    tripinfo_df_2 = parse_tripinfo(args.tripinfo_dir_2)
    var_time_2, waitingTime_2, timeLoss_2, stopTime_2 = count_innet_vehs(tripinfo_df_2)

    mpl.rcParams["font.sans-serif"] = ["SimHei"]
    mpl.rcParams["axes.unicode_minus"] = False

    x = np.array([0, 0.3])
    y1 = [waitingTime_1, timeLoss_1]
    y2 = [waitingTime_2, timeLoss_2]

    bar_width = 0.1
    tick_label = ["waiting_time", "time_loss"]

    plt.bar(x, y1, bar_width, color="c", align="center", label=args.method_1, alpha=0.5)
    plt.bar(x + bar_width, y2, bar_width, color="b", align="center", label=args.method_2, alpha=0.5)

    plt.xlabel("Evaluation index")
    plt.ylabel("Value")

    plt.xticks(x + bar_width / 2, tick_label)

    plt.legend()

    plt.show()


if __name__ == '__main__':
    args = parse_args()
    plot_result(args)
