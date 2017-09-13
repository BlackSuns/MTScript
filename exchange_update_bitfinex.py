from utils import print_log
from exchanges.bitfinex import BitfinexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")
    bf = BitfinexExchange()
    bf.post_result()
