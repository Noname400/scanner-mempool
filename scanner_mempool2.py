from function import *

version = '0.09 / 21.09.23'

global_count = 0
global_total = 0

codec = RouterCodec()

def handle_event(event):
    t = ''
    transaction = Web3.to_json(event).strip('"')
    print(transaction)
    global global_count
    global global_total
    global_total += 1
    print(f'Counter transaction: {global_total}', end='\r')
    t = w3_ws.eth.get_transaction(event)
    # try:
    #     transaction = Web3.to_json(event).strip('"')
    #     global_total += 1
    #     print(f'Counter transaction: {global_total}', end='\r')
        
    #     transaction = w3_ws.eth.get_transaction(transaction)
    #     if transaction.blockNumber is None and transaction.to in addr_routers:
    #         ds = data_source()
    #         ds.from_ = transaction.get("from")
    #         ds.to_ = transaction.to
    #         ds.value = transaction.value
    #         ds.dex_addr = transaction.to
    #         ds.dex_name = addr_routers.get(transaction.to)
    #         ds.gas = transaction.gas
    #         ds.gasPrice = transaction.gasPrice
    #         if 'maxFeePerGas' in transaction:
    #             ds.maxFeePerGas = transaction.maxFeePerGas
    #             ds.maxPriorityFeePerGas = transaction.maxPriorityFeePerGas
    #         print(ds.__dict__)
    #         print(f'================================================================')
    #         decoded_trx_input = codec.decode.function_input(transaction.input)
    #         print(decoded_trx_input)
    #         global_count += 1
    #         print(f'---------------------------------------------- {global_count} / {global_total} --------------------------------------------')
    # except TransactionNotFound:
    #     pass
    # except Exception as err:
    #     print(f'ERROR: {err}')
    #     print(type(err))
    


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)


def main():
    tx_filter = w3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(tx_filter, 1)))
    finally:
        loop.close()


if __name__ == '__main__':
    print(f'Run version: {version}')
    main()