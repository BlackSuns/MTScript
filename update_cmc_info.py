import json
import os

import requests
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


def get_json_request(url):
    r = requests.get(url)

    if r.status_code == 200 and r.json()['code'] == 0:
        return r.json()['data']
    else:
        print('http code when getting: {}'.format(r.status_code))


def post_json_request(url, params):
    print(url)
    print(params)
    r = requests.post(url, data=params)

    if r.status_code == 200\
       and 'code' in r.json().keys()\
       and r.json()['code'] == 0\
       and r.json()['data']:
        # self.print_log(
        #     'post success: {symbol}/{anchor} on {market}'.format(
        #         symbol=params['symbol'],
        #         anchor=params['anchor'],
        #         market=self.exchange))
        return r.json()
    else:
        # print(params)
        error_info = "http code: {}".format(r.status_code)
        if r.status_code == 200:
            try:
                error_info += ' and server return error: {}'.format(
                    r.json())
            except:
                pass
        print_log(error_info)


def analysis_currency(currency_data):
    rd = []
    for cd in currency_data:
        jd = json.loads(cd[0].decode("utf-8"))

        # deal supplies
        for s in ('total_supply', 'max_supply', 'circulating_supply'):
            if s in jd.keys() and jd[s] != '-':
                jd[s] = translate_sp_str_to_number(jd[s])
            else:
                jd[s] = 0

        # deal media
        media_types = ('Website', 'Explorer', 'Announcement', 'Message Board')
        for m in jd['media']:
            if m[1] in media_types:
                key = str(m[1]).lower().replace(' ', '_')
                jd[key] = m[0]

        rd.append(jd)

    return rd


def get_currency_info(cnx):
    currencies = []

    sql = '''
            select result from cmc
    '''

    with cnx.cursor() as cursor:
        cursor.execute(sql)
        currencies = cursor.fetchall()

    return analysis_currency(currencies)


def filter_currency_param(currency):
    dealed_currency = {}
    params = ('name', 'symbol', 'cmc_url', 'logo', 'website',
              'explorer', 'announcement', 'message_board',
              'circulating_supply', 'total_supply', 'max_supply')

    for k in currency.keys():
        if k.lower() in params and currency[k]:
            dealed_currency[k] = currency[k]

    return dealed_currency


def format_com(com, exist_markets):
    market_id = None
    must_keys = ('markets', 'pair', 'price', 'volume')

    for k in must_keys:
        if k not in com.keys():
            return None

    # get market_id
    market_id = exist_markets.get(com['markets'], None)
    if not market_id:
        print_log('passed {}: not exist'.format(com['markets']))
        return None

    # get symbol / anchor
    (symbol, anchor) = com['pair'].split('/')
    if not symbol or not anchor:
        return None

    # get symbol 24h volume
    price = float(com['price'])
    volume = float(com['volume'])
    volume_symbol = 0
    if price > 0:
        volume_symbol = volume / price

    return {
        'market_id': market_id,
        'symbol': symbol,
        'anchor': anchor,
        'volume': volume_symbol,
    }


def translate_sp_str_to_number(str_number):
    str_number = str(str_number).split(' ')[0]
    t = str_number.replace(',', '')

    try:
        n = float(t)
    except:
        n = 0

    return n


def get_exist_markets():
    markets = {}
    remote_markets_url = '{}/market/marketlist?source=script'.format(BASE_URL)
    result = get_json_request(remote_markets_url)
    for m in result['list']:
        markets[m['name']] = m['id']

    return markets


def get_market_info(cnx, exist_markets):
    result = []
    sql = '''
            select result from cmc_markets
    '''

    with cnx.cursor() as cursor:
        cursor.execute(sql)
        markets = cursor.fetchall()

    for m in markets:
        try:
            jm = json.loads(m[0])
            name = jm['name']
            website = ''
            twitter = ''

            if name not in exist_markets:
                for media in jm['media']:
                    if str(media[0]).startswith('http'):
                        website = media[0]
                    if 'twitter' in str(media[0]):
                        twitter = media[0]

                result.append({
                    'name': jm['name'],
                    'cmc_url': jm['url'],
                    'website': website,
                    'twitter': twitter
                })
        except Exception as e:
            print_log(e)

    return result

if __name__ == '__main__':
    cnx = pymysql.connect(**get_mysql_conn_params('cmc_spider_db'))

    # update markets
    # markets = get_market_info(cnx, [])
    # markets_url = '{}/market/upsertmarket?source=script'.format(BASE_URL)
    # for m in markets:
    #     post_json_request(markets_url, m)

    # update currencies
    currencies = get_currency_info(cnx)
    exist_markets = get_exist_markets()
    currency_url = '{}/currency/upsertcurrency?source=script'.format(BASE_URL)
    com_url = '{}/currency/batchupsert'.format(BASE_URL)
    # for c in currencies:
    #     param = filter_currency_param(c)
    #     post_json_request(currency_url, param)

    for i in range(10):
        param = filter_currency_param(currencies[i])
        # post_json_request(currency_url, param)

        # com
        post_com_param = []
        for com in currencies[i]['markets']:
            com_param = format_com(com, exist_markets)
            if com_param:
                # print_log(com_param)
                post_com_param.append(com_param)
        post_json_request(com_url, {'json': json.dumps(post_com_param)})
