from utils import print_log
from exchanges.bcex import BcexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")
    be = BcexExchange()
    be.post_result_batch()

    print_log("BCEX Done...")
