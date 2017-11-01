from utils import print_log
from exchanges.cex import CexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    cex = CexExchange()
    cex.post_result_batch()
    print_log("cex done...")

    print_log("all exchanges synced...")
