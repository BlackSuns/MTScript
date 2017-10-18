from utils import print_log
from exchanges.coinnest import CoinnestExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    cn = CoinnestExchange()
    cn.post_result_batch()
    print_log('Coinnest done...')
