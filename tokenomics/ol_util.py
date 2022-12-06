import os
import re
from typing import AnyStr


def lookup_wallet_type(address: AnyStr) -> AnyStr:
    """
    Checks if a given address is a slow wallet.
    :param address: the address to check
    :return: 'S' > Slow, 'C' > Community, 'O' > Other
    """
    # check if the address is valid
    regex_out = re.search("[a-fA-F0-9]{32}$", address)
    if not regex_out:
        return False

    # We are checking both 'SlowWallet' and 'Community' occurence in the query output
    with os.popen(f"ol -a {address} query -r | sed -n '/SlowWallet/,/StructTag/p'") as f:
        for elem in f.readlines():
            if 'SlowWallet' in elem:
                return 'S'
    return 'O'


if __name__ == "__main__":
    
    test_list = [
        "5F8AC83A9B3BF2EFF20A6C16CD05C111", # SLOW basic wallet
        "2BFD96D8A674A360B733D16C65728D72", # normal basic wallet
        "1367B68C86CB27FA7215D9F75A26EB8F", # SLOW community wallet
        "5335039ab7908dc38d328685dc3b9141", # normal miner wallet
        "7e56b29cb23a49368be593e5cfc9712e", # SLOW validator wallet
        "82a1097c4a173e7941e2c34b4cbf15b4", # normal miner wallet
        "5e358589da97d5f08bf3a7462a112ae6", # normal miner wallet
        "19E966BFA4B32CE9B7E23721B37B96D2", # SLOW another community wallet
        "cd0fa23141e9e5e348b33c5da51f211d", # normal miner wallet
        "f100a2878d61bab8554aed256feb8001", # normal miner wallet
        "4be425e5306776a0bd9e2db152b856e6", # SLOW miner wallet
        "7103da7bb5bb15eb7e72b6db16147f56", # normal miner wallet
        "74745f89883134d270d0a57c6c854b4b", # normal miner wallet
    ]

    for addr in test_list:
        if lookup_wallet_type(addr) == 'S':
            print(f"{addr} is a slow wallet!")
        elif lookup_wallet_type(addr) == 'C':
            print(f"{addr} is a community wallet!")
        else:
            print(f"{addr} is a normal wallet!")
    