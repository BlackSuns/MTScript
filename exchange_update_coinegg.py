from utils import print_log
from exchanges.coinegg import CoineggExchange


if __name__ == '__main__':
    print_log("start sync exchanges...")

    egg = CoineggExchange()
    egg.post_result_batch()
    print_log("Coinegg done...")

    print_log("all exchanges synced...")
