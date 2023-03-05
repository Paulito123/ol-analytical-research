from ol_util import (
    load_account_balances_for_acc_type
    # , lookup_wallet_type
)
from db.model import session, AccountBalance, label, cast, Integer, or_
from typing import List, Dict, Tuple
from collections import namedtuple
from datetime import datetime
from time import mktime
from json import dumps, load
from db.config import Config
from db.model import AccountTransaction
from rpc import make_RPC_call
from requests.exceptions import HTTPError


# def lookup_slow_flag(address_list: List) -> None:
#     counter = 0
#     for addr_obj in address_list:
#         counter += 1
#         print(f"Checking [{counter}] {addr_obj['address']}")
#         id = session\
#             .query(AccountBalance.id)\
#             .filter(AccountBalance.address == addr_obj['address'])\
#             .scalar()
#         if addr_obj['account_type'] == 'community':
#             addr_obj['wallet_type'] = 'C'
#         else:
#             addr_obj['wallet_type'] = lookup_wallet_type(addr_obj['address'])
        
#         ab = AccountBalance(
#             id=id,
#             wallet_type=addr_obj['wallet_type']
#         )

#         session.merge(ab)
#         session.commit()
    
#     return None


def get_acc_balances() -> List:
    qres = session.query(
        AccountBalance.id,
        AccountBalance.address,
        AccountBalance.account_type,
        label("balance", cast(AccountBalance.balance / 1000000, Integer)),
        AccountBalance.updated_at)\
            .filter(AccountBalance.wallet_type=='X')\
            .all()
    list_out = []
    for ab in qres:
        obj = {
            "id": ab[0],
            "address": ab[1],
            "account_type": ab[2],
            "balance": ab[3],
            "updated_at": mktime(ab[4].timetuple()),
        }
        list_out.append(obj)
    return list_out


def how_liquid_are_we() -> None:
    print("getting validator balance...")
    load_account_balances_for_acc_type("validator")
    print("getting miner balances")
    load_account_balances_for_acc_type("miner")
    print("getting basic balances")
    load_account_balances_for_acc_type("basic")
    print("getting community balances")
    load_account_balances_for_acc_type("community")

    # print("getting unlocked balances")
    # AccountBalance.lookup_wallets_unlocked(AccountBalance)
    # print("lookup wallet types slow / normal")
    # AccountBalance.lookup_wallet_types(AccountBalance)
    # # # print("calculate liquidity...")
    # # # ls = AccountBalance.get_liquid_supply()
    # # # print(f"We have a liquid supply of {ls[0]} / {ls[1]}")

    print("done!")


def main():
    ...
    # account_balance_list = get_acc_balances()
    # lookup_slow_flag(account_balance_list)
    # Serializing json
    # json_object = dumps(account_balance_list_rich, indent=4)
    
    # # Writing to sample.json
    # with open(f"{Config.PYTHONPATH}/assets/generated/wallet_balances.json", "w") as outfile:
    #     outfile.write(json_object)

# def test_shit(url, counter, increase=10):
#     # address = "2bfd96d8a674a360b733d16c65728d72"
#     address = "7db562b2cc2c542ed65f2a2b94e0f2f8"
#     address = "00000000000000000000000000000000"
#     # while keep_going:
#         # print(f"counter={counter}")
#     try:
#         response = make_RPC_call(
#             url, 
#             "get_account_transactions", 
#             [address, counter, increase, True]
#         )

#         if response.status_code == 200:
#             result = response.json()
#             # print(result)
#             if 'result' in result:
#                 # print(f"[{datetime.now()}]:INFO:{len(result['result'])} results fetched")
#                 # escape if result is empty
#                 # if len(result["result"]) == 0:
#                 #     print("Exiting...")
#                     # keep_going = False
#                     # continue
#                 # ingest data
#                 # AccountTransaction.upload_result(address, result["result"])
#                 print(f'[{address}] on [{url}] = {len(result["result"])} records fetched.')
#                 return url
#             else:
#                 print(f"result={result}")
#         else:
#             print(f"Request failed with status code: {response.status_code}")

#     except HTTPError as h:
#         print(f"[{datetime.now()}]:HTTPERROR:{h}")
#     except Exception as e:
#         print(f"[{datetime.now()}]:ERROR:{e}")
    
#     return None


if __name__ == "__main__":
    how_liquid_are_we()

    # test_shit()

    # with open('/home/user/projects/ol-analytical-research/assets/fullnode_seed_playlist.json', 'r') as f:
    #     data = load(f)
    
    # nodes = [node['url'] for node in data['nodes']]
    # # print(nodes)

    # good_node_list = []

    # for node in nodes:
    #     print(f"processing node: {node}")
    #     good_node = test_shit(node, 0)
    #     if good_node:
    #         good_node_list.append(good_node)
    
    # print(f'good_node_list={good_node_list}')
