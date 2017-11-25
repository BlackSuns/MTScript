from utils import print_log
from exchanges.coinexchange import CoinexchangeExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    cc = CoinexchangeExchange()
    cc.post_result_batch()
    print_log('coinexchange done...')
