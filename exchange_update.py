from exchanges.liqui import LiquiExchange
from exchanges.bittrex import BittrexExchange
from exchanges.hitbtc import HitbtcExchange


if __name__ == '__main__':
    le = LiquiExchange()
    le.post_result()
    bt = BittrexExchange()
    bt.post_result()
    hb = HitbtcExchange()
    hb.post_result()
