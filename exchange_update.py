from exchanges.liqui import LiquiExchange
from exchanges.bittrex import BittrexExchange


if __name__ == '__main__':
    le = LiquiExchange()
    le.post_result()
    bt = BittrexExchange()
    bt.post_result()
