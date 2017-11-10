from exchanges.bithumb import BithumbExchange
from exchanges.bitflyer import BitflyerExchange
from exchanges.nereax import NeraexExchange
from exchanges.coinone import CoinoneExchange
from exchanges.korbit import KorbitExchange
from exchanges.quoine import QuoineExchange
from exchanges.coincheck import CoincheckExchange
from exchanges.zaif import ZaifExchange

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

    qe = QuoineExchange()
    qe.post_result_batch()
    print_log('Quoine done...')

    cc = CoincheckExchange()
    cc.post_result_batch()
    print_log('Coincheck done...')

    zf = ZaifExchange()
    zf.post_result_batch()
    print_log('Zaif done...')

    print_log("all exchanges synced...")
