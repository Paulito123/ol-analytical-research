from requests import get as rget
from typing import List
import asyncio
from typing import AnyStr
from datetime import datetime


# async def get_active_set_ips_async() -> List:
#     api_url = "https://0lexplorer.io/api/webmonitor/vitals"
#     active_set_list = []
#     try:
#         result = rget(api_url, timeout=10).json()
#         active_set_list = [validator['validator_ip'] for validator in result['chain_view']['validator_view']]
#     except Exception as e:
#         print(f"{e}")
    
#     return active_set_list


def get_active_set_ips() -> List:
    api_url = "https://0lexplorer.io/api/webmonitor/vitals"
    active_set_list = []
    try:
        result = rget(api_url, timeout=10).json()
        active_set_list = [validator['validator_ip'] for validator in result['chain_view']['validator_view']]
    except Exception as e:
        print(f"{e}")
    
    return active_set_list


def validate_timestamp(timestamp_text: AnyStr) -> AnyStr:
    try:
        datetime.strptime(timestamp_text, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DDTHH:MI:SS")
    return timestamp_text


# async def main_async():
#     task_get_ips = asyncio.create_task(get_active_set_ips_async())
#     bla = await task_get_ips
#     print(bla)
    

if __name__ == "__main__":
    # asyncio.run(main_async())
    # print(validate_timestamp('2022-11-21T20:25:59'))

    # print(len(get_active_set_ips()))
    # print(get_active_set_ips())

    # sum
    # 104402.10947614838
    # count
    # 1035366

    # 1047395

    print(f"")

