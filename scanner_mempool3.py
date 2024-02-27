#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from function import *
version = '0.14 / 10.10.23'

def handle_event(event):
    ds:data_source = data_source()
    trx:TxData
    try:
        transaction = Web3.to_json(event).strip('"')
        trx = w3.eth.get_transaction(transaction)
        if trx.blockNumber is None and trx.to in addr_routers:
            ds.from_ = trx.get("from")
            ds.to_ = trx.to
            ds.value = trx.value
            ds.dex_addr = trx.to
            ds.dex_name = addr_routers.get(trx.to)
            ds.gas = trx.gas
            ds.gasPrice = trx.gasPrice
            if 'maxFeePerGas' in trx:
                ds.maxFeePerGas = trx.maxFeePerGas
                ds.maxPriorityFeePerGas = trx.maxPriorityFeePerGas
            decoded_trx_input = codec.decode.function_input(trx.input)
            for trx_decode in decoded_trx_input[1]['inputs']:
                ds = parser(trx_decode[1], ds)
                print('********* ',trx_decode[1],' ********')
            save_file('outds', ds.__dict__)
            return ds.__dict__
        else: return trx
    except TransactionNotFound:
        pass
    except Exception as err:
        save_file('errors_scan_mempool', f"{type(err)}{err}")
        # print(f'ERROR: {err}')
        # print(type(err))
    
if __name__ == '__main__':
    freeze_support()
    print(f'Run version: {version} / CPU usage: {cpu_count()}')
    num_processes = int(cpu_count()/2)
    tx_filter = w3.eth.filter('pending')
    with Pool(processes=num_processes) as pool:
        while True:
            events = tx_filter.get_new_entries()
            resu = pool.map(handle_event, events)
            if len(resu) > 0 or len(events) > 0:
                print(' '*120, end='\r')
                print(f"Events из сети: [{len(events)}] / Результатов после обработки: [{len(resu)}]", end='\r')