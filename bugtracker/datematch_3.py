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
from datetime import datetime, timedelta

# time gaps
time_gap_list = [
    ("2022-11-21T23:00:00", "2022-11-22T01:55:00"),
]


def secs_between(start_ts_string: AnyStr, end_ts_string: AnyStr) -> int:
    a = datetime.strptime(start_ts_string, "%Y-%m-%dT%H:%M:%S")
    b = datetime.strptime(end_ts_string, "%Y-%m-%dT%H:%M:%S")
    return int((b-a).total_seconds())


def print_range(regex, start, end="", seconds_from_start=None, seconds_rest=None):
    print(f"{regex}")
    if seconds_from_start and seconds_rest:
        new_start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=seconds_from_start)
        new_end = new_start + timedelta(seconds=seconds_rest)
        start = datetime.strftime(new_start, "%Y-%m-%dT%H:%M:%S")
        end = datetime.strftime(new_end, "%Y-%m-%dT%H:%M:%S")
    print(f"Partial regex for: {start} > {end}")


def regex_time_range(start_ts_string: AnyStr, end_ts_string: AnyStr):
    # 2022-01-01T03:35:15 > 2022-01-01T23:37:21
    str_out = "("
    ds = start_ts_string[0:11:]
    de = end_ts_string[0:11:]
    _H = (int(start_ts_string[11::12]), int(end_ts_string[11::12]))
    _h = (int(start_ts_string[12::13]), int(end_ts_string[12::13]))
    _M = (int(start_ts_string[14::15]), int(end_ts_string[14::15]))
    _m = (int(start_ts_string[15::16]), int(end_ts_string[15::16]))
    _S = (int(start_ts_string[17::18]), int(end_ts_string[17::18]))
    _s = (int(start_ts_string[18::19]), int(end_ts_string[18::19]))

    _total_diff_sec = secs_between(start_ts_string, end_ts_string)
    seconds_discounter = _total_diff_sec
    next_jump = (10 - _s[0]) # (0-9)

    # Screw otpimization, stick to the easiest way out, which is a layered hamburger regex 

    # 00:01 - 00:07     next_jump = 9  | seconds_discounter = 6  (next_jump > seconds_discounter)
    # 00:05 - 00:10     next_jump = 5  | seconds_discounter = 5  (next_jump = seconds_discounter)
    # 00:00 - 00:11     next_jump = 10 | seconds_discounter = 11 (next_jump < seconds_discounter)
    
    # Opening regex:
    if next_jump > seconds_discounter:
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string)
        return str_out
    elif next_jump == seconds_discounter:
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-{_s[1]}].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string)
        return str_out
    elif next_jump < seconds_discounter:
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-{'' if _s[0]==9 else '-9'}].*"
        print_range(str_out, start_ts_string, end_ts_string)
    
    # if we arrive here, we know seconds_discounter will be > 0
    # Calculate leftover range !!! 
    # What has been regexed doesn't need to be taken into account anymore at this point!!!
    # examples:
    # - (00:00) 00:10 - 00:11
    # - (00:59) 00:10 - 01:01

    seconds_discounter -= next_jump     # (00:00) 00:10 - 00:11     seconds_discounter = 1
    next_jump = 60 - ((_S[0]+1)*10)     # (00:00) 00:10 - 00:11     next_jump = 50

    if next_jump == 0: # but seconds_discounter = n > 0
        ...
    elif next_jump <= seconds_discounter:
        ...
    else: # next_jump > seconds_discounter
        # str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][0-9].*"
        ...
    


    # # 00:00 > 01:10
    # secs_to_next = 10 - _s[0]
    # if secs_to_next <= secs_left:
    #     # example: 35:55 > 36:05 | 35:55 > 37:05 (70) | 35:13 > 36:01 (47)
    #     str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-9].*"
    #     secs_left -= secs_to_next # (30)
    #     secs_to_next = 60 - ((_S[0]+1)*10) # 30
    #     if secs_left == 0:
    #         # example: 35:55 > 36:00
    #         str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*"
    #     # elif secs_left == secs_to_next:
    #     #     # example: 35:25 > 36:00 (30, 30) | 35:45 > 36:00 (10, 10)
    #     #     str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-5][0-9].*"
    #     #     str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*"
    #     elif secs_left <= secs_to_next:
    #         # examples: 35:15 > 35:21 (1 < 40) | 35:15 > 35:31 (11 < 40) | 35:15 > 35:55 (35 < 40)
    #         if (_S[1] - (_S[0]+1)) == 0:
    #             str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*"
    #         elif (_S[1] - (_S[0]+1)) == 1:
    #             str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}][0-9].*"
    #             str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    #         else:
    #             str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-{_S[1]-1}][0-9].*"
    #             str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    #     else: # secs_left > secs_to_next
    #         # examples: 
    #         # 00:30 > 01:10
    #         str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-5][0-9].*"

    #         secs_left -= secs_to_next #
    #         secs_to_next = (10 - (_m[0]+1)) * 60 # 4 * 60 = 240
            
    #         if secs_left == 0:
    #             # example: 03:35:55 > 03:40:00
    #             ... # Is already handled!!
    #         elif secs_left == secs_to_next:
    #             # example: 35:55 > 40:00 secs_left = 240 OK!
    #             str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]+1}-9]\:[0-5][0-9].*"
    #             str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][0].*"
    #         elif secs_left < secs_to_next:
    #             # example: (secs_to_next = 240)
    #             # 35:15 > 36:01 secs_left = 1
    #             # 35:15 > 36:25 secs_left = 25
    #             # 35:55 > 37:00 secs_left = 60
    #             # 35:55 > 37:10 secs_left = 70
    #             # 35:55 > 37:45 secs_left = 105
    #             # 35:55 > 38:00 secs_left = 120
    #             # 35:55 > 38:05 secs_left = 125
    #             # 35:55 > 38:59 secs_left = 179
    #             if (_m[1] - (_m[0]+1)) == 0:
    #                 if _S[1] == 0:
    #                     str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    #                 else:
    #                     str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0-{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    #             elif (_m[1] - (_m[0]+1)) == 1:
    #                 ...
    #                 # str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}][0-9].*"
    #                 # str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    #             else:
    #                 ...
    #                 # str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-{_S[1]-1}][0-9].*"
    #                 # str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*"
    # else:
    #     # OK!
    #     str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-{_s[1]}].*"


    str_out = f"{str_out})"
    return str_out


