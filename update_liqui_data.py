import os

import pymysql

from exchanges.liqui import LiquiExchange
from utils import print_log, get_config


CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'


def get_mysql_conn_params(section):
    return get_config(CONFIG_PATH, section, {
        'host':       'string',
        'port':       'int',
        'user':       'string',
        'password':   'string',
        'db':         'string',
    })

if __name__ == '__main__':
    conn_data = pymysql.connect(**get_mysql_conn_params('cmc_data_db'))
    le = LiquiExchange(conn_data)
    le.update_database()
