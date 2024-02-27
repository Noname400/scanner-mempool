#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""
version = 'function 0.6 / 10.10.23'

#https://medium.com/coinmonks/discovering-the-secrets-of-an-ethereum-transaction-64febb00935c
#https://eth-abi.readthedocs.io/en/stable/decoding.html
#https://github.com/tradingstrategy-ai/web3-ethereum-defi/blob/master/tests/test_block_reader.py
#https://habr.com/ru/articles/674204/

from os import path, mkdir
from datetime import datetime
from web3 import Web3, HTTPProvider
from web3.types import TxData
from web3.exceptions import TransactionNotFound
from abis import my_abi, Uniswap_V2
import redis
from eth_abi import encode, decode
from uniswap_universal_router_decoder import RouterCodec
import asyncio
import psycopg2
from time import time, sleep
import concurrent.futures
from json import loads, dumps
from signal import SIGINT, SIG_IGN, signal
from multiprocessing import Pool, freeze_support, cpu_count, Process, pool
#import sympy as sp

DB = {"ip":"92.255.77.103", "db":"buterbrod", "user":"search", "password":"Vfhbyfl66$$$"}

hh = "http://192.168.1.120:8545" #"https://nodes.speedynodes.net:8443/mainnet/eth-http?apikey=kCWonyiXqP9jbpzfozs6wckB6YspxqVg"
w3 = Web3(HTTPProvider(hh, request_kwargs={'timeout': 60}))

ww = "ws://192.168.1.120:8546/" #"wss://nodes.speedynodes.net:8443/mainnet/eth-ws?apikey=kCWonyiXqP9jbpzfozs6wckB6YspxqVg"
w3_ws = Web3(Web3.WebsocketProvider(ww, websocket_timeout=60))

codec = RouterCodec(w3)

QUOTE_TOKENS = ["BUSD", "USDC", "USDT", "WBTC", "DAI"]

class data_source(object):
    def __init__(self) -> None:
        self.from_ = ''
        self.to_ = ''
        self.hash = ''
        self.value = 0
        self.dex_addr = ''
        self.dex_name = ''
        self.maxFeePerGas = 0
        self.maxPriorityFeePerGas = 0
        self.gas = 0
        self.gasPrice = 0
        self.amount = 0
        self.amountIn = 0
        self.amountInMin = 0
        self.amountInMax = 0
        self.amountOut = 0
        self.amountOutMin = 0
        self.amountOutMax = 0
        self.data = ''
        self.path:list =  []
        self.reserve0 = 0
        self.reserve1 = 0
        self.pair_name = ''
        self.pair_addr:str = ''
        self.pair_liquidity = 0
        self.pair_price = 0.0
        self.token0_addr = ''
        self.token0_name = ''
        self.token0_symbol = ''
        self.token0_decimals = 0
        self.token1_addr = ''
        self.token1_name = ''
        self.token1_symbol = ''
        self.token1_decimals = 0

addr_routers = {Web3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"):"UniswapV2",
                Web3.to_checksum_address("0xEfF92A263d31888d860bD50809A8D171709b7b1c"):"PancakeSwapV2",
                Web3.to_checksum_address("0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f"):"SushiSwap",
                Web3.to_checksum_address("0x03f7724180AA6b939894B5Ca4314783B0b36b329"):"Shiba Inu: ShibaSwap",
                Web3.to_checksum_address("0xE592427A0AEce92De3Edee1F18E0157C05861564"):"Uniswap V3",
                Web3.to_checksum_address("0xEf1c6E67703c7BD7107eed8303Fbe6EC2554BF6B"):"Uniswap: Universal Router V2",
                Web3.to_checksum_address("0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD"):"Uniswap: Universal Router"}

def save_file(infile, text):
    if path.exists('log'): pass
    else: mkdir('log')
    file = f'log/{infile}.log'
    f = open(file, 'a', encoding='utf-8', errors='ignore')
    f.write(f'{text}\n')
    f.close()

