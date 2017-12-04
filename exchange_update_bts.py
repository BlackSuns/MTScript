from utils import print_log
from exchanges.bts import BtsExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    bts = BtsExchange()
    bts.post_result_batch()
    print_log("BTS done...")

    print_log("all exchanges synced...")
