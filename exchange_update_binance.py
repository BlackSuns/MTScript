from utils import print_log
from exchanges.binance import BinanceExchange

if __name__ == '__main__':
    print_log("start sync exchanges...")
    bn = BinanceExchange()
    bn.post_result_batch()
    print_log("all exchanges synced...")
