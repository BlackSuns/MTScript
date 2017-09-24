from utils import print_log
from exchanges.coinmarketcap import CmcExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    cmc = CmcExchange()
    cmc.post_result_batch()
    print_log("cmc done...")

    print_log("all exchanges synced...")
