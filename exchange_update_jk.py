from exchanges.bithumb import BithumbExchange
from exchanges.bitflyer import BitflyerExchange
from exchanges.nereax import NeraexExchange
from exchanges.coinone import CoinoneExchange
from exchanges.korbit import KorbitExchange

from utils import print_log


if __name__ == '__main__':
    print_log("start sync exchanges...")

    bh = BithumbExchange()
    bh.post_result_batch()
    print_log("Bithumb done...")

    bf = BitflyerExchange()
    bf.post_result_batch()
    print_log("bitFlyer done...")

    co = CoinoneExchange()
    co.post_result_batch()
    print_log('Coinone done...')

    nx = NeraexExchange()
    nx.post_result_batch()
    print_log('Nereax done...')

    kb = KorbitExchange()
    kb.post_result_batch()
    print_log('Korbit done...')

    print_log("all exchanges synced...")
