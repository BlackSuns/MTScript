import json
import os

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
        5. use self.get_json_request to create connection, pass an url
           this function will return you the response if get correct response
        Done and try

        How to use:
        1. create an instance of some exchange object, pass a pymysql conn obj
        2. instance.update_database()
    '''

    BASE_PRICE_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/../tmp'

    def __init__(self, conn, exchange):
        super().__init__()
        self.conn = conn  # pymysql connection object
        self.exchange = exchange  # exchange name
        self.alias = ''
        self.update_time = 0  # when get price info, timestamp

        self.base_url = ''  # base url of api
        self.ticker_url = ''  # api to get ticker info

        self.support_pairs = []
        self.pairs = {}  # pair info, see update_pairs
        self.price_anchor_tmp = {}  # used for restore temp price of anchor
        self.price_history_file = '{}/{}.json'.format(
            self.BASE_PRICE_FOLDER, self.exchange)
        self.price_history = self.get_price_history()

        self.exchange_rate_USDCNY = self.get_USDCNY_rate()

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

    def update_pairs(self):
        ''' update pair info to self.pairs
            this function will do:
            1. part symbol and anchor
            2. calculate price_cny/price_usd
            3. calculate increase
            4. set update_type

            after this func, we will get our data ready in self.pairs
            in folling format:
            {
                "BTC/CNY": {
                   "symbol": "BTC",
                   "anchor": "CNY",
                   "price": 100.1,
                   "price_cny": 100.1,
                   "price_usd": 100.1,
                   "volume_24h": 4857293,
                   "volume_24h_cny": 100.1,
                   "volume_24h_usd": 100.1,
                   "increase": 0.1,
                   "update_type": 2,
                   "additional_val": {
                        "market_id": 1,
                        "currency_id": 1,
                   }
                   "update_time": 1501601719
                }
                ...
            }
        '''
        self.print_log('start request')
        self.pairs = {}
        remote_data = self.get_remote_data()
        self.print_log('remote exchange data got')

        if not remote_data and not isinstance(remote_data, list):
            raise RuntimeError(
                'illegal remote data found,'
                'check your get_remote_data implement')

        for item in remote_data:
            # get symbol and anchor
            pair = item['pair']
            price = self.format_price(item['price'])
            volume = item['volume']
            volume_anchor = item['volume_anchor']
            (symbol, anchor) = self.part_pair(pair)

            # get price and volume
            (anchor_rate_cny, anchor_rate_usd) = self.get_anchor_price(anchor)
            price_usd = self.format_price(price * anchor_rate_usd)
            price_cny = self.format_price(price * anchor_rate_cny)
            volume_usd = self.format_price(volume_anchor * anchor_rate_usd)
            volume_cny = self.format_price(volume_anchor * anchor_rate_cny)

            self.pairs[pair.upper()] = {
                "symbol": symbol,
                "anchor": anchor,
                "com_id": "{}_{}".format(symbol.lower(), anchor.lower()),
                "price": price,
                "price_cny": price_cny,
                "price_usd": price_usd,
                "volume_24h": volume,
                "volume_24h_cny": volume_cny,
                "volume_24h_usd": volume_usd,
            }

        # write increase
        self.print_log('check if needs to modify history file')
        self.write_price_history(remote_data)

        # get increase
        self.print_log('start calculate increase')
        self.calculate_increase()

        # get update info
        self.print_log('prepair for update')
        self.get_update_type()

    def update_database(self):
        self.update_pairs()
        mysql_update = '''
                update  currency_on_market
                set     price={price},
                        price_cny={price_cny},
                        price_usd={price_usd},
                        volume_24h={volume_24h},
                        volume_24h_cny={volume_24h_cny},
                        volume_24h_usd={volume_24h_usd},
                        percent_change_today={increase},
                        updated_at=unix_timestamp(now())
                where   market_name='{market_name}'
                and     pair='{pair}'
        '''

        mysql_insert = '''
                insert into currency_on_market
                            (
                                currency_id,
                                market_id,
                                market_name,
                                market_alias,
                                pair,
                                com_id,
                                currency,
                                anchor,
                                price,
                                price_cny,
                                price_usd,
                                volume_24h,
                                volume_24h_cny,
                                volume_24h_usd,
                                percent_change_today,
                                enabled,
                                created_at,
                                updated_at
                            )
                values      (
                                {currency_id},
                                {market_id},
                                '{market_name}',
                                '{market_alias}',
                                '{pair}',
                                '{com_id}',
                                '{currency}',
                                '{anchor}',
                                {price},
                                {price_cny},
                                {price_usd},
                                {volume_24h},
                                {volume_24h_cny},
                                {volume_24h_usd},
                                {percent_change_today},
                                {enabled},
                                unix_timestamp(now()),
                                unix_timestamp(now())
                            )
        '''

        self.print_log('start update')
        with self.conn.cursor() as cursor:
            for pair in self.pairs:
                item = self.pairs[pair]
                # update type 1
                # if market and pair found in currency_on_market, update it
                if item['update_type'] == 1:
                    cursor.execute(mysql_update.format(
                        price=item['price'],
                        price_cny=item['price_cny'],
                        price_usd=item['price_usd'],
                        volume_24h=item['volume_24h'],
                        volume_24h_cny=item['volume_24h_cny'],
                        volume_24h_usd=item['volume_24h_usd'],
                        increase=item['increase'],
                        market_name=self.exchange,
                        pair=pair
                    ))

                # update type 2
                # if market and symbol found, anchor not, create pair
                if item['update_type'] == 2:
                    cursor.execute(mysql_insert.format(
                        currency_id=item['additional_val']['currency_id'],
                        market_id=item['additional_val']['market_id'],
                        market_name=self.exchange,
                        market_alias=self.alias,
                        pair=pair,
                        com_id=item['com_id'],
                        currency=item['symbol'],
                        anchor=item['anchor'],
                        price=item['price'],
                        price_cny=item['price_cny'],
                        price_usd=item['price_usd'],
                        volume_24h=item['volume_24h'],
                        volume_24h_cny=item['volume_24h_cny'],
                        volume_24h_usd=item['volume_24h_usd'],
                        percent_change_today=item['increase'],
                        enabled=1,
                    ))

                # update type 3
                # if symbol not in table symbol, create symbol and create pair
                if item['update_type'] == 3:
                    cursor.execute(mysql_insert.format(
                        currency_id=item['additional_val']['currency_id'],
                        market_id=item['additional_val']['market_id'],
                        market_name=self.exchange,
                        market_alias=self.alias,
                        pair=pair,
                        com_id=item['com_id'],
                        currency=item['symbol'],
                        anchor=item['anchor'],
                        price=item['price'],
                        price_cny=item['price_cny'],
                        price_usd=item['price_usd'],
                        volume_24h=item['volume_24h'],
                        volume_24h_cny=item['volume_24h_cny'],
                        volume_24h_usd=item['volume_24h_usd'],
                        percent_change_today=item['increase'],
                        enabled=1,
                    ))
                    print(pair)
                    print(mysql_insert.format(
                        currency_id=item['additional_val']['currency_id'],
                        market_id=item['additional_val']['market_id'],
                        market_name=self.exchange,
                        market_alias=self.alias,
                        pair=pair,
                        com_id=item['com_id'],
                        currency=item['symbol'],
                        anchor=item['anchor'],
                        price=item['price'],
                        price_cny=item['price_cny'],
                        price_usd=item['price_usd'],
                        volume_24h=item['volume_24h'],
                        volume_24h_cny=item['volume_24h_cny'],
                        volume_24h_usd=item['volume_24h_usd'],
                        percent_change_today=item['increase'],
                        enabled=1,
                    ))

                # update type 4
                # if pair not found but symbol found, waiting for review
                if item['update_type'] == 4:
                    cursor.execute(mysql_insert.format(
                        currency_id=item['additional_val']['currency_id'],
                        market_id=item['additional_val']['market_id'],
                        market_name=self.exchange,
                        market_alias=self.alias,
                        pair=pair,
                        com_id=item['com_id'],
                        currency=item['symbol'],
                        anchor=item['anchor'],
                        price=item['price'],
                        price_cny=item['price_cny'],
                        price_usd=item['price_usd'],
                        volume_24h=item['volume_24h'],
                        volume_24h_cny=item['volume_24h_cny'],
                        volume_24h_usd=item['volume_24h_usd'],
                        percent_change_today=item['increase'],
                        enabled=0,
                    ))

            self.conn.commit()
        self.print_log('done!')

    def get_update_type(self):
        ''' check how we should deal data
            add an update_type in every self.pairs element
            update_type = 1: hit market and pair
            update_type = 2: hit market and symbol
            update_type = 3: symbol not in currency
            update_type = 4: symbol in currency
        '''

        # if you want to change column,
        # remember to check trans dict function below
        mysql_exchange = '''
            select  m.id market_id,
                    c.id currency_id,
                    c.name,
                    c.symbol,
                    com.pair,
                    com.anchor
            from    currency_on_market com
            inner   join market m on com.market_id=m.id
            inner   join currency c on c.id=com.currency_id
            where   m.name='{exchange}'
        '''.format(exchange=self.exchange)

        mysql_currency = '''
            select      id
            from        currency
            where       symbol='{symbol}'
            order by    id desc
        '''

        mysql_currency_insert = '''
                insert into currency
                            (
                                name,
                                symbol,
                                review_status,
                                enabled,
                                created_at,
                                updated_at
                            )
                SELECT      '{symbol}' as `name`,
                            '{symbol}' as `symbol`,
                            1 as `review_status`,
                            1 as `enabled`,
                            unix_timestamp(now()) as `created_at`,
                            unix_timestamp(now()) as `update_at`
                FROM        dual
                WHERE       not exists (
                SELECT      *
                FROM        currency
                WHERE       `symbol` = '{symbol}'
                )
        '''

        with self.conn.cursor() as cursor:
            cursor.execute(mysql_exchange)
            result = cursor.fetchall()

        # trans dict function
        # ensure all following data should work efficiently and correctly
        jr = []

        for row in result:
            jr.append({
                'market_id': row[0],
                'currency_id': row[1],
                'name': row[2],
                'symbol': row[3],
                'pair': row[4],
                'anchor': row[5],
            })

        # symbol_status used to cache symbol update status and additional_val
        # if pair can not match
        symbol_status = {}

        for pair in self.pairs.keys():
            item = self.pairs[pair]
            if self.in_dict_list(jr, 'pair', pair):
                item['update_type'] = 1
            else:
                # if symbol has been dealed and cached
                # use params directly
                if item['symbol'] in symbol_status.keys():
                    item['update_type'] = \
                        symbol_status[item['symbol']]['update_type']
                    item['additional_val'] = \
                        symbol_status[item['symbol']]['additional_val']
                # if symbel hasn't been dealed
                else:
                    sr = self.in_dict_list(
                        jr, 'symbol', item['symbol'])
                    if sr:
                        item['update_type'] = 2
                        item['additional_val'] = sr
                    else:
                        with self.conn.cursor() as cursor:
                            cursor.execute(mysql_currency_insert.format(
                                symbol=item['symbol']))
                            self.conn.commit()
                            if cursor.lastrowid > 0:
                                item['update_type'] = 3
                                item['additional_val'] = {
                                    'market_id': self.get_market_id(),
                                    'currency_id': cursor.lastrowid
                                }
                            else:
                                item['update_type'] = 4
                                cursor.execute(mysql_currency.format(
                                    symbol=item['symbol']))
                                result = cursor.fetchone()
                                if result is None:
                                    raise RuntimeError(
                                        'Not found symbol,'
                                        'somethong wrong happened')
                                item['additional_val'] = {
                                    'market_id': self.get_market_id(),
                                    'currency_id': result[0]
                                }
                    # cache dealed symbol
                    symbol_status[item['symbol']] = {
                            'update_type': item['update_type'],
                            'additional_val': item['additional_val']
                        }

            self.pairs[pair] = item

    def get_market_id(self):
        if hasattr(self, 'exchange_id') and self.exchange_id:
            return self.exchange_id

        if self.exchange:
            with self.conn.cursor() as cursor:
                mysql = '''
                    select id from market where name = '{}'
                '''.format(self.exchange)
                # print(mysql)
                cursor.execute(mysql)
                result = cursor.fetchone()
                if result:
                    self.exchange_id = result[0]
                    return result[0]
                else:
                    raise RuntimeError(
                        'market {} not found'.format(self.exchange))
        else:
            raise RuntimeError('not market name found')

    def get_anchor_price(self, anchor):
        ''' get a anchor price
        '''
        if anchor.upper() == 'RMB':
            return (1, round(1/self.exchange_rate_USDCNY*100, 2))

        if anchor.upper() == 'USD':
            return (self.exchange_rate_USDCNY/100, 1)

        if anchor not in self.price_anchor_tmp.keys():
            self.get_anchor_price_fromDB(anchor)

        return (self.price_anchor_tmp[anchor]['price_cny'],
                self.price_anchor_tmp[anchor]['price_usd'])

    def get_anchor_price_fromDB(self, anchor):
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

        with self.conn.cursor() as cursor:
            cursor.execute(mysql)
            result = cursor.fetchone()
            if result:
                if result[0]:
                    price_cny = float(result[0])
                if result[1]:
                    price_usd = float(result[1])

        if (price_cny == 0 and price_usd > 0):
            price_cny = price_usd * self.exchange_rate_USDCNY / 100

        if (price_cny > 0 and price_usd == 0):
            price_usd = price_cny / self.exchange_rate_USDCNY * 100

        self.price_anchor_tmp[anchor] = {
            'price_cny': price_cny,
            'price_usd': price_usd
        }

    def format_price(self, price):
        if price > 1:
            return round(price, 2)
        else:
            return round(price, 8)

    def get_price_history(self):
        ''' load price history
        executed when obj is init
        '''
        if not os.path.isdir(self.BASE_PRICE_FOLDER):
            os.mkdir(self.BASE_PRICE_FOLDER)
            return []

        if not os.path.isfile(self.price_history_file):
            return []

        with open(self.price_history_file, 'r') as f:
            ph = json.load(f)

        return ph

    def write_price_history(self, remote_data):
        ''' write price history if needed
            remote_data: [
                {
                    pair: pair,
                    price: price,
                    volume: volume,
                }
                ...
            ]

            price history format:
            [
               {
                  ts: timestamp,
                  pair1: price1,
                  pair2: price2,
                  ...
               }
               ...
            ]
        '''
        record_minute_span = 20  # do record from minute 0 - x every hour
        now = arrow.now().timestamp
        now_minute = arrow.now().minute

        if not os.path.isdir(self.BASE_PRICE_FOLDER):
            os.mkdir(self.BASE_PRICE_FOLDER)

        if now_minute < record_minute_span:
            if (len(self.price_history) == 0) or \
               (self.price_history[-1]['ts'] < now - record_minute_span * 60):
                # generate dictionary to write
                ph = {'ts': now}
                for data in remote_data:
                    ph[data['pair']] = data['price']

                # push
                self.price_history.append(ph)
                self.print_log('a price history added')

                # remove time out records
                available_index = 0
                remove_ts = 0
                for i, history in enumerate(self.price_history):
                    if history['ts'] > now - 60 * 60 * 24:
                        available_index = i
                        break
                    else:
                        remove_ts = history['ts']

                if remove_ts > 0:
                    self.print_log('remove price history before {}'.format(
                        arrow.get(remove_ts)))
                self.price_history = self.price_history[available_index:]
                with open(self.price_history_file, 'w') as f:
                    json.dump(self.price_history, f, indent=4)

    def calculate_increase(self):
        ''' get today's base price to calculate current increase

        '''

        # define which price should be available
        # first item is not earlier than
        # second id not later than
        # unit is hour
        compare_span = (25, 1)
        now = arrow.now().timestamp
        ts_target = now - 3600 * 24
        ts_bottom = now - 3600 * compare_span[0]
        ts_top = now - 3600 * compare_span[1]
        ts_diff = ts_bottom

        # get 1st object and check if it can be the base
        base_item = {}
        for history in self.price_history:
            if history['ts'] < ts_top and history['ts'] > ts_bottom and \
                    history['ts'] - ts_target < ts_diff:
                base_item = history
                ts_diff = history['ts'] - ts_target

            if history['ts'] > ts_top:
                break

        # try to read a pair price and cal increase, while cann't, return 0
        if base_item:
            self.print_log('base item got, recorded at {}'.format(
                arrow.get(base_item['ts'])))
            for pair in self.pairs.keys():
                if pair in base_item.keys():
                    price_before = base_item[pair]
                    price_now = self.pairs[pair]['price']
                    self.pairs[pair]['increase'] = \
                        round((price_now - price_before) / price_before * 100,
                              2)
                else:
                    self.pairs[pair]['increase'] = 0
        else:
            print('none base item loaded')
            for pair in self.pairs.keys():
                self.pairs[pair]['increase'] = 0

    def in_dict_list(self, dict_list, key, val):
        ''' check if val in one of dictionary list's key value
            return the entire dict if hit
            return None if not hit
        '''
        for dict_item in dict_list:
            if val == dict_item[key]:
                return dict_item

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
        with self.conn.cursor() as cursor:
            cursor.execute(mysql)
            result = cursor.fetchone()
            if result:
                return float(result[0])
            else:
                return 665

    def get_json_request(self, url):
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            print('someting wrong and return http code: {}'.format(
                r.status_code))

    def print_log(self, message, m_type='INFO'):
        m_types = ('INFO', 'WARNING', 'ERROR')
        prefix = '[exchange {}][ {} ]'.format(
            self.exchange, arrow.now().format('YYYY-MM-DD HH:mm:ss:SSS'))
        if str(m_type).upper() in m_types:
            m_type = str(m_type).upper()
        else:
            raise RuntimeError('Invalid log type: {}'.format(m_type))

        print('{} -{}- {}'.format(prefix, m_type, message))
