from ol_util import load_account_balances_for_acc_type
from db.model import session, AccountBalance, label, cast, Integer
from typing import List
from time import mktime


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


def get_balances() -> None:
    print("getting validator balance...")
    load_account_balances_for_acc_type("validator")
    print("getting miner balances")
    load_account_balances_for_acc_type("miner")
    print("getting basic balances")
    load_account_balances_for_acc_type("basic")
    print("getting community balances")
    load_account_balances_for_acc_type("community")
    print("balances fetched!!")


def main():
    get_balances()
    

if __name__ == "__main__":
    main()
