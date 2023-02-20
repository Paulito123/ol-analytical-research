from typing import List, Dict, Tuple, AnyStr, Any
from datetime import datetime
from db.model import session, AccountBalance, AccountTransaction
from asyncio import create_task, sleep, get_event_loop, Queue, new_event_loop, set_event_loop
from aiohttp import ClientSession
from jsonrpcclient import Ok, parse
import random

addr_list = session\
    .query(AccountBalance.address)\
    .all()
addresses = [addr[0] for addr in addr_list]
nodes = ['http://63.229.234.76:8080', 'http://63.229.234.77:8080']

print()


async def get_transactions_for_address(node_url, address):
    max_error_count = 10
    lks = AccountTransaction.max_seq(address)
    last_known_seq = lks if lks else 0
    print(f"last_known_seq={last_known_seq}")

    async with ClientSession() as session:
        counter = last_known_seq
        increase = 200
        errors = 0
        while True:
            params = [address, counter, increase, True]
            headers = {
                'Content-Type': 'application/json'
            }

            payload = {
                "method": "get_account_transactions",
                "params": params,
                "jsonrpc": "2.0",
                "id": 1,
            }
            async with session.post(node_url, json=payload, headers=headers) as response:
                parsed = parse(await response.json())
                if isinstance(parsed, Ok):
                    if len(parsed.result) == 0:
                        break
                    # add directly to DB
                    print(f"push to db {len(parsed.result)} results")
                    AccountTransaction.upload_result(address, parsed.result)
                    counter += increase
                    errors = 0
                else:
                    print(f"[{datetime.now()}]:ERROR:{parsed.message}")
                    errors += 1
            # prevent infinite loop...
            if errors == max_error_count:
                print(f"[{datetime.now()}]:ERROR:maximum number of errors [{max_error_count}] reached")
                break


async def run_task(node_url):
    while True:
        # Pick the next address from the list
        try:
            address = addresses.pop(0)
        except IndexError:
            break  # No more addresses left to ingest

        # Fetch data for the current address from the current node
        print(f'Running task for address {address} on node {node_url}')
        await get_transactions_for_address(node_url, address)
        print(f'Finished task for address {address} on node {node_url}')

        # Add the next address for this node to the list
        next_address = addresses.pop(0)
        addresses.append(next_address)

        # Wait for a random amount of time before starting the next task
        await sleep(random.uniform(0.1, 0.5))


async def main():
    # Create a task pool with n workers
    task_pool = Queue(maxsize=len(nodes))

    # Add the initial set of tasks to the pool
    for node_url in nodes:
        await task_pool.put(create_task(run_task(node_url)))

    # Keep adding new tasks to the pool until all addresses have been ingested
    while addresses:
        task = await task_pool.get()
        await task
        task_pool.put_nowait(create_task(run_task(task.get_name())))


if __name__ == "__main__":
    print("Starting woohoo")
    loop = new_event_loop()
    set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    print("Done woohoo")
