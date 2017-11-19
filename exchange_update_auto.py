from utils import print_log
from exchanges.bxinth import BxinthExchange
from exchanges.gemini import GeminiExchange
from exchanges.acx import AcxExchange
from exchanges.livecoin import LivecoinExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    lc = LivecoinExchange()
    lc.post_result_batch()
    print_log("livecoin Done...")

    bx = BxinthExchange()
    bx.post_result_batch()
    print_log("BX Tailand Done...")

    gm = GeminiExchange()
    gm.post_result_batch()
    print_log("Gemini Done...")

    acx = AcxExchange()
    acx.post_result_batch()
    print_log("ACX Done...")

    print_log("all exchanges synced...")