def run_test(
    regex_str: AnyStr,
    file_path: AnyStr = "/home/user/projects/ol-analytical-research/assets/generated/daterange_test.txt") -> List:
    matches = []
    try:
        with open(file_path, "r") as f:
            filedata = f.read()
            matches = re.findall(regex_str, filedata)
            # print(f"Number of matches found: [{len(matches)}]")
            # print(matches)
    except Exception as e:
        print(f"regex_str={regex_str}")
        print(f"e={e}")
    return matches


def main():
    # 86400 = full day
    start_ts_str = '2022-01-01T00:00:00'
    seconds = 40
    # end_ts = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=seconds)
    # end_ts_str = datetime.strftime(end_ts, '%Y-%m-%dT%H:%M:%S')
    # print(f"range = {start_ts_str} > {end_ts_str}")
    # start date iterator
    break_flag = False
    for i in range(0, seconds):
        loop_start_ts = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=i)
        loop_start_str = datetime.strftime(loop_start_ts, '%Y-%m-%dT%H:%M:%S')
        for j in range(i+1, seconds+1):
            loop_end_ts = loop_start_ts + timedelta(seconds=j)
            loop_end_str = datetime.strftime(loop_end_ts, '%Y-%m-%dT%H:%M:%S')
            regex = regex_time_range(loop_start_str, loop_end_str)
            matches = run_test(regex)
            expectation = secs_between(loop_start_str, loop_end_str) +1
            if len(matches) != expectation:
                print(f"{loop_start_str} > {loop_end_str}")
                print(regex)
                # print(f"matches={matches}")
                break_flag = True
                break
            # print(f"i={i} & j={j} & matches={len(matches)} & expectation={expectation}")
        if break_flag:
            break


if __name__ == "__main__":
    # main()
    print(secs_between("2022-01-01T00:00:00", "2022-01-01T00:00:10"))
        
