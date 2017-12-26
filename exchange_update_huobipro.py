from utils import print_log
from exchanges.huobi import HuobiExchange

if __name__ == '__main__':
    print_log("start sync exchanges...")

    hb = HuobiExchange()
    hb.post_result_batch()
    print_log('Huobi Pro done...')

    print_log("all exchanges synced...")
