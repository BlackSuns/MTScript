from utils import print_log
from exchanges.binance import BinanceExchange
from exchanges.gateio import GateioExchange
from exchanges.kucoin import KucoinExchange
from exchanges.aex import AexExchange
from exchanges.ceo import CeoExchange
from exchanges.coinegg import CoineggExchange
from exchanges.exx import ExxExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

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

    print_log("all exchanges synced...")
