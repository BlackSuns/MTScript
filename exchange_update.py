from utils import print_log
from exchanges.liqui import LiquiExchange
from exchanges.bittrex import BittrexExchange
from exchanges.hitbtc import HitbtcExchange
from exchanges.poloniex import PoloniexExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    le = LiquiExchange()
    le.post_result()
    print_log("liqui done...")

    bt = BittrexExchange()
    bt.post_result()
    print_log("bittrex done...")

    hb = HitbtcExchange()
    hb.post_result()
    print_log("hitbtc done...")

    px = PoloniexExchange()
    px.post_result()
    print_log("poloniex done...")

    print_log("all exchanges synced...")