def init_worker():
    signal(SIGINT, SIG_IGN)

def parser(data, ds):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "amount": ds.amount = value
            elif key == "amountIn": ds.amountIn = value
            elif key == "amountInMin": ds.amountInMin = value
            elif key == "amountInMax": ds.amountInMax = value
            elif key == "amountOut": ds.amountOut = value
            elif key == "amountOutMin": ds.amountOutMin = value
            elif key == "amountOutMax": ds.amountOutMax = value
            elif key == "data": ds.data = value.hex()
            elif key == "token": ds.pair_addr = value
            elif key == "path":
                if isinstance(value, list) and isinstance(value[0], bytes):
                    tmp = len(value)
                    ds.path = [value[0].hex(), value[tmp-1].hex()]
                elif isinstance(value, bytes): 
                    ds.path = [value[:20].hex(), value[-20:].hex()]
                else: 
                    ds.path = value
                n, s, d = info_token(ds.path[0])
                ds.token0_addr = ds.path[0]
                ds.token0_name = n
                ds.token0_symbol = s
                ds.token0_decimals = d
                n, s, d = info_token(ds.path[1])
                ds.token1_addr = ds.path[1]
                ds.token1_name = n
                ds.token1_symbol = s
                ds.token1_decimals = d
                ds.pair_name = f'{ds.token0_symbol}/{ds.token1_symbol}'
            elif isinstance(value, dict): parser(value, ds)
    elif isinstance(data, list):
        for item in data:
            parser(item[1], ds)
    return ds

def date_str():
    now = datetime.now()
    return now.strftime("%Y/%m/%d/, %H:%M:%S")

def info_token(token_name):
    usdt_contract_address = Web3.to_checksum_address(token_name)
    usdt_contract2 = w3.eth.contract(usdt_contract_address, abi=my_abi)
    token_name = usdt_contract2.functions.name().call()
    token_symbol = usdt_contract2.functions.symbol().call()
    token_decimals = usdt_contract2.functions.decimals().call()
    return token_name, token_symbol, token_decimals

def check_database(ip, db, user, password):
        conn = psycopg2.connect(
            host=ip,
            database=db,
            user=user,
            password=password
        )
        #conn.close()
        return True, conn

def db_create():
    #q, conn = check_database(ip="92.255.77.103", db="buterbrod", user="Noname", password="Vfhbyfl66$$$")
    q, conn = check_database(DB["ip"], DB["db"], DB["user"], DB["password"])
    if q:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stat (
                id SERIAL PRIMARY KEY,
                pair TEXT,
                price NUMERIC(20, 18),
                token0_addr CHARACTER(42),
                token0_name CHARACTER(42),
                token0_decimals BIGINT,
                token1_addr CHARACTER(42),
                token1_name CHARACTER(42),
                token1_decimals BIGINT,
                dex_addr CHARACTER(42),
                dex_name CHARACTER(42),
                date_update TIMESTAMP
            )
        ''')
        conn.commit()
        print('Table stat created ...')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS research (
                id SERIAL PRIMARY KEY,
                pair_name CHARACTER(42),
                pair_addr CHARACTER(42),
                pair_price NUMERIC(20, 18),
                dex_name CHARACTER(42),
                dex_addr CHARACTER(42),
                counter INTEGER, 
                date_update TIMESTAMP
            )
        ''')
        conn.commit()
        print('Table research created ...')
        cur.close()
        conn.close()

