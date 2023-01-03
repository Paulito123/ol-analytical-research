#!/usr/bin/python3
# The goal of this script is to search for patterns inside 
# log files for a given date range.

import os
import re
from typing import List, AnyStr
from datetime import datetime, timedelta

# time gaps
time_gap_list = [
    ("2022-11-21T23:00:00", "2022-11-22T01:55:00"),
]


def secs_between(start_ts_string: AnyStr, end_ts_string: AnyStr) -> int:
    a = datetime.strptime(start_ts_string, "%Y-%m-%dT%H:%M:%S")
    b = datetime.strptime(end_ts_string, "%Y-%m-%dT%H:%M:%S")
    return int((b-a).total_seconds())


def print_range(regex, start, end, seconds_rest=None, tag="", message=""):
    if seconds_rest:
        secs_between_start_end = secs_between(start, end)
        seconds_from_start = secs_between_start_end - seconds_rest
        new_start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=seconds_from_start)
        start = datetime.strftime(new_start, "%Y-%m-%dT%H:%M:%S")
    print(f"<{tag}>[{message}]={regex}")


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
    # When will the next 10 sec roll over?  00:00:00 > 00:00:10
    next_roll = (10 - _s[0]) # (0-9)

    # DEBUG
    print(f"############################# NEW ############################# {start_ts_string} > {end_ts_string}")
    print(f"[s] next_roll={next_roll} & seconds_discounter={seconds_discounter}")

    # Screw otpimization, stick to the easiest way out, which is a layered hamburger regex 

    # 00:01 - 00:07     next_roll = 9  | seconds_discounter = 6  (next_roll > seconds_discounter)
    # 00:05 - 00:10     next_roll = 5  | seconds_discounter = 5  (next_roll = seconds_discounter)
    # 00:00 - 00:11     next_roll = 10 | seconds_discounter = 11 (next_roll < seconds_discounter)
    
    # Opening regex:
    if next_roll > seconds_discounter:
        str_out = f"{str_out}{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[0]}-{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=1, message="FINAL")
        return str_out
    elif next_roll == seconds_discounter:
        # 01:45 > 01:50
        # [0][1]:[4][5-9] | [0][1]:[5][0]
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=2, message="FINAL")
        return str_out
    else:  # next_roll < seconds_discounter:
        str_out = f"{str_out}{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]}][{_s[0]}{'' if _s[0]==9 else '-9'}].*"
        print_range(str_out, start_ts_string, end_ts_string, tag=3, message="PARTIAL")
    
    # if we arrive here, we know seconds_discounter will be > 0
    # Calculate leftover range !!! 
    # What has been regexed doesn't need to be taken into account anymore at this point!!!

    seconds_discounter -= next_roll
    # When will the next 1 minute roll over?    00:00:00 > 00:01:00 
    next_roll = 60 - ((_S[0] + 1) *10) # (50-0)
    print(f"[S] next_roll={next_roll} & seconds_discounter={seconds_discounter}")

    # examples:
    #  Hh:Ss[0]
    # (00:00)   00:10 - 59:00 next_roll = 50 | seconds_discounter = 3530
    # (00:59)   01:00 - 05:00 next_roll = 0  | seconds_discounter = 300
    # (00:45)   00:50 - 01:30 next_roll = 10 | seconds_discounter = 40
    if next_roll == 0:
        # Do nothing... because this level rolls over with the previous regex
        ...
    elif seconds_discounter == 0:
        # (00:00)   01:00 - 01:00 next_roll = 540 | seconds_discounter = 0
        # [0][1-8]\:[1-5][0-9]
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=4, message="FINAL")
        return str_out
    elif next_roll > seconds_discounter: # but seconds_discounter = n > 0
        # All outcomes close the regex !
        # (00:00)   00:10 - 00:11 next_roll = 50 | seconds_discounter = 1       (next_roll > seconds_discounter)
        # [0][0]\:[1][0-1]
        if (_S[1] -(_S[0]+1)) == 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=5, message="FINAL")
            return str_out

        # (00:00)   00:10 - 00:28 next_roll = 50 | seconds_discounter = 18      (next_roll > seconds_discounter)
        # [0][0]\:[1][0-9]|[0][0]\:[2][0-8]
        elif (_S[1] -(_S[0]+1)) == 1:
            str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][0-{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=6, message="FINAL")
            return str_out

        # (00:00)   00:10 - 00:38 next_roll = 50 | seconds_discounter = 28      (next_roll > seconds_discounter)
        # [0][0]\:[1-2][0-9]|[0][0]\:[3][0-8]
        else: # (_S[1] -(_S[0]+1)) > 1
            str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}-{_S[1]-1}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=7, message="FINAL")
            return str_out
    elif next_roll == seconds_discounter:
        # (00:11)   00:20 - 01:00 next_roll = 39 | seconds_discounter = 39
        # (00:25)   00:30 - 01:00 next_roll = 30 | seconds_discounter = 30
        # (00:00)   00:10 - 01:00 next_roll = 35 | seconds_discounter = 35
        # [0][0]\:[5][0-9]|[0][0]\:[3][0-8]
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}{'' if (_S[0]+1)==5 else '-5'}][0-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=8, message="FINAL")
        return str_out
    else: # next_roll < seconds_discounter
        # (00:45)   00:50 - 01:01 next_roll = 10 | seconds_discounter = 11      (next_roll = seconds_discounter)
        # [0][0]\:[5][0-9]
        # (00:25)   00:30 - 01:43 next_roll = 30 | seconds_discounter = 73      (next_roll = seconds_discounter)
        # [0][0]\:[3-5][0-9]
        # (00:00)   00:10 - 02:00 next_roll = 50 | seconds_discounter = 110     (next_roll = seconds_discounter)
        # [0][0]\:[1-5][0-9]
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]}]\:[{_S[0]+1}{'' if (_S[0]+1)==5 else '-5'}][0-9].*"
        print_range(str_out, start_ts_string, end_ts_string, tag=9, message="PARTIAL")
        
    seconds_discounter -= next_roll
    # When will the next 10 minutes roll over?    00:00:00 > 00:10:00 
    next_roll = (10 - (_m[0]+1)) * 60
    print(f"[m] next_roll={next_roll} & seconds_discounter={seconds_discounter}")

    if next_roll == 0:
        # Do nothing... because this level rolls over with the previous regex
        ...
    elif seconds_discounter == 0:
        # (00:00)   01:00 - 01:00 next_roll = 540 | seconds_discounter = 0
        # [0][1-8]\:[1-5][0-9]
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=10, message="FINAL")
        return str_out
    elif next_roll > seconds_discounter: # but seconds_discounter = n > 0
        # All outcomes close the regex !
        # (00:00)   01:00 - 01:10 next_roll = 540 | seconds_discounter = 10
        # [0][1]\:[0][0-9]|[0][1]\:[1][0]
        if seconds_discounter < 60:
            if _S[1] == 0:
                # (00:00)   01:00 - 01:01 next_roll = 540 | seconds_discounter = 1
                # [0][1]\:[0][0-1]
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=12, message="FINAL")
                return str_out
            else:
                # (00:00)   01:00 - 01:23 next_roll = 540 | seconds_discounter = 23
                # [0][1]\:[0-1][0-9] | [0][2]\:[2][0-3]
                # (00:00)   01:00 - 01:58 next_roll = 540 | seconds_discounter = 58
                # [0][1]\:[0-4][0-9] | [0][1]\:[5][0-8]
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=14, message="FINAL")
                return str_out
        else:
            if _m[1] - (_m[0] + 1) == 1:
                # (00:00)   01:00 - 02:01 next_roll = 540 | seconds_discounter = 61
                # [0][1]\:[0-5][0-9] | [0][2]\:[0][0-1]
                # (00:00)   01:00 - 02:35 next_roll = 540 | seconds_discounter = 95
                # [0][1]\:[0-5][0-9] | [0][2]\:[0-2][0-9] | |[0][2]\:[3][0-5]
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[0]+1}]\:[0-5][0-9].*"
                if _S[1] == 0:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[0][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=15, message="FINAL")
                    return str_out
                else:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else (f'0-{_S[1]-1}')}][0-9].*"
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=16, message="FINAL")
                    return str_out
            else:
                # (00:00)   01:00 - 03:01 next_roll = 540 | seconds_discounter = 121
                # [0][1-2]\:[0-5][0-9] | [0][3]\:[0][0-1]
                # (00:00)   01:00 - 03:35 next_roll = 540 | seconds_discounter = 155
                # [0][1-2]\:[0-5][0-9] | [0][3]\:[0-2][0-9] | [0][3]\:[3][0-5]
                # (01:45)   02:00 - 09:58 next_roll = 480 | seconds_discounter = 478
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[0]+1}-{_m[1]-1}]\:[0-5][0-9].*"
                if _S[1] == 0:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=17, message="FINAL")
                else:
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"
                    str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
                    print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=18, message="FINAL")
                return str_out
    elif next_roll == seconds_discounter:
        # All outcomes close the regex !
        # (00:45)   01:00 - 10:00 next_roll = 540 | seconds_discounter = 540
        # [0][1-9]\:[0-5][0-9] | [0][0]\:[3][0-8]
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]+1}{'' if (_m[0]+1)==9 else '-9'}]\:[0-5][0-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=19, message="FINAL")
        return str_out
    else: # next_roll < seconds_discounter
        # (50:45)   51:00 - 00:01 next_roll = 540 | seconds_discounter = 61
        # [0][1-9]\:[0-5][0-9]

        # (26:00)   27:00 > 29:59   (59:19) next_roll = 540 | seconds_discounter = 541
        # [0][1-9]\:[0-5][0-9]
        ############################# NEW ############################# 2022-01-01T01:43:00 > 2022-01-01T02:01:19
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{_M[0]}][{_m[0]+1}{'' if (_m[0]+1)==9 else '-9'}]\:[0-5][0-9].*"
        print_range(str_out, start_ts_string, end_ts_string, tag=20, message="PARTIAL")
        
        
    seconds_discounter -= next_roll
    # When will the next 1 hour roll over?    00:00:00 > 01:00:00 
    next_roll = (6 - (_M[0] + 1)) * 10 * 60     # (0-3000)
    print(f"[M] next_roll={next_roll} & seconds_discounter={seconds_discounter}")
    # 10:00 > 38:00

    if next_roll == 0:
        # Do nothing...
        ...
    elif seconds_discounter == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=21, message="FINAL")
        return str_out
    elif next_roll > seconds_discounter:
        # All outcomes close the regex !
        # (01:45)   10:00 > 18:25   next_roll=3000 | seconds_discounter=505
        # [1][0-7]:[0-5][0-9] | [1][8]:[0-1][0-9] | [1][8]:[2][0-5]
        if seconds_discounter <= 9:
            # (01:45)   10:00 > 10:08   next_roll=3000 | seconds_discounter=8
            # [1][0]:[0][0-8]
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=22, message="FINAL")
            return str_out
        elif seconds_discounter < 60:
            # (01:45)   10:00 > 10:37   next_roll=3000 | seconds_discounter=37
            # [1][0]:[0-2][0-9] | [1][0]:[3][0-7]
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{f'0-{_S[1]-1}' if _S[1]>1 else '0'}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=23, message="FINAL")
            return str_out
        elif seconds_discounter < 600:
            ############################# NEW ############################## 2022-01-01T01:43:00 > 2022-01-01T01:59:59
            if _M[1] - (_M[0]+1) == 1:
                # 01:33:00 > 01:59:58   [4][0-9][0-5][0-9]
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]-1}][0-9]\:[0-5][0-9].*"
            elif _M[1] - (_M[0]+1) > 1:
                # 01:23:00 > 01:59:58 > 
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[0]+1}-{_M[1]-1}][0-9]\:[0-5][0-9].*"
            
            if _m[1] >= 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{f'0-{_m[1]-1}' if _m[1]>1 else '0'}]\:[0-5][0-9].*"

            if _S[1] >= 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{f'0-{_S[1]-1}' if _S[1]>1 else '0'}][0-9].*"
            
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=25, message="FINAL")
            return str_out 
        else: # seconds_discounter < 3600
            # (26:00)   30:00 > 50:00   (59:19) next_roll = 540 | seconds_discounter = 541
            # [3-4][0-5]\:[0-5][0-9] | [5][0-8]:[0-5][0-9] | [5][9]:[0][0-9] | [5][9]:[1][0-9]
            if _M[1] - (_M[0] + 1) == 1:
                # (36:00)   40:00 > 59:19   (59:19) next_roll = 540 | seconds_discounter = 541
                # [3-4][0-5]\:[0-5][0-9] | [5][0-8]:[0-5][0-9] | [5][9]:[0][0-9] | [5][9]:[1][0-9]
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[0]+1}][0-9]\:[0-5][0-9].*"
            else:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[0]+1}-{_M[1]-1}][0-9]\:[0-5][0-9].*"

            if _m[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
            
            if _S[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]<=1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=26, message="FINAL")
            return str_out
    else: # next_roll < seconds_discounter:
        str_out = f"{str_out}|{ds}[{_H[0]}][{_h[0]}]\:[{'5' if (_M[0]+1)==5 else f'{_M[0]+1}-5'}][0-9]\:[0-5][0-9].*"
        print_range(str_out, start_ts_string, end_ts_string, tag=27, message="PARTIAL")


    seconds_discounter -= next_roll
    # When will the next 10 hour roll over?   00:00:00 > 10:00:00
    next_roll = (10 - (_h[0] + 1)) * 60 * 60    # (0-36000)
    print(f"[h] next_roll={next_roll} & seconds_discounter={seconds_discounter}")

    if next_roll == 0:
        # Do nothing...
        ...
    elif seconds_discounter == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=28, message="FINAL")
        return str_out
    elif next_roll > seconds_discounter:
        # All outcomes close the regex !
        if seconds_discounter <= 9:
            # (00:00:00)   01:00:00 > 01:00:08   next_roll=36000 | seconds_discounter=8
            
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=29, message="FINAL")
            return str_out
        elif seconds_discounter < 60:
            # (00:00:00)   01:00:00 > 01:00:58   next_roll=36000 | seconds_discounter=58
            
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]<=1 else f'0-{_S[1]-1}'}][0-9].*"
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=30, message="FINAL")
            return str_out
        elif seconds_discounter < 600:
            # (00:00:00)   01:00:00 > 01:05:00   next_roll=36000 | seconds_discounter=300
            
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]==1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"

            if _S[1] >= 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=31, message="FINAL")
            return str_out
        elif seconds_discounter < 3600:
            # (00:00:00)   01:00:00 > 01:15:00   next_roll=36000 | seconds_discounter=3900

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]==1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

            if _m[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
            
            if _S[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=32, message="FINAL")
            return str_out
        else: # seconds_discounter < 36000
            # (00:00:00)   00:00:00 > 09:59:59   next_roll=36000 | seconds_discounter=28799
            if _h[1] - (_h[0] + 1) == 1:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]+1}]\:[0-5][0-9]\:[0-5][0-9].*"
            else:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[0]+1}-{_h[1]-1}]\:[0-5][0-9]\:[0-5][0-9].*"

            if _M[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]<=1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

            if _m[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
            
            if _S[1] > 0:
                str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
            print_range(str_out, start_ts_string, end_ts_string, tag=33, message="FINAL")
            return str_out
    else: # next_roll < seconds_discounter:
        str_out = f"{str_out}|{ds}[{_H[0]}][{'9' if (_M[0]+1)==9 else f'{_M[0]+1}-9'}]\:[0-5][0-9]\:[0-5][0-9].*"
        print_range(str_out, start_ts_string, end_ts_string, tag=34, message="PARTIAL")   

    # update discounter
    seconds_discounter -= next_roll
    # When will the next day roll over?   00:00:00 > 10:00:00
    next_roll = (2 - (_H[0] + 1)) * 60 * 60 * 10    # (0-36000)

    if next_roll == 0:
        # TODO: Add code for dat range here...
        # This would be a new day...
        ...
    
    if seconds_discounter == 0:
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, seconds_discounter, tag=35, message="FINAL")
        return str_out
    
    # All outcomes close the regex !
    if seconds_discounter <= 9:
        # (00:00:00)   01:00:00 > 01:00:08   next_roll=36000 | seconds_discounter=8
        
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=36, message="FINAL")
        return str_out
    elif seconds_discounter < 60:
        # (00:00:00)   01:00:00 > 01:00:58   next_roll=36000 | seconds_discounter=58
        
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]<=1 else f'0-{_S[1]-1}'}][0-9].*"
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=37, message="FINAL")
        return str_out
    elif seconds_discounter < 600:
        # (00:00:00)   01:00:00 > 01:05:00   next_roll=36000 | seconds_discounter=300
        
        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]==1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"

        if _S[1] >= 1:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'' if _s[1]==0 else '0-'}{_s[1]}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=38, message="FINAL")
        return str_out
    elif seconds_discounter < 3600:
        # (00:00:00)   01:00:00 > 01:15:00   next_roll=36000 | seconds_discounter=3900

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]==1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

        if _m[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
        
        if _S[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=39, message="FINAL")
        return str_out
    else: # seconds_discounter < 36000
        # (00:00:00)   00:00:00 > 09:59:59   next_roll=36000 | seconds_discounter=28799
        if _H[1] - (_H[0]+1) == 1:
            str_out = f"{str_out}|{ds}[{_H[0]+1}][0-9]\:[0-5][0-9]\:[0-5][0-9].*"
        
        if _h[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{'0' if _h[1]<=1 else f'0-{_h[1]-1}'}]\:[0-5][0-9]\:[0-5][0-9].*"

        if _M[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{'0' if _M[1]<=1 else f'0-{_M[1]-1}'}][0-9]\:[0-5][0-9].*"

        if _m[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{'0' if _m[1]<=1 else f'0-{_m[1]-1}'}]\:[0-5][0-9].*"
        
        if _S[1] > 0:
            str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{'0' if _S[1]==1 else f'0-{_S[1]-1}'}][0-9].*"

        str_out = f"{str_out}|{ds}[{_H[1]}][{_h[1]}]\:[{_M[1]}][{_m[1]}]\:[{_S[1]}][{'0' if _s[1]==0 else f'0-{_s[1]}'}].*)"
        print_range(str_out, start_ts_string, end_ts_string, tag=40, message="FINAL")
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
    break_flag = False
    start_ts_str = "2022-01-01T00:00:00"
    start_ts = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S')
    end_ts_str = "2022-01-01T21:00:01"
    end_ts = datetime.strptime(end_ts_str, '%Y-%m-%dT%H:%M:%S')

    total_seconds = secs_between(start_ts_str, end_ts_str)

    for i in range(0, total_seconds+1):
        subj_start_ts = start_ts + timedelta(seconds=i)
        subj_start_str = datetime.strftime(subj_start_ts, '%Y-%m-%dT%H:%M:%S')
        for j in range(0, total_seconds-i):
            subj_end_ts = end_ts - timedelta(seconds=j)
            subj_end_str = datetime.strftime(subj_end_ts, '%Y-%m-%dT%H:%M:%S')

            regex = regex_time_range(subj_start_str, subj_end_str)
            matches = run_test(regex)
            expectation = secs_between(subj_start_str, subj_end_str) +1
            if len(matches) != expectation:
                print("__________________________________________________ERROR__________________________________________________")
                print(f"[Result does not match!] {subj_start_str} > {subj_end_str}")
                print(regex)
                # print(f"matches={matches}")
                break_flag = True
                # os.system("aplay -d 1 ./assets/sin.wav")
                break
        if break_flag:
            break

if __name__ == "__main__":
    main()
    # print(secs_between("2022-01-01T00:00:00", "2022-01-01T00:00:10"))
