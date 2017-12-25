from utils import print_log
from exchanges.bxinth import BxinthExchange
from exchanges.gemini import GeminiExchange
from exchanges.acx import AcxExchange
from exchanges.livecoin import LivecoinExchange
from exchanges.itbit import ItbitExchange
from exchanges.coinbene import CoinbeneExchange
from exchanges.kkex import KkexExchange
from exchanges.rightbtc import RightbtcExchange
from exchanges.bjex import BjexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    lc = LivecoinExchange()
    lc.post_result_batch()
    print_log("livecoin Done...")

    it = ItbitExchange()
    it.post_result_batch()
    print_log("Itbit Done...")

    bx = BxinthExchange()
    bx.post_result_batch()
    print_log("BX Tailand Done...")

    gm = GeminiExchange()
    gm.post_result_batch()
    print_log("Gemini Done...")

    acx = AcxExchange()
    acx.post_result_batch()
    print_log("ACX Done...")

    cb = CoinbeneExchange()
    cb.post_result_batch()
    print_log("Coinbene done...")

    kk = KkexExchange()
    kk.post_result_batch()
    print_log("KKEX done...")

    rbtc = RightbtcExchange()
    rbtc.post_result_batch()
    print_log("Rightbtc done...")

    bj = BjexExchange()
    bj.post_result_batch()
    print_log('bjex done...')

    print_log("all exchanges synced...")
