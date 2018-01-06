from utils import print_log
from exchanges.coinw import CoinwExchange

if __name__ == '__main__':
    print_log("start sync exchanges...")

    cw = CoinwExchange()
    cw.post_result_batch()
    print_log('Coinw Pro done...')

    print_log("all exchanges synced...")
