from pathlib import Path
from utils.util import download_url
import subprocess
import argparse
import yaml
from multiprocessing.pool import Pool
import os
import tarfile

basepath = Path(__file__).parents[1]


def build_nets(url, folder, filename):
    if Path(folder, filename).exists():
        print("Using exist file", filename)
    else:
        filepath = download_url(url, folder)
        tar = tarfile.open(filepath)
        tar.extractall(path=folder)
        tarname = tar.getnames()[0]
        ori_name = str(Path(folder, tarname))
        new_name = str(Path(folder, filename))
        tar.close()
        os.rename(ori_name, new_name)
        os.remove(filepath)

    print(f"Finish building nets {filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--netname', nargs='+', type=str, required=True,
                        default="", help="Net files to build")

    args = parser.parse_args()
    netname = args.netname

    with open(Path(basepath, 'datasets', 'params.yaml'), "r") as f:
        config_dict = yaml.load(f)

    urls = list()
    output_folders = list()
    file_names = list()
    for net in netname:
        net = net.lower()
        urls.append(config_dict[net]['url'])
        file_name = config_dict[net]['filename']
        file_names.append(file_name)
        output_folders.append(str(Path(basepath, 'datasets', net)))

    with Pool() as p:
        p.starmap(build_nets, zip(urls, output_folders, file_names))
