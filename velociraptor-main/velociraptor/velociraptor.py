import argparse
from pathlib import Path
from velociraptor.types.util import resolve_path
from velociraptor.types.config_manager import ConfigManager

def main(description: str):
    config_file = 'config.json'
    config_dir = 'config/'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-c", "--config_file", nargs=1, help="file name for the config input file")
    parser.add_argument("-d", "--config_dir", nargs=1, help="directory for the config input file")
    args = parser.parse_args()

    if args is not None:
        if args.config_file is not None:
            config_file = args.config_file[0]
        if args.config_dir is not None:
            config_dir = args.config_dir[0]

    base_directory_path = Path(__file__).parents[1].absolute()
    config_dir = resolve_path(base_directory_path, config_dir)
    return ConfigManager(base_directory_path, Path(config_dir) / config_file)
