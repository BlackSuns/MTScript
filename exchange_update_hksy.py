from utils import print_log

from exchanges.hksy import HksyExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    hksy = HksyExchange()
    hksy.post_result_batch()
    print_log('HKSY done...')

    print_log("all exchanges synced...")
