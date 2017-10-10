from utils import print_log

from exchanges.kraken import KrakenExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    kn = KrakenExchange()
    kn.post_result_batch()
    print_log('Kraken done...')

    print_log("all exchanges synced...")
