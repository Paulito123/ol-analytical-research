from typing import AnyStr
from datetime import datetime, timedelta


if __name__ == "__main__":
    # seconds in a day
    ubound = (60*60*24)
    base_ts_str = "2022-01-01T00:00:00"
    base_ts = datetime.strptime(base_ts_str, "%Y-%m-%dT%H:%M:%S")
    outstr = ""
    for i in range(0, ubound):
        new_dt = base_ts + timedelta(seconds=i)
        outstr = outstr + f'{datetime.strftime(new_dt, "%Y-%m-%dT%H:%M:%S")} >> 1\n========{i}========\n'
    with open("/home/user/projects/ol-analytical-research/assets/generated/daterange_test.txt", "w") as f:
        f.write(outstr)
