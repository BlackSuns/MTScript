from utils import print_log
from exchanges.allcoin import AllcoinExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")
    ac = AllcoinExchange()
    ac.post_result_batch()

    print_log("Allcoin Done...")
