from utils import print_log
from exchanges.binance import BinanceExchange
from exchanges.gateio import GateioExchange
from exchanges.kucoin import KucoinExchange
from exchanges.aex import AexExchange
from exchanges.ceo import CeoExchange
from exchanges.coinegg import CoineggExchange
from exchanges.exx import ExxExchange
from exchanges.uncoinex import UncoinexExchange
from exchanges.ucx import UcxExchange
from exchanges.bibox import BiboxExchange
from exchanges.coin900 import Coin900Exchange
from exchanges.lbank import LbankExchange
from exchanges.hib8 import Hib8Exchange
from exchanges.coinw import CoinwExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    bx = BiboxExchange()
    bx.post_result_batch()
    print_log("Bibox done...")

    bn = BinanceExchange()
    bn.post_result_batch()
    print_log("Binance done...")

    gt = GateioExchange()
    gt.post_result_batch()
    print_log("Gate.io done...")

    kc = KucoinExchange()
    kc.post_result_batch()
    print_log("Kucoin done...")

    aex = AexExchange()
    aex.post_result_batch()
    print_log("AEX done...")

    ceo = CeoExchange()
    ceo.post_result_batch()
    print_log("CEO done...")

    egg = CoineggExchange()
    egg.post_result_batch()
    print_log("Coinegg done...")

    exx = ExxExchange()
    exx.post_result_batch()
    print_log("Exx done...")

    uc = UncoinexExchange()
    uc.post_result_batch()
    print_log("Uncoinex done...")

    ucx = UcxExchange()
    ucx.post_result_batch()
    print_log("UCX done...")

    ce = Coin900Exchange()
    ce.post_result_batch()
    print_log("Coin900 done...")

    lb = LbankExchange()
    lb.post_result_batch()
    print_log("Lbank done...")

    h8 = Hib8Exchange()
    h8.post_result_batch()
    print_log("Hib8 done...")

    cw = CoinwExchange()
    cw.post_result_batch()
    print_log("Coinw done...")

    print_log("all exchanges synced...")