def add_db_stat(src: dict):
    q, conn = check_database(DB["ip"], DB["db"], DB["user"], DB["password"])
    if q:
        cur = conn.cursor()
        insert_query = """
            INSERT INTO stat (pair, price, token0_addr, token0_name, token0_decimals, token1_addr, token1_name, token1_decimals, dex_addr, dex_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            src["pair"],
            src["price"],
            src["token0_addr"],
            src["token0_name"],
            src["token0_decimals"],
            src["token1_addr"],
            src["token1_name"],
            src["token1_decimals"],
            src["dex_addr"],
            src["dex_name"]
        )
        cur.execute(insert_query, values)
        conn.commit()
        cur.close()
        conn.close()
        return True
    
def add_db_research(src: dict):
    q, conn = check_database(DB["ip"], DB["db"], DB["user"], DB["password"])
    if q:
        cur = conn.cursor()

        check_query = """
            SELECT COUNT(*) FROM research WHERE pair_addr = %s
        """
        cur.execute(check_query, (src["pair_addr"],))
        result = cur.fetchone()

        if result and result[0] > 0:
            update_query = """
                UPDATE research
                SET pair_price = %s, date_update = now(), counter = counter + 1
                WHERE pair_addr = %s
            """
            cur.execute(update_query, (src["pair_price"], src["pair_addr"]))
        else:
            insert_query = """
                INSERT INTO research (pair_name, pair_addr, pair_price, dex_name, dex_addr,counter, date_update)
                VALUES (%s, %s, %s, %s, %s, 1, now())
            """
            values = (
                src["pair_name"],
                src["pair_addr"],
                src["pair_price"],
                src["dex_name"],
                src["dex_addr"],
            )
            cur.execute(insert_query, values)

        conn.commit()
        cur.close()
        conn.close()
        return True

def sel_db_stat():
    q, conn = check_database(DB["ip"], DB["db"], DB["user"], DB["password"])
    if q:
        cur = conn.cursor()
        cur.execute("SELECT * FROM stat")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data

def sel_db_research():
    q, conn = check_database(DB["ip"], DB["db"], DB["user"], DB["password"])
    if q:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.research ORDER BY date_update DESC LIMIT 500")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data

def oracle(ds):
    contract_addr = Web3.to_checksum_address('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
    contract = w3.eth.contract(contract_addr, abi=Uniswap_V2)
    bribeToMiners = Web3.to_wei(20, 'gwei')
    t0 = int(ds["token0_addr"],16)
    t1 = int(ds["token1_addr"],16)
    if (t0 < t1):
        a = ds["reserve0"]
        b = ds["reserve1"]
    else:
        a = ds["reserve1"]
        b = ds["reserve0"]
        
    maxGasFee = ds["maxFeePerGas"] + bribeToMiners if ds["maxFeePerGas"] else bribeToMiners
    priorityFee = ds["maxPriorityFeePerGas"] + bribeToMiners if ds["maxPriorityFeePerGas"] else bribeToMiners

    ###################################################################################################
    firstAmountOut = contract.functions.getAmountOut(ds["amountIn"], a, b).call()
    updatedReserveA = a + ds["amountIn"]
    updatedReserveB = b + (firstAmountOut * 997) // 1000
    print(firstAmountOut, updatedReserveA, updatedReserveB)
    ###################################################################################################
    secondBuyAmount = contract.functions.getAmountOut(ds["amountIn"], updatedReserveA, updatedReserveB).call()
    print(secondBuyAmount, ds["amountOutMin"])

    if secondBuyAmount < ds["amountOutMin"]:
        print('Victim would get less than the minimum')

    updatedReserveA2 = updatedReserveA + ds["amountIn"]
    updatedReserveB2 = updatedReserveB + (secondBuyAmount * 997) // 1000
    secondBuyAmount = contract.functions.getAmountOut(firstAmountOut, updatedReserveB2, updatedReserveA2).call()
    ###################################################################################################
    deadline = int(time.time()) + 60 * 60  # 1 час с текущего момента

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    print("Successfully connected to Redis task!")
except redis.ConnectionError as e:
    print("Error connecting to Redis task:", str(e))
    
# if __name__ == '__main__':
#     ds = {"pair":"", "price":0.00000001111, "token0_addr":"", "token0_name":"", "token0_decimals":0, "token1_addr":"", "token1_name":"", "token1_decimals":0, "dex_addr":"", "dex_name":""}
#     db_create()
#     s = add_db(ds)
#     print(s)