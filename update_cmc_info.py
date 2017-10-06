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
    # print(url)
    r = requests.get(url)

    if r.status_code == 200 and r.json()['code'] == 0:
        return r.json()['data']
    else:
        print('http code when getting: {}'.format(r.status_code))


def post_json_request(url, params):
    # print(url)
    # print(params)
    r = requests.post(url, data=params)

    try:
        if r.status_code == 200\
           and 'code' in r.json().keys()\
           and r.json()['code'] == 0\
           and 'data' in r.json().keys()\
           and r.json()['data']\
           and 'false' not in r.text:
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
    except Exception as e:
        print_log(e)


def analysis_currency(currency_data):
    rd = []
    for cd in currency_data:
        jd = json.loads(cd[0].decode("utf-8"))
        if 'name' in jd.keys() and 'symbol' in jd.keys()\
                and jd['name'] and jd['symbol']:
            # deal supplies
            for s in ('total_supply', 'max_supply', 'circulating_supply'):
                if s in jd.keys() and jd[s] != '-':
                    jd[s] = translate_sp_str_to_number(jd[s])
                else:
                    jd[s] = 0

            # deal media
            media_types = ('Website', 'Explorer',
                           'Announcement', 'Message Board')
            for m in jd['media']:
                if m[1] in media_types:
                    key = str(m[1]).lower().replace(' ', '_')
                    jd[key] = m[0]

            rd.append(jd)
        else:
            print_log('error found, no name or symbol:'
                      ' name is {}, symbol is {}'.format(
                        jd.get('name', None), jd.get('symbol', None)))
            print_log(jd['url'])

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
            if k == 'circulating_supply':
                dealed_currency['available_supply'] = currency[k]
            else:
                dealed_currency[k] = currency[k]

    return dealed_currency


def format_com(com, currency, exist_markets):
    market_id = None
    must_keys = ('market', 'pair', 'price', 'volume')

    for k in must_keys:
        if k not in com.keys():
            return None

    # get symbol / anchor
    (symbol, anchor) = com['pair'].split('/')
    if not symbol or not anchor:
        return None

    # get market_id
    market_id = exist_markets.get(com['market'], None)
    if not market_id:
        print_log('passed {}: not exist'.format(com['market']))
        return None

    volume = float(com['volume'])

    return {
        'name': currency,
        'market_id': market_id,
        'symbol': symbol,
        'anchor': anchor,
        'volume_24h_usd': volume,
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
    exist_markets = get_exist_markets()
    markets = get_market_info(cnx, exist_markets)
    markets_url = '{}/market/upsertmarket?source=script'.format(BASE_URL)
    for m in markets:
        post_json_request(markets_url, m)

    print_log('market done')

    # update currencies
    currencies = get_currency_info(cnx)
    exist_markets = get_exist_markets()
    currency_url = '{}/currency/upsertcurrency?source=script'.format(BASE_URL)
    com_url = '{}/currency/batchupsert'.format(BASE_URL)

    for c in currencies:
        print_log('dealing {}/{}'.format(c['name'], c['symbol']))
        # currency
        param = filter_currency_param(c)
        post_json_request(currency_url, param)

        # com
        post_com_param = []
        for com in c['markets']:
            if not str(com['pair']).endswith(c['symbol']):
                com_param = format_com(com, c['name'], exist_markets)
                if com_param:
                    # print_log(com_param)
                    post_com_param.append(com_param)
        post_json_request(com_url, {'json': json.dumps(post_com_param)})

    # for i in range(9, 10):
    #     param = filter_currency_param(currencies[i])
    #     post_json_request(currency_url, param)

        # com
            # post_com_param = []
            # for com in currencies[i]['markets']:
            #     com_param = format_com(com, currencies[i]['name'], exist_markets)
            #     if com_param:
            #         # print_log(com_param)
            #         post_com_param.append(com_param)
            # post_json_request(com_url, {'json': json.dumps(post_com_param)})
