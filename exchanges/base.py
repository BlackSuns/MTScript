import os
from configparser import ConfigParser

import arrow
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


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

        self.price_anchor_tmp = {}  # used for restore temp price of anchor
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
        s = requests.Session()
        s.mount('https://', MyAdapter())
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            self.print_log('someting wrong and return http code: {}'.format(
                r.status_code))

    def post_json_request(self, url, params):
        r = requests.post(url, data=params)

        if r.status_code == 200 and r.json()['code'] == 0\
           and r.json()['data']['result']:
            # self.print_log(
            #     'post success: {symbol}/{anchor} on {market}'.format(
            #         symbol=params['symbol'],
            #         anchor=params['anchor'],
            #         market=self.exchange))
            return r.json()
        else:
            error_info = "someting wrong when dealing {}/{}"\
                         " and return http code: {}".format(
                            params['symbol'],
                            params['anchor'],
                            r.status_code)
            if r.status_code == 200:
                try:
                    error_info += ' and server return error: {}'.format(
                        r.json())
                except:
                    pass
            self.print_log(error_info)

    def post_result(self):
        host = 'http://internal.mytoken.iknowapp.com:12306'
        endpoint = '/currency/upsertcurrencyonmarket'

        request_url = '{host}{endpoint}'.format(
            host=host, endpoint=endpoint)

        remote_data = self.get_remote_data()
        for data in remote_data:
            (symbol, anchor) = self.part_pair(data['pair'])
            price = data['price']
            volume_anchor = data['volume_anchor']

            params = {
                'symbol': symbol,
                'market_id': self.exchange_id,
                'anchor': anchor,
                'price': price,
                'volume_24h': volume_anchor,
            }

            # print(request_url)
            # print(params)
            self.post_json_request(request_url, params)
            # self.print_log(result)

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
