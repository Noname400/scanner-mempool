#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from function import *

version = 'task pool sendwich 0.09 / 10.09.23'
G = 0
codec = RouterCodec(w3, hh)

def scan_mempool(tx):
    global G
    G += 1
    print(G)
    transaction = tx['tx']
    try:
        full_transaction = codec.decode.transaction(w3.to_bytes(transaction))
    except Exception as err:
        #print(err)
        return None
    
    to = full_transaction['to']
    block = full_transaction['blockNumber']
    print(block, to, redis_client.llen())
    if block is None and addr_routers.get(to) is not None:
        print(f'****************************************************************')
        print(full_transaction['decoded_input'])
        # ds =iterate_keys(full_transaction['decoded_input']['inputs'][1]) #find_tokens_recursive(decoded_trx_input[1])
        # print(ds)
        # reserve0, reserve1 = decode(['uint112','uint112'], data)
        # print(reserve0, reserve1)
        # ds["amountIn"] = amountIn
        # ds["amountOutMin"] = amountOutMin
        
        # n, s, d = info_token(path[0])
        # ds["token0_addr"] = path[0]
        # ds["token0_name"] = s
        # ds["token0_decimals"] = d
        
        # n, s, d = info_token(path[len(path)-1])
        # ds["token1_addr"] = path[len(path)-1]
        # ds["token1_name"] = s
        # ds["token1_decimals"] = d
        
        # ds["dex_addr"] = transaction["to"]
        # ds["dex_name"] = addr_routers.get(transaction["to"])
        # ds["pair"] = f'{ds["token0_name"]}/{ds["token1_name"]}'
        
        # ctnb1 = int(ds["token0_addr"], 16)
        # ctnb2 = int(ds["token1_addr"], 16)
        
        # if (ctnb1 > ctnb2):
        #     ds["price"] = amountIn / ds["token0_decimals"]
        # else:
        #     ds["price"] = amountOutMin / ds["token1_decimals"]
        # print(ds)
        # #считаем математику и отправляем транзу (bundel)
        

def process_tasks():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            task = redis_client.lpop('task_queue')
            if task is not None:
                task = task.decode('utf-8')
                task_data = loads(task)
                executor.submit(scan_mempool, task_data)

if __name__ == '__main__':
    print(f'Start {version}')
    db_create()
    process_tasks()
