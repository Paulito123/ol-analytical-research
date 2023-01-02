from datetime import datetime, timedelta
from typing import AnyStr
from time import sleep


def secs_between(start_ts_str: AnyStr, end_ts_str: AnyStr) -> int:
    a = datetime.strptime(start_ts_str, "%Y-%m-%dT%H:%M:%S")
    b = datetime.strptime(end_ts_str, "%Y-%m-%dT%H:%M:%S")
    return int((b-a).total_seconds())


# 86400 = full day
start_ts_str = '2022-01-01T00:00:10'
end_ts_str = '2022-01-01T00:00:11'
seconds_discounter = secs_between(start_ts_str, end_ts_str)

print(seconds_discounter)

ds = start_ts_str[0:11:]
de = end_ts_str[0:11:]
_H = (int(start_ts_str[11::12]), int(end_ts_str[11::12]))
_h = (int(start_ts_str[12::13]), int(end_ts_str[12::13]))
_M = (int(start_ts_str[14::15]), int(end_ts_str[14::15]))
_m = (int(start_ts_str[15::16]), int(end_ts_str[15::16]))
_S = (int(start_ts_str[17::18]), int(end_ts_str[17::18]))
_s = (int(start_ts_str[18::19]), int(end_ts_str[18::19]))


# for i in range(0, seconds_discounter):
    # subject = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=i)
    # subject_str = datetime.strftime(subject, '%Y-%m-%dT%H:%M:%S')
    
    # secs_rest = seconds_discounter - i
    
    # H = subject.hour
    # M = subject.minute
    # S = subject.second

    # H_ = 24-H
    # M_ = (60-M) * 60
    # S_ = 60-S

    # seconds_to_next_hour = M_ + S_

    # seconds_discounter -= (10 - _s[0])
    # seconds_to_next_level_m = 60 - ((_S[0]+1)*10)
    # seconds_to_next_level_M = (10 - _m[0]) * 60

    # print(f"{sstring} H_={H_} M_={M_} S_={S_} seconds_to_next_hour={seconds_to_next_hour}")
    # sleep(0.3)

    # if seconds_to_next_hour <= secs_left
    
    # _H = int(sstring[11::12])
    # _h = int(sstring[12::13]) 
    # _M = int(sstring[14::15]) #60 - _M
    # _m = int(sstring[15::16]) #10 - _m
    # _S = int(sstring[17::18]) #60 - _S * 10
    # _s = int(sstring[18::19]) #10 - _s
    
    # loop_start_ts = datetime.strptime(start_ts_str, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=i)
    # loop_start_str = datetime.strftime(loop_start_ts, '%Y-%m-%dT%H:%M:%S')
    # for j in range(i+1, seconds+1):
    #     loop_end_ts = loop_start_ts + timedelta(seconds=j)
    #     loop_end_str = datetime.strftime(loop_end_ts, '%Y-%m-%dT%H:%M:%S')
        
        