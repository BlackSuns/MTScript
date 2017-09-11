import json
import os
import hashlib
from configparser import ConfigParser

import pymysql
import arrow
import requests


class BaseExchange(object):
    ''' This is Base Exchange Object to pull currency data from exchanges
        and record them in database

        Most important func here is update_pairs and update_database

        If you want to add a exchange, inherit this object and do:
        1. create a __init__ func and request a pymysql connection param
        2. do super().__init__(conn, your_exchange_name) in your __init__
           conn is the pymysql connection param metioned above
        3. overload your base_url, ticker_url, and alias if needs, in __init__
        4. overload get_remote_data func, remember to return a list include
           elements like {pair: xx, price: xxx, volume: xxx, volume_anchor: xx}
        5. if a pair use an assigned com_id, override self.assigned_com_id
           with format {pair1: com_id1, pair2_com_id2}
        5. use self.get_json_request to create connection, pass an url
           this function will return you the response if get correct response
        Done and try

        How to use:
        1. create an instance of some exchange object, pass a pymysql conn obj
        2. instance.update_database()
    '''
    CONFIG_PATH = os.path.abspath(
        os.path.dirname(__file__)) + '/../script.conf'
    CONFIG_SECTION = 'cmc_data_db'

    def __init__(self):
        super().__init__()
        self.exchange = ''
        self.exchange_id = 0
        self.cnx = pymysql.connect(**self.get_config())

        self.price_anchor_tmp = {}  # used for restore temp price of anchor
        self.exchange_rate_USDCNY = self.get_USDCNY_rate()
        self.assigned_com_id = {}

    def get_remote_data(self):
        ''' get data from markets and return value
            this function should be implemented in extend classes

            return value:
            [
                {
                    pair: 'OMG/ETH',
                    price: 0.03456,
                    volume: 2036,  # volume of symbol
                    volume_cur: 56,  # volume of anchor
                }
                ...
            ]
            e.g.
            pair symbols should be in capital
        '''
        raise NotImplementedError("You should implement this")

    def get_json_request(self, url):
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            self.print_log('someting wrong and return http code: {}'.format(
                r.status_code))

    def post_json_request(self, url, params):
        r = requests.post(url, data=params)

        if r.status_code == 200:
            self.print_log('post success')
            return r.json()
        else:
            self.print_log('someting wrong and return http code: {}'.format(
                r.status_code))

    def post_result(self):
        host = 'http://internal.mytoken.iknowapp.com:12306'
        endpoint = '/currency/upsertcurrencyonmarket'
        # ts = arrow.now().timestamp
        # key = 'thalesky_eos_'
        # secret = hashlib.md5('{}{}'.format(key, ts)
        #                            .encode(encoding='utf-8')).hexdigest()
        request_url = '{host}{endpoint}'.format(
            host=host, endpoint=endpoint)

        remote_data = self.get_remote_data()[0]
        (symbol, anchor) = self.part_pair(remote_data['pair'])
        price = remote_data['price']
        volume_anchor = remote_data['volume_anchor']
        # get price and volume
        (anchor_rate_cny, anchor_rate_usd) = self.get_anchor_fiat_price(anchor)
        price_usd = self.format_price(price * anchor_rate_usd)
        price_cny = self.format_price(price * anchor_rate_cny)
        volume_usd = self.format_price(volume_anchor * anchor_rate_usd)
        volume_cny = self.format_price(volume_anchor * anchor_rate_cny)

        params = {
            'symbol': symbol,
            'market_id': self.exchange_id,
            'anchor': anchor,
            'price_cny': price_cny,
            'price': price,
            'price_usd': price_usd,
            'volume_24h': volume_anchor,
            'volume_24h_cny': volume_cny,
            'volume_24h_usd': volume_usd,
        }

        # result = self.post_json_request(request_url, params)
        # self.print_log(result)
        print(request_url)
        print(params)

    def print_log(self, message, m_type='INFO'):
        m_types = ('INFO', 'WARNING', 'ERROR')
        prefix = '[exchange {}][ {} ]'.format(
            self.exchange, arrow.now().format('YYYY-MM-DD HH:mm:ss:SSS'))
        if str(m_type).upper() in m_types:
            m_type = str(m_type).upper()
        else:
            raise RuntimeError('Invalid log type: {}'.format(m_type))

        print('{} -{}- {}'.format(prefix, m_type, message))

    def get_config(self):
        args = {
            'host':       'string',
            'port':       'int',
            'user':       'string',
            'password':   'string',
            'db':         'string',
        }
        config = ConfigParser()
        config.read(self.CONFIG_PATH)

        if config.has_section(self.CONFIG_SECTION):
            dictdata = {}
            for arg, argtype in args.items():
                try:
                    if argtype == 'int':
                        dictdata[arg] = config.getint(
                            self.CONFIG_SECTION, arg)
                    elif argtype == 'float':
                        dictdata[arg] = config.getfloat(
                            self.CONFIG_SECTION, arg)
                    elif argtype == 'boolean':
                        dictdata[arg] = config.getboolean(
                            self.CONFIG_SECTION, arg)
                    else:
                        dictdata[arg] = config.get(
                            self.CONFIG_SECTION, arg)
                except:
                    dictdata[arg] = None

            return dictdata
        else:
            return None

    def part_pair(self, pair):
        ''' part a pair to (symbol, anchor)
        return (None, None) if illegal format
        '''
        result = str(pair).split('/')
        if len(result) == 2:
            return result
        else:
            raise RuntimeError('not valid pair: {}'.format(pair))

    def format_price(self, price):
        if price > 1:
            return round(price, 2)
        else:
            return round(price, 8)

    def get_anchor_fiat_price(self, anchor):
        ''' get an anchor's fiat price
            return (RMB_price, USD_price)
        '''
        if anchor.upper() == 'RMB':
            return (1, round(1/self.exchange_rate_USDCNY, 2))

        if anchor.upper() in ('USD', 'USDT'):
            return (self.exchange_rate_USDCNY, 1)

        if anchor not in self.price_anchor_tmp.keys():
            self.get_anchor_fiat_price_fromDB(anchor)

        return (self.price_anchor_tmp[anchor]['price_cny'],
                self.price_anchor_tmp[anchor]['price_usd'])

    def get_anchor_fiat_price_fromDB(self, anchor):
        ''' get a anchor price in cmc market from database
        set price_cny, price_usd to self.price_anchor_tmp
        price will be 0 if not recorded
        remember ask self.price_anchor_tmp for price first,
        if no record, try this
        '''
        price_cny = 0
        price_usd = 0
        mysql = '''
                select      com.price_cny,
                            com.price_usd
                from        currency_on_market com
                inner join  currency c on com.currency_id=c.id
                where       com.market_id=1303
                and         c.symbol='{}'
        '''.format(anchor)

        with self.cnx.cursor() as cursor:
            cursor.execute(mysql)
            result = cursor.fetchone()
            if result:
                if result[0]:
                    price_cny = float(result[0])
                if result[1]:
                    price_usd = float(result[1])

        if (price_cny == 0 and price_usd > 0):
            price_cny = price_usd * self.exchange_rate_USDCNY

        if (price_cny > 0 and price_usd == 0):
            price_usd = price_cny / self.exchange_rate_USDCNY

        self.price_anchor_tmp[anchor] = {
            'price_cny': price_cny,
            'price_usd': price_usd
        }

    def get_USDCNY_rate(self):
        ''' return a usd/cny rate from db
            this value is how much rmb should be exchange of 100 usd
        '''
        mysql = '''
            select  config_value
            from    system_config
            where   config='usdcny_rate'
            and     enabled=1
        '''
        with self.cnx.cursor() as cursor:
            cursor.execute(mysql)
            result = cursor.fetchone()
            if result:
                return float(result[0])
            else:
                return 6.65
