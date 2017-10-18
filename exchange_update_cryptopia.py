from utils import print_log
from exchanges.cryptopia import CryptopiaExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    ct = CryptopiaExchange()
    ct.post_result_batch()
    print_log("Cryptopia done...")

    print_log("all exchanges synced...")
