# from typing import List, Dict, Tuple, AnyStr, Any
from datetime import datetime
from db.model import session, AccountBalance, AccountTransaction, engine
from sqlalchemy import text
import asyncio
# from aiohttp import ClientSession
# from jsonrpcclient import Ok, parse
from config import Config
# import random
import os

addresses = []

with engine.connect() as con:
    sql = text("SELECT distinct address from accountbalance where wallet_type in ('X', 'N') and account_type not in ('community') and updated_at < (NOW() - INTERVAL '1 DAY')")
    addr_list = con.execute(sql)
    addresses = [addr[0] for addr in addr_list]

print(f"addr={len(addresses)}")


async def run_command(address):
    with os.popen(f"{Config.TOOLS_PATH}/ol -a {address} query -r | sed -n '/SlowWallet/,/StructTag/p'") as f:
        for elem in f.readlines():
            if 'SlowWallet' in elem:
                return {"address": address, "wallet_type": 'S'}
        return {"address": address, "wallet_type": 'N'}


async def process_addresses():
    tasks = []
    results = []
    sem = asyncio.Semaphore(Config.TASK_LIMIT)  # limit to x tasks running concurrently
    async with sem:
        for address in addresses:
            task = asyncio.create_task(run_command(address))
            tasks.append(task)
            if len(tasks) == Config.TASK_LIMIT:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                print(f"finished={len(done)}")
                for task in done:
                    result = task.result()
                    AccountBalance.update_wallet_type(result)
                    results.append(result)
                    tasks.remove(task)
    # wait for any remaining tasks to finish
    done, pending = await asyncio.wait(tasks)
    for task in done:
        result = task.result()
        AccountBalance.update_wallet_type(result)
        results.append(result)
    return results


def process_result(result):
    print(result)
    

async def main():
    results = await process_addresses()
    # Do something with results if needed...


if __name__ == '__main__':
    startdt = datetime.now()

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")

    enddt = datetime.now()
    print(f"seconds minutes: {(enddt-startdt).total_seconds()/60}")