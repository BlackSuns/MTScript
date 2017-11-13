import json
import os

import arrow
import pymysql

from utils import print_log, get_config

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'
BASE_URL = get_config(
    CONFIG_PATH, 'exchange_settings', {'base_url': 'string'})['base_url']


def get_mysql_conn_params(section):
    return get_config(CONFIG_PATH, section, {
        'host':       'string',
        'port':       'int',
        'user':       'string',
        'password':   'string',
        'db':         'string',
    })


def get_float(string):
    try:
        return float(string)
    except:
        return 0


def get_last_ts(cnx_tmp, currency, symbol):
    sql = '''
        select max(timestamp) from kline
        where currency='{}' and symbol='{}'
    '''.format(currency, symbol)

    with cnx_tmp.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchone()

    if result[0]:
        return result[0]
    else:
        return 0


def deal_k_data(cnx, cnx_tmp):
    sql = '''
            select result from cmc_k
    '''

    with cnx.cursor() as cursor:
        cursor.execute(sql)
        cmc_k = cursor.fetchall()

    for i, k in enumerate(cmc_k, 1):
        try:
            jk = json.loads(k[0])
            currency = jk['name']
            symbol = jk['symbol']
            last_ts = get_last_ts(cnx_tmp, currency, symbol)

            print_log('dealing {}/{}: {}'.format(i, len(cmc_k), currency))
            batch_value = []
            for kdate in jk['k']:
                d = arrow.get(kdate[0], 'MMM DD, YYYY')
                update_at = arrow.now().timestamp
                if d.timestamp > last_ts:
                    batch_value.append(
                        "('{}', '{}', '{}', {}, "
                        "{}, {}, {}, {}, {}, {}, {}, {})".format(
                            currency, symbol, d.format('YYYY-MM-DD'),
                            d.timestamp,
                            get_float(kdate[1]),
                            get_float(kdate[2]),
                            get_float(kdate[3]),
                            get_float(kdate[4]),
                            get_float(kdate[5]),
                            get_float(kdate[6]),
                            update_at, update_at))
                else:
                    break

            if batch_value:
                insert_sql = '''
                    insert into kline
                           (`currency`, `symbol`, `date`, `timestamp`,
                            `open`, `high`, `low`, `close`, `volume`,
                            `marketcap`, `created_at`, `updated_at`)
                    values
                           {}
                '''.format(', '.join(batch_value))

                # print(insert_sql)
                with cnx_tmp.cursor() as cursor:
                    cursor.execute(insert_sql)

        except Exception as e:
            print_log(e)

    cnx_tmp.commit()


if __name__ == '__main__':
    cnx = pymysql.connect(**get_mysql_conn_params('cmc_spider_db'))
    cnx_tmp = pymysql.connect(**get_mysql_conn_params('temp_db'))

    deal_k_data(cnx, cnx_tmp)
