from utils import print_log
from exchanges.jex import JexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    jex = JexExchange()
    jex.post_result_batch()
    print_log("JEX done...")

    print_log("all exchanges synced...")
