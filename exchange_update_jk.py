from exchanges.bithumb import BithumbExchange
from exchanges.bitflyer import BitflyerExchange
from exchanges.nereax import NeraexExchange

from utils import print_log


if __name__ == '__main__':
    print_log("start sync exchanges...")

    bh = BithumbExchange()
    bh.post_result_batch()
    print_log("Bithumb done...")

    bf = BitflyerExchange()
    bf.post_result_batch()
    print_log("bitFlyer done...")

    nx = NeraexExchange()
    nx.post_result_batch()
    print_log('Nereax done...')

    print_log("all exchanges synced...")
