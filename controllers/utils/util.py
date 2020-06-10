from __future__ import print_function

import os.path as osp
from six.moves import urllib
import os
import os.path as osp
import errno
import requests
from pathlib import Path
import yaml

basepath = Path(__file__).parents[1]


def makedirs(path):
    try:
        os.makedirs(osp.expanduser(osp.normpath(path)))
    except OSError as e:
        if e.errno != errno.EEXIST and osp.isdir(path):
            raise e


def download_url(url, folder, log=True):
    r"""Downloads the content of an URL to a specific folder.
    """
    filename = url.split('/')[-1]
    filepath = Path(folder, filename)

    if log:
        print('Downloading', url)
    with open(filepath, 'wb') as f:
        r = requests.get(url)
        f.write(r.content)
    return filepath


def plot_map(net_file, net_name):
    import subprocess
    import os
    import sys

    print(f'Plot {net_name}')

    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare the environment variable 'SUMO_HOME'")

    plot_file = basepath / 'utils' / 'plot_net_trafficLights.py'
    out_file = basepath / 'images' / f'{net_name}.png'

    if net_name == 'monaco':
        xylim = '--xlim 1000,10000 --ylim 0,6000 '
    elif net_name == 'luxembourg':
        xylim = '--xlim 1000,13000 --ylim 0,11500 '
    else:
        xylim = ''

    subprocess.call('python '
                    f'{plot_file} -n {net_file} '                    
                    '--edge-width .5 '
                    f'{xylim} '
                    '--xlabel [m] --ylabel [m] '
                    '--width 3 '
                    '--blind '
                    f'--output {out_file}',
                    shell=True)


if __name__ == '__main__':
    net_names = ['monaco', 'luxembourg']

    with open(Path(basepath, 'datasets', 'params.yaml'), "r") as f:
        config_dict = yaml.load(f)

    for net in net_names:
        net_file_path = config_dict[net]['netfile']
        filename = config_dict[net]['filename']
        net_file_path = Path(basepath, 'datasets', net, filename, net_file_path)
        plot_map(net_file_path, net)
