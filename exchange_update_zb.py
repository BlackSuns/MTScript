from utils import print_log
from exchanges.zb import ZbExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    zb = ZbExchange()
    zb.post_result_batch()
    print_log("ZB done...")

    print_log("all exchanges synced...")
