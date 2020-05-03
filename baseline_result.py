#!/usr/bin/env python
# encoding: utf-8
"""
@author:  Howe Liu
@time:    2020.4.22
@file:    baseline_result.py
"""

import argparse
import xml.etree.ElementTree as ET
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sumo_cfg', type=str, required=False, default='./3X3grid/3X3grid.sumocfg', help='The directory of the sumocfg file')
    subparsers = parser.add_subparsers(dest='method', help='The method to be tested: fix, webster, or actuated')

    sp = subparsers.add_parser('fix', help='Method: fix')
    sp.add_argument('--green-time', type=str, required=False, default='30', help='The duration of green')

    sp = subparsers.add_parser('webster', help='Method: webster')

    sp = subparsers.add_parser('actuated', help='Method: actuated')
    sp.add_argument('--minDur', type=str, required=False, default='5', help='The minimum duration of green')
    sp.add_argument('--maxDur', type=str, required=False, default='60', help='The maximum duration of green')

    args = parser.parse_args()
    if not args.method:
        parser.print_help()
        exit(1)
    return args

def fix(args):
    print('Method: fix')

    sumo_cfg = args.sumo_cfg
    green_time = args.green_time

    print('The duration of green: %s' % green_time)

    tree_cfg = ET.ElementTree(file=sumo_cfg)
    config_cfg = tree_cfg.getroot()
    net_dir = ''
    find_all = lambda data, s: [r for r in range(len(data)) if data[r] == s]
    for n in config_cfg.iter('net-file'):
        net_dir = sumo_cfg[0:find_all(sumo_cfg, '/')[-1] + 1] + n.attrib['value']

    tree = ET.ElementTree(file=net_dir)
    config = tree.getroot()
    for n in config.iter('phase'):
        if not 'y' in n.attrib['state']:
            n.attrib['duration'] = green_time
    tree.write(net_dir, encoding='utf-8', xml_declaration=True)

    os.system('sumo %s' % sumo_cfg)
    print('Finished!')

def webster(args):
    print('Method: webster')

    sumo_cfg = args.sumo_cfg
    tree = ET.ElementTree(file=sumo_cfg)
    config = tree.getroot()

    net_dir = ''
    rou_dir = ''
    find_all = lambda data, s: [r for r in range(len(data)) if data[r] == s]
    for n in config.iter('net-file'):
        net_dir = sumo_cfg[0:find_all(sumo_cfg, '/')[-1] + 1] + n.attrib['value']
    for n in config.iter('route-files'):
        rou_dir = sumo_cfg[0:find_all(sumo_cfg, '/')[-1] + 1] + n.attrib['value']
    out_dir = sumo_cfg[0:find_all(sumo_cfg, '/')[-1] + 1] + 'newTLS.add.xml'

    for n in config.iter('input'):
        add = ET.Element('additional-files', {'value': 'newTLS.add.xml'})
        n.append(add)
    tree.write(sumo_cfg, encoding='utf-8', xml_declaration=True)

    os.system('python tlsCycleAdaptation.py -n %s -r %s -o %s' % (net_dir, rou_dir, out_dir))
    os.system('sumo %s' % sumo_cfg)
    print('Finished!')

def actuated(args):
    print('Method: actuated')

    sumo_cfg = args.sumo_cfg
    minDur = args.minDur
    maxDur = args.maxDur

    print('The minimum duration of green: %s' % minDur)
    print('The maximum duration of green: %s' % maxDur)

    tree_cfg = ET.ElementTree(file=sumo_cfg)
    config_cfg = tree_cfg.getroot()
    net_dir = ''
    find_all = lambda data, s: [r for r in range(len(data)) if data[r] == s]
    for n in config_cfg.iter('net-file'):
        net_dir = sumo_cfg[0:find_all(sumo_cfg, '/')[-1] + 1] + n.attrib['value']

    tree = ET.ElementTree(file=net_dir)
    config = tree.getroot()
    for n in config.iter('tlLogic'):
        n.attrib['type'] = 'actuated'
        add = ET.Element('param', {'key': 'max-gap', 'value': '3.0'})
        n.append(add)
        add = ET.Element('param', {'key': 'detector-gap', 'value': '2.0'})
        n.append(add)
        add = ET.Element('param', {'key': 'show-detectors', 'value': 'false'})
        n.append(add)
        add = ET.Element('param', {'key': 'file', 'value': 'NULL'})
        n.append(add)
        add = ET.Element('param', {'key': 'freq', 'value': '300'})
        n.append(add)
    for n in config.iter('phase'):
        if not 'y' in n.attrib['state']:
            n.set('minDur', minDur)
            n.set('maxDur', maxDur)
    tree.write(net_dir, encoding='utf-8', xml_declaration=True)

    os.system('sumo %s' % sumo_cfg)
    print('Finished!')

if __name__ == '__main__':
    args = parse_args()
    if args.method == 'fix':
        fix(args)
    elif args.method == 'webster':
        webster(args)
    elif args.method == 'actuated':
        actuated(args)
    else:
        print("The method of baseline doesn't exist.")
