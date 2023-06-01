from ol_util import load_account_balances_for_acc_type
from db.model import session, AccountBalance, PermissionTree, label, cast, Integer
from time import mktime
from typing import List, Dict, Tuple, AnyStr, Any
from datetime import datetime
from db.model import session, AccountBalance, PermissionTree, AccountTransaction, engine, text
from asyncio import create_task, run, Semaphore, create_task, wait, FIRST_COMPLETED
from aiohttp import ClientSession
from jsonrpcclient import Ok, parse
import random


addresses = AccountBalance.get_all_accounts_with_type()
node = "https://0l.interblockcha.in:444/"
TASK_LIMIT = 10


async def get_ptree_for_address(addr_tuple: Tuple):

    max_error_count = 10

    async with ClientSession() as session:

        try:

            errors = 0
            
            while True:
                
                account_type = "validator" if addr_tuple[1] == "validator" else "miner"
                url = f"{node}permission-tree/{account_type}/{addr_tuple[0]}"

                async with session.get(url) as response:

                    parsed = await response.text()
                    
                    if isinstance(parsed, str):
                        
                        if len(parsed) == 0:
                            break
                        
                        # add directly to DB
                        print(f"push to ptree db for {addr_tuple[0]}")
                        PermissionTree.update_ptree(addr_tuple[0], parsed)
                        return 1

                    else:

                        print(f"[{datetime.now()}]:ERROR:{parsed.message}")
                        errors += 1

                # prevent infinite loop...
                if errors == max_error_count:
                    print(f"[{datetime.now()}]:ERROR:maximum number of errors [{max_error_count}] reached")
                    break
        
        except Exception as e:
            print(f"Error: {e}")
        
        return 0


async def process_addresses():
    tasks = []
    results = []
    sem = Semaphore(TASK_LIMIT)  # limit to x tasks running concurrently

    async with sem:
        for address in addresses:
            task = create_task(get_ptree_for_address(address))
            tasks.append(task)

            if len(tasks) == TASK_LIMIT:
                done, pending = await wait(tasks, return_when=FIRST_COMPLETED)
                # print(f"finished={len(done)}")

                for task in done:
                    result = task.result()
                    results.append(result)
                    tasks.remove(task)

    # wait for any remaining tasks to finish
    done, pending = await wait(tasks)

    return "a"


def write_ptree_to_json() -> None:

    with engine.connect() as con:
        sql = text("select ab.address, ab.account_type, pt.ptree from accountbalance ab left join permissiontree pt on ab.address = pt.address")
        result = con.execute(sql)

    filename = 'assets/generated/ptree.json'
    empty_dict = '{}'

    with open(filename, 'w') as f:
        f.write("[")

        is_first = True

        for row in result:
            if is_first:
                is_first = False
            else:
                f.write(",")
                
            f.write(f'{{"address": "{row[0]}", "type": "{row[1]}", "tree": {row[2] if row[2] else empty_dict}}}')

        f.write("]")

async def main():
    results = await process_addresses()
    # Do something with results if needed...


if __name__ == '__main__':
    startdt = datetime.now()

    # try:
    #     run(main())
    # except Exception as e:
    #     print(f"[{datetime.now()}]:ERROR:{e}")

    try:
        write_ptree_to_json()
    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")

    enddt = datetime.now()
    print(f"seconds minutes: {(enddt-startdt).total_seconds()/60}")
