from utils import print_log
from exchanges.huobi import HuobiExchange
from exchanges.okex import OkexExchange

if __name__ == '__main__':
    print_log("start sync exchanges...")

    hb = HuobiExchange()
    hb.post_result_batch()
    print_log('Huobi Pro done...')

    ok = OkexExchange()
    ok.post_result_batch()
    print_log('OKEX done...')

    print_log("all exchanges synced...")
