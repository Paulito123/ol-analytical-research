from requests import Response, post
from typing import List, AnyStr, Any
from datetime import datetime
from aiohttp import ClientSession
from jsonrpcclient import Ok, parse


known_methods = {
    "get_transactions": ["startVersion", "limit", "includeEvents"],
    "get_recent_transactions": ["startVersion", "limit", "includeEvents"],
    "get_transaction": ["hash", "includeEvents"],
    'get_account': ["account"],
    'get_account_transaction': ["account", "sequenceNumber", "includeEvents"],
    'get_account_transactions': ["account", "start", "limit", "includeEvents"],
    'get_recent_account_transactions': ["account", "start", "limit", "includeEvents"],
    'get_metadata': ["version"],
    'get_events': ["key", "start", "limit"],
    'get_currencies': [],
    'get_tower_state_view': ["account"]
}

URL = "http://63.229.234.76:8080"


def make_RPC_call(url: AnyStr, method: AnyStr, params: List) -> Response:
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 1,
    }

    return post(url, json=payload, headers=headers)


async def make_RPC_call_async(url: AnyStr, method: AnyStr, params: List) -> Any:
    async with ClientSession() as session:
        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 1,
        }
        async with session.post(
            url, 
            json=payload,
            headers=headers
        ) as response:
            parsed = parse(await response.json())
            if isinstance(parsed, Ok):
                return parsed
            else:
                print(f"[{datetime.now()}]:ERROR:{parsed.message}")
                return None
    


if __name__ == "__main__":
    response = make_RPC_call(
        URL, 
        "get_account_transactions", 
        ["2bfd96d8a674a360b733d16c65728d72", 0, 100, False]
    )

    # response = make_RPC_call(
    #     URL, 
    #     "get_account", 
    #     ["2bfd96d8a674a360b733d16c65728d72"]
    # )

    if response.status_code == 200:
        result = response.json()
        print(f"Result: {result}")
    else:
        print(f"Request failed with status code: {response.status_code}")