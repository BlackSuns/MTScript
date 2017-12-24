from exchanges.bithumb import BithumbExchange
from exchanges.bitflyer import BitflyerExchange
from exchanges.nereax import NeraexExchange
from exchanges.coinone import CoinoneExchange
from exchanges.korbit import KorbitExchange
from exchanges.quoine import QuoineExchange
from exchanges.qryptos import QryptosExchange
from exchanges.coincheck import CoincheckExchange
from exchanges.zaif import ZaifExchange
from exchanges.btcbox import BtcboxExchange
from exchanges.fisco import FiscoExchange

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

    qp = QryptosExchange()
    qp.post_result_batch()
    print_log('Qryptos done...')

    cc = CoincheckExchange()
    cc.post_result_batch()
    print_log('Coincheck done...')

    zf = ZaifExchange()
    zf.post_result_batch()
    print_log('Zaif done...')

    box = BtcboxExchange()
    box.post_result_batch()
    print_log('BTCBOX done...')

    fisco = FiscoExchange()
    fisco.post_result_batch()
    print_log('Fisco done...')

    print_log("all exchanges synced...")
