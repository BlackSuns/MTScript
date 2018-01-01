from utils import print_log

from exchanges.qbtc import QbtcExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    qbtc = QbtcExchange()
    qbtc.post_result_batch()
    print_log('QBTC done...')

    print_log("all exchanges synced...")
