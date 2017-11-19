from utils import print_log
from exchanges.bxinth import BxinthExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    bx = BxinthExchange()
    bx.post_result_batch()
    print_log("BX Tailand Done...")

    print_log("all exchanges synced...")
