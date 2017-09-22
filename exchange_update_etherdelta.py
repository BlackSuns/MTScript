from utils import print_log
from exchanges.etherdelta import EtherdeltaExchange

if __name__ == '__main__':
    print_log("start sync exchanges...")
    ed = EtherdeltaExchange()
    ed.post_result_batch()
    print_log("all exchanges synced...")
