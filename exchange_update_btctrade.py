from utils import print_log
from exchanges.btctradeim import BtctradeimExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    bt = BtctradeimExchange()
    bt.post_result_batch()
    print_log("btctrade.im done...")

    print_log("all exchanges synced...")
