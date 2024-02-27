url = "wss://solana-mainnet.g.alchemy.com/v2/U7qctecXWziIPPFI35ewlKXYGacSUjSK"
url = "https://solana-mainnet.g.alchemy.com/v2/U7qctecXWziIPPFI35ewlKXYGacSUjSK"
import asyncio
from asyncstdlib import enumerate
from solana.rpc.websocket_api import connect
import pprint
import json

async def main():
    async with connect("wss://api.mainnet-beta.solana.com") as websocket:
        await websocket.logs_subscribe()
        first_resp = await websocket.recv()
        subscription_id = first_resp[0].result
        next_resp = await websocket.recv()
        print(next_resp)
        await websocket.logs_unsubscribe(subscription_id)

    async with connect("wss://api.mainnet-beta.solana.com") as websocket:
        await websocket.logs_subscribe()
        first_resp = await websocket.recv()
        subscription_id = first_resp[0].result
        async for idx, msg in enumerate(websocket):
            if idx == 30:
                break
            print(msg)
        await websocket.logs_unsubscribe(subscription_id)

# asyncio.run(main())

import requests


# payload = {
#     "id": 1,
#     "jsonrpc": "2.0",
#     "method": "getSlot"
# }
# headers = {
#     "accept": "application/json",
#     "content-type": "application/json"
# }
# response = requests.post(url, json=payload, headers=headers)
# res = response.json()['result']
# print(res)


# s1 = {"jsonrpc": "2.0","id":1,"method":"getBlock","params":[554, {"encoding": "json","transactionDetails":"full","rewards":False}]}
# response = requests.post(url, json=s1, headers=headers)
# dd = response.json()
# pprint.pprint(dd, indent=4)

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getBlockCommitment",
    "params": [
      "9f5AoCo7kGGp77emVnFYPbsGGYxf64jN69fyrJCYCu9E",
      {
        "commitment": "finalized"
      }
    ]}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}
response = requests.post(url, json=payload, headers=headers)
dd = response.json()
pprint.pprint(dd, indent=4)