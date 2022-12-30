#!/usr/bin/python3
# The goal of this script is to search for patterns inside 
# log files for a given date range.
# TODO: find the regex for a newline (EOL)  

import os
import re
import mmap
from pathlib import Path
from config import Config
from util import validate_timestamp
from typing import List, AnyStr, Tuple
from datetime import datetime


# project path
project_path = Path(__file__).parent.parent

# determine path where log files are
if len(Config.LOG_FILE_PATH) > 0:
    log_file_path = Config.LOG_FILE_PATH
else:
    log_file_path = f"{project_path}/assets/logs"

# time gaps
time_gap_list = [
    ("2022-11-21T23:00:00", "2022-11-22T01:55:00"),
]



def search_all(time_gap_list: List) -> List:
    # Iterate list
    for gap in time_gap_list:
        print(f"{gap[0]} and {gap[1]}")
    regexp = f'2022-11-21T23:00.*'
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
    search_all(time_gap_list)


def is_valid_timestamp(input_string: AnyStr) -> bool:
    # regexp = r'[0-9]{1,4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}'
    regexp = r'((((19|20)([2468][048]|[13579][26]|0[48])|2000)-02-29|((19|20)[0-9]{2}-(0[4678]|1[02])-(0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}-(0[1359]|11)-(0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}-02-(0[1-9]|1[0-9]|2[0-8])))\s([01][0-9]|2[0-3]):([012345][0-9]):([012345][0-9]))'
    regexp = r'^((20[0-9]{2})-([0-1]\d).*)'

    regex = re.compile(regexp, re.MULTILINE)

    m = regex.findall(input_string)
    
    return m



def secs_between(start_ts_string: AnyStr, end_ts_string: AnyStr) -> int:
    a = datetime.strptime(start_ts_string, "%Y-%m-%dT%H:%M:%S")
    b = datetime.strptime(end_ts_string, "%Y-%m-%dT%H:%M:%S")
    return int((b-a).total_seconds())


def regex_time_range(start_ts_string: AnyStr, end_ts_string: AnyStr):
    # 2022-12-21T03:35:15 > 2022-12-21T23:37:21
    str_out = "("
    ds = start_ts_string[0:11:]
    de = end_ts_string[0:11:]
    _H = (int(start_ts_string[11::12]), int(end_ts_string[11::12]))
    _h = (int(start_ts_string[12::13]), int(end_ts_string[12::13]))
    _M = (int(start_ts_string[14::15]), int(end_ts_string[14::15]))
    _m = (int(start_ts_string[15::16]), int(end_ts_string[15::16]))
    _S = (int(start_ts_string[17::18]), int(end_ts_string[17::18]))
    _s = (int(start_ts_string[18::19]), int(end_ts_string[18::19]))

    total_secs = secs_between(start_ts_string, end_ts_string)
    sleft = total_secs

    stnj = 10 - _s[0]
    if stnj <= sleft:
        # example: 35:55 > 36:05 | 35:55 > 37:05 (70) | 35:15 > 36:01 (46)
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-9].*"
        sleft -= stnj # (41)
        stnj = 60 - ((_S[0]+1)*10)
        if sleft == 0:
            # example: 35:55 > 36:00
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*"
        elif sleft == stnj:
            # example: 35:25 > 36:00 (30, 30) | 35:45 > 36:00 (10, 10)
            str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-5][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*"
        elif sleft < stnj:
            # examples: 35:15 > 35:21 (1 < 40) | 35:15 > 35:31 (11 < 40) | 35:15 > 35:55 (35 < 40)
            if (_S[1] - (_S[0]+1)) == 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*"
            elif (_S[1] - (_S[0]+1)) == 1:
                str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}][0-9].*"
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
            else:
                str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-{_S[1]-1}][0-9].*"
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
        else: # sleft > stnj
            # examples: 
            # 35:55 > 37:05 (65)
            # 35:15 > 36:01 sleft = 1
            # 35:15 > 36:25 sleft = 25
            # 35:55 > 37:00 sleft = 60
            # 35:55 > 37:10 sleft = 70
            # 35:55 > 37:45 sleft = 105
            # 35:55 > 38:00 sleft = 120
            # 35:55 > 38:05 sleft = 125
            # 35:55 > 38:59 sleft = 179
            # 35:55 > 40:00 sleft = 360
            # 35:55 > 40:10 sleft = 370
            str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-5][0-9].*"

            sleft -= stnj
            stnj = (10 - (_m[0]+1)) * 60 # 4 * 60 = 360
            
            if sleft == 0:
                # example: 03:35:55 > 03:40:00
                ... # Is already handled!!
            elif sleft == stnj:
                # example: 35:55 > 40:00 sleft = 360
                str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]+1}-9]\:[0-5][0-9].*"
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][0].*"
            elif sleft < stnj:
                # example: 
                if (_S[1] - (_S[0]+1)) == 0:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*"
                elif (_S[1] - (_S[0]+1)) == 1:
                    ...
                    # str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}][0-9].*"
                    # str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
                else:
                    ...
                    # str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-{_S[1]-1}][0-9].*"
                    # str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    else:
        # OK!
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-{_s[1]}].*"


    str_out = f"{str_out})"
    return str_out

