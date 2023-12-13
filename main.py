import argparse
import os
import logging
from pathlib import Path
import shutil
import time

def define_argument_parser():
    """
    Define the argument parser for the command line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(
        description='Synchronize two directories.',
        usage='python interview.py [SOURCE_FOLDER] [REPLICA_FOLDER] [INTERVAL_TIME] [LOG_FILE]',
    )

    parser.add_argument(
        'source_folder_path',
        type=str,
        help='Path to the source folder',
        nargs=1,
        metavar='SOURCE_FOLDER',
    )

    parser.add_argument(
        'replica_folder_path',
        type=str,
        help='Path to the replica folder',
        nargs=1,
        metavar='REPLICA_FOLDER',
    )

    parser.add_argument(
        '-d', '--days',
        action='store_true',
        help='Specify if the interval is in days',
    )

    parser.add_argument(
        '-m', '--minutes',
        action='store_true',
        help='Specify if the interval is in minutes',
    )

    parser.add_argument(
        'interval',
        type=int,
        help='Interval time to check for changes',
        nargs=1,
        metavar='INTERVAL_TIME',
    )

    parser.add_argument(
        'log_file_path',
        type=str,
        help='Path to the log file',
        nargs=1,
        metavar='LOG_FILE',
    )

    return parser.parse_args()


def create_loggers(logger_path: str):
    """
    Creates a logger object and adds a file handler to it.

    Parameters:
        logger_path (str): The path to the log file.
    Returns:
        The logger object.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
    )

    logger = logging.getLogger(__name__)

    handler = logging.FileHandler(logger_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

def check_folders_existence(source_folder_path: Path, replica_folder_path: Path, logger: logging.Logger):
    """
    Check if source and replica folders exist.

    Parameters:
        source_folder_path (Path): Path to the source folder .
        replica_folder_path (Path): Path to the replica folder.
    Returns:
        A tuple containing a boolean indicating whether both folders exist and a string describing the result.
    """
    source_exists = source_folder_path.exists()
    replica_exists = replica_folder_path.exists()

    if source_exists and replica_exists:
        return True
    elif source_exists:
        logger.error(f"Replica folder {replica_folder_path} does not exist")
        return False
    else:
        logger.error(f"Source folder {source_folder_path} does not exist")
        return False

def write_stats_to_logging_file(changes_stats: dict, logger: logging.Logger):
    """
    Writes the statistics of changes to a logging file.

    Parameters:
        changes_stats (dict): A dictionary containing the statistics of changes.
        logger (logging.Logger): The logger object to write the statistics to.
    Returns:
    """
    s = "; ".join([f'{key} = {value}' for key, value in changes_stats.items()])
    logger.info(f'{s}\n')
    for key, value in changes_stats.items():
        changes_stats[key] = 0

def synchronize_folders(source_folder_path: str, replica_folder_path: str, changes_stats: dict, logger: logging.Logger):
    """
    Synchronizes two folders by copying files from the source folder to the replica folder and deleting files from the replica folder that do not exist in the source folder.

    Parameters:
    - source_folder_path (str): The path of the source folder.
    - replica_folder_path (str): The path of the replica folder.
    - changes_stats (dict): A dictionary to keep track of the changes made during synchronization.
    - logger (logging.Logger): The logger object used for logging synchronization events.
    """
    for source_file in source_folder_path.rglob('*'):
        replica_source_file = replica_folder_path.joinpath(source_file.relative_to(source_folder_path))
        if source_file.is_file():
            try:
                if not replica_source_file.exists():
                    shutil.copy2(source_file, replica_source_file)
                    logger.info(f'Created and copied {source_file} to {replica_source_file}')
                    changes_stats["Files created"] += 1
                elif source_file.stat().st_size != replica_source_file.stat().st_size or source_file.stat().st_mtime > replica_source_file.stat().st_mtime:
                    shutil.copy2(source_file, replica_source_file)
                    logger.info(f'Copied {source_file} to {replica_source_file}')
                    changes_stats["Files changed/copied"] += 1
            except:
                logger.error(f'Failed to copy {source_file} to {replica_source_file}')
        elif source_file.is_dir():
            try:
                if not replica_source_file.exists():
                    replica_source_file.mkdir(parents=True)
                    logger.info(f'Created new directory: {source_file} in {replica_source_file}')
                    changes_stats["Directories created"] += 1
            except:
                logger.error(f'Failed to create new directory: {source_file} in {replica_source_file}')

    for replica_file in replica_folder_path.rglob('*'):
        source_replica_file = source_folder_path.joinpath(replica_file.relative_to(replica_folder_path))

        if replica_file.is_file() and not source_replica_file.exists():
            try:
                replica_file.unlink()
                logger.info(f'Deleted file: {replica_file}')
                changes_stats["Files deleted"] += 1
            except:
                logger.error(f'Failed to delete file: {replica_file}')
        elif replica_file.is_dir() and not source_replica_file.exists():
            try:
                shutil.rmtree(replica_file)
                logger.info(f'Deleted directory: {replica_file}')
                changes_stats["Directories deleted"] += 1
            except:
                logger.error(f'Failed to delete directory: {replica_file}')


def main():

    args = define_argument_parser()

    source_folder_path = Path(args.source_folder_path[0]).resolve()
    replica_folder_path = Path(args.replica_folder_path[0]).resolve()
    if args.days:
        interval = args.interval[0] * 24 * 60 * 60
    else:
        # assuming minutes as default
        interval = args.interval[0] * 60

    log_file_path = args.log_file_path[0]

    changes_stats = {
        "Files created": 0,
        "Files changed/copied": 0,
        "Directories created": 0,
        "Files deleted": 0,
        "Directories deleted": 0,
    }

    logger = create_loggers(log_file_path)

    exist = check_folders_existence(source_folder_path,replica_folder_path, logger)

    if exist:
        while True:
            synchronize_folders(source_folder_path, replica_folder_path, changes_stats, logger)
            write_stats_to_logging_file(changes_stats, logger)
            time.sleep(interval)

if __name__ == '__main__':
    main()