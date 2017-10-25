# import random

from utils import print_log
from exchanges.bitfinex import BitfinexExchange
# from exchanges.bitfinex_probe import BitfinexProbeExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")
    bf = BitfinexExchange()
    bf.post_result_batch()

    # if random.randint(0, 1000) < 5:
    #     bfp = BitfinexProbeExchange()
    #     bfp.post_result_batch()
    #     print_log("probed...")

    print_log("Bitfinex Done...")