if __name__ == "__main__":


    # print(secs_between("2022-12-21T23:36:00","2022-12-21T23:36:05"))

    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:35:17"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:35:20"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:35:25"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:35:30"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:35:35"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:35:55"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:36:00")) # OK
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:36:01"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:36:10"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:36:11"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:36:41"))
    print("---")
    print(regex_time_range("2022-12-21T03:35:15", "2022-12-21T03:37:00"))

    # main()
    check_string = """2022-12-21T02:01:04.786976 [0]: jarry jarry
    2022-12-21T03:35:15.000000 [1]: appo
    2022-12-21T09:43:41.786976 [2]: jarry 
    2022-12-21T18:11:21.786976 [3]: jarry
    2022-12-21T20:33:44.786976 [4]: huh
    2022-12-21T23:36:04.786976 [5]: Sa
    2022-12-21T23:37:50.390976 [6]: nung
    2022-12-21T23:39:04.564029 [7]: song
    2022-12-22T00:01:04.123456 [8]: sam
    2022-12-31T23:18:22.123456 [9]: ha
    2023-01-01T00:01:04.123456 [10]: ni
    2023-01-01T18:01:04.123456 [11]: jarry jarry
    2023-01-01T23:58:04.123456 [12]: Dibla
    """

    # 2022-12-21T23:36:00 > 2022-12-21T23:36:05
    regex_str = (
        "(2022-12-21T[2][3]\:[3][6]\:[0][0-5].*)"
        )

    print(re.findall(regex_str, check_string))

    # 2022-12-21T03:35:15 > 2022-12-21T23:37:21
    regex_str = (
        "(2022-12-21T[0][3]\:[3][5]\:[1][5-9].*|"
        "2022-12-21T[0][3]\:[3][5]\:[2-5][0-9].*|"
        "2022-12-21T[0][3]\:[3][5-9]\:[0-5][0-9].*|"
        "2022-12-21T[0][3]\:[3-5][0-9]\:[0-5][0-9].*|"
        "2022-12-21T[0][3-9]\:[0-5][0-9]\:[0-5][0-9].*|"
        "2022-12-21T[1][0-9]\:[0-5][0-9]\:[0-5][0-9].*|"
        "2022-12-21T[2][0-2]\:[0-5][0-9]\:[0-5][0-9].*|"
        "2022-12-21T[2][3]\:[0-2][0-9]\:[0-5][0-9].*|"
        "2022-12-21T[2][3]\:[3][0-6]\:[0-5][0-9].*|"
        "2022-12-21T[2][3]\:[3][7]\:[0-1][0-9].*|"
        "2022-12-21T[2][3]\:[3][7]\:[2][0-1].*)"
        )

    print(re.findall(regex_str, check_string))

    # print("2022-12-21T03:35:15"[0:4:])  
    # print("2022-12-21T03:35:15"[5:7:])  
    # print("2022-12-21T03:35:15"[8:10:]) 
    # print("2022-12-21T03:35:15"[11:13:])
    # print("2022-12-21T03:35:15"[14:16:])
    # print("2022-12-21T03:35:15"[17:19:])
    




    
    # print(is_valid_timestamp(check_string))
    # print(is_valid_timestamp('2022-11-21 23:36:04'))
    # print(f"{is_valid_timestamp('abcdefkaboemdef')}")

    # file_path = "/home/user/projects/ol-analytical-research/assets/logs/2022-11-22-18_36"
    # parseFile(file_path)
