from utils import print_log
from exchanges.chaoex import ChaoexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    ce = ChaoexExchange()
    ce.post_result_batch()
    print_log("Chaoex done...")

    print_log("all exchanges synced...")
