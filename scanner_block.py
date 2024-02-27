#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from function import *
version = 'filling DB 0.7 / 10.10.23'

def handle_event(event):
        ds = data_source()
        log = dict(event)
        try:
            full_transaction = codec.decode.transaction(log["transactionHash"])
        except Exception as e:
            if e.args[0].find('matching selector') > -1:
                pass
            else: print(e)
        else:
            inputs = full_transaction.get('decoded_input').get('inputs')
            print('--------------------------------')
            print(inputs)
            print('--------------------------------')
            ds.pair_addr = log.get("address")
            ds.dex_addr = full_transaction["to"]
            ds.dex_name = addr_routers.get(full_transaction["to"])
            ds.from_ = full_transaction['from']
            ds.to_ = full_transaction['to']
            ds.hash = full_transaction['hash']
            ds.value = full_transaction['value']
            ds.reserve0, ds.reserve1 = decode(['uint112','uint112'], log['data'])
            ds_ = parser(inputs, ds)
            print(Web3.to_json(ds_.__dict__))
            
            if (ds_.token0_symbol in QUOTE_TOKENS) or (ds_.token1_symbol in QUOTE_TOKENS):
                print('ВЫХОД -> QUOTE_TOKENS')
                return None
            
            ctnb0 = (ds_.reserve0 / (10**ds_.token0_decimals))
            ctnb1 = (ds_.reserve1 / (10**ds_.token1_decimals))
            
            if (ds_.token0_addr < ds_.token1_addr):
                ds_.pair_price = (ctnb0) / (ctnb1)
            else:
                ds_.pair_price = (ctnb1) / (ctnb0)

            save_file('block', Web3.to_json(ds_.__dict__))
            #add_db_research(ds.__dict__)
            #считаем математику и отправляем транзу (bundel)
            print(f'********** {ds_.pair_name} *** {ds_.pair_price:.18f} ********')
            # except Exception as err:
            #     exc_type, exc_value, exc_traceback = sys.exc_info()
            #     if str(exc_value).find('selector') != -1:
            #         print(exc_type, exc_value, exc_traceback)

async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

def filter_topics():
    try:
        topic = w3_ws.eth.filter({"topics": ["0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"]})
    except: filter_topics()
    else: return topic

def main():
    topic = filter_topics()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(log_loop(topic, 2)))
    except Exception as E:
        print(E)
        main()
    finally:
        loop.close()

if __name__ == '__main__':
    print(f'Start {version}')
    #db_create()
    main()