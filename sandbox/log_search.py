#!/usr/bin/python3
# The goal of this script is to search for patterns inside 
# log files for a given date range.
# TODO: find the regex for a newline (EOL)  

import os
import re
import mmap
from pathlib import Path
from config import Config

# project path
project_path = Path(__file__).parent.parent

# determine path where log files are
if len(Config.LOG_FILE_PATH) > 0:
    log_file_path = Config.LOG_FILE_PATH
else:
    log_file_path = f"{project_path}/assets/logs"


def search_all(ts_from = None, ts_to = None):
    regexp = f'2022-11-21T20:25:5{"*"}'
    inputFile = f"{log_file_path}/2022-11-22-04_39"

    try:
        with open(inputFile, 'r') as file:
            contents = file.read()
            # Search the first matching date existing in dateList
            if re.search(regexp, contents):
                print(re.findall(regexp, contents))
    except Exception as e:
        print(e)


def search_all_bin():
    f = open("data.log", "r")
    mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
    re.search(b"test", mm)




def main():
    print(log_file_path)
    search_all()


if __name__ == "__main__":
    main()
