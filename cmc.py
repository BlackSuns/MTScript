import json
import os
import re

import pymysql

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


def get_spider_data(conn):
    market_data = get_spider_results(conn, 'cmc_markets')
    currency_data = get_spider_results(conn, 'cmc')

    return {
        'markets': analysis_market(market_data),
        'currencies': analysis_currency(currency_data),
    }


# return format:
# {
#   OkCoin Intl.': {
#     'url': 'https://coinmarketcap.com/exchanges/okcoin-intl/',
#     'name': 'OkCoin Intl.',
#     'media': [['https://www.okcoin.com', 'https://www.okcoin.com'],
#               ['https://twitter.com/OKCoinBTC', '@OKCoinBTC']]
#   },
#   ...
# }
def analysis_market(market_data):
    rd = {}
    for md in market_data:
        jd = json.loads(md[1].decode("utf-8"))
        rd[jd['name']] = jd

    return rd


# return format:
# {
#   Patientory: {
#     'url': 'https://coinmarketcap.com/assets/patientory/',
#     'name': 'Patientory (PTOY)',
#     'logo': 'https://files.coinmarketcap.com/static/img/coins/32x32/patientory.png',
#     'media': [['https://patientory.com/', 'Website'],
#               ['https://ethplorer.io/address/0x8ae4bf2c33a8e667de34b54938b0ccd03eb8cc06', 'Explorer'],
#               ['https://etherscan.io/token/0x8ae4bf2c33a8e667de34b54938b0ccd03eb8cc06', 'Explorer 2'],
#               ['https://bitcointalk.org/index.php?topic=1886446.0', 'Announcement']],
#     'markets': [{'market_url': 'https://coinmarketcap.com/exchanges/bittrex/', 'markets': 'Bittrex', 'pair': 'PTOY/BTC'},
#                 {'market_url': 'https://coinmarketcap.com/exchanges/liqui/', 'markets': 'Liqui', 'pair': 'PTOY/BTC'},
#                 {'market_url': 'https://coinmarketcap.com/exchanges/liqui/', 'markets': 'Liqui', 'pair': 'PTOY/ETH'},
#                 ...}],
#     'currency': 'Patientory',
#     'symbol': 'PTOY'
#   },
#   ...
# }
def analysis_currency(currency_data):
    pattern = r'[(]\w+[)]'
    rd = {}
    for cd in currency_data:
        jd = json.loads(cd[1].decode("utf-8"))
        results = [
            (m.start(), m.end()) for m in re.finditer(pattern, jd['name'])]
        if results:
            (start, end) = results[-1]
            jd['currency'] = jd['name'][:start].strip()
            jd['symbol'] = jd['name'][start+1:end-1].strip()
        # search = re.search(pattern, jd['name'])
        # if search:
        #     jd['currency'] = jd['name'][:search.start()].strip()
        #     jd['symbol'] = jd['name'][search.start()+1:search.end()-1].strip()
        else:
            jd['currency'] = jd['name'].strip()
            jd['symbol'] = jd['name'].strip()
        if ('total_supply' in jd.keys()):
            jd['max_supply'] = translate_sp_str_to_number(jd['total_supply'])
        rd[jd['name']] = jd

    return rd


def translate_sp_str_to_number(str_number):
    str_number = str(str_number).split(' ')[0]
    t = str_number.split(',')
    n = ''
    for i in t:
        n += i
    try:
        n = int(n)
    except:
        n = 0

    return n


def get_exist_currencies(conn):
    # 由于在update currency时， 要确保只更新空值的link字段，所以不能只取id
    # 如果要更改这里取出来的字段，相印的需要检查update_currency_basic_info中
    # 数据存在时的update代码
    mysql = '''
        select  id,
                name,
                symbol,
                enabled,
                cmc_url,
                website,
                explorer,
                announcement,
                message_board
          from  currency
    '''

    with conn.cursor() as cursor:
        cursor.execute(mysql)
        currencies = cursor.fetchall()

    rd = []
    for c in currencies:
        rd.append({
            'id': c[0],
            'name': c[1].strip(),
            'symbol': c[2].strip(),
            'currency': '{} ({})'.format(c[1].strip(), c[2].strip()),
            'enabled': c[3],
            'cmc_url': c[4],
            'website': c[5],
            'explorer': c[6],
            'announcement': c[7],
            'message_board': c[8]
        })

    return rd


def get_exist_markets(conn):
    mysql = '''
        select  id,
                name
          from  market
    '''

    with conn.cursor() as cursor:
        cursor.execute(mysql)
        markets = cursor.fetchall()

    rd = {}
    for m in markets:
        rd[m[1]] = m[0]

    return rd


def update_currency_basic_info(currency_data, conn_data, exist_currencies):
    # 由于在update currency时， 要确保只更新空值的link字段，所以这里不用on duplicate key
    # 的写法，分为insert 和 update两个语句执行，比较复杂
    inerst_sql_str = '''
         INSERT INTO  `currency`
                      (
                      `name`,
                      `symbol`,
                      `cmc_url`,
                      `website`,
                      `explorer`,
                      `announcement`,
                      `message_board`,
                      `enabled`,
                      `review_status`,
                      `created_at`,
                      `updated_at`
                      )
              VALUES  (
                        "{name}",
                        "{symbol}",
                        "{cmc_url}",
                        "{website}",
                        "{explorer}",
                        "{announcement}",
                        "{message_board}",
                        "{enabled}",
                        "{review_status}",
                        unix_timestamp(now()),
                        unix_timestamp(now())
                      )
    '''

    with conn_data.cursor() as cursor:
        for s in currency_data.keys():
            name = currency_data[s]['currency']
            symbol = currency_data[s]['symbol']
            currency = currency_data[s]['name']

            extra_data = {
                'cmc_url': currency_data[s]['url'],
                'website': '',
                'explorer': '',
                'announcement': '',
                'message_board': '',
            }

            for l in currency_data[s]['media']:
                if extra_data['website'] == ''\
                        and 'website' in str(l[1]).lower():
                    extra_data['website'] = l[0]
                elif extra_data['explorer'] == ''\
                        and 'explorer' in str(l[1]).lower():
                    extra_data['explorer'] = l[0]
                elif extra_data['announcement'] == ''\
                        and 'announcement' in str(l[1]).lower():
                    extra_data['announcement'] = l[0]
                elif extra_data['message_board'] == ''\
                        and 'message board' in str(l[1]).lower():
                    extra_data['message_board'] = l[0]
                elif 'explorer' not in str(l[1]).lower()\
                    and 'website' not in str(l[1]).lower()\
                        and 'message board' not in str(l[1]).lower():
                    print_log(
                        'new currency link? found {} / {}'.format(l[0], l[1]))

            # insert if symbol not exists : update_type = 0
            # insert an unenabled
            # if symbol exist but name not match : update_type = 1
            # update if currency match : update_type = 2
            # currency is format of 'Bitcoin/BTC'
            update_type = 0
            exist_currency_info = {}
            for ec in exist_currencies:
                if currency == ec['currency']:
                    update_type = 2
                    exist_currency_info['id'] = ec['id']
                    exist_currency_info['cmc_url'] = ec['cmc_url']
                    exist_currency_info['website'] = ec['website']
                    exist_currency_info['explorer'] = ec['explorer']
                    exist_currency_info['announcement'] = ec['announcement']
                    exist_currency_info['message_board'] = ec['message_board']
                    break
                elif symbol == ec['symbol']:
                    update_type = 1

            if update_type == 0:
                exec_sql = inerst_sql_str.format(
                    name=name,
                    symbol=symbol,
                    cmc_url=extra_data['cmc_url'],
                    website=extra_data['website'],
                    explorer=extra_data['explorer'],
                    announcement=extra_data['announcement'],
                    message_board=extra_data['message_board'],
                    enabled=1,
                    review_status=1,
                )
                # print_log(exec_sql)
                cursor.execute(exec_sql)

            if update_type == 1:
                exec_sql = inerst_sql_str.format(
                    name=name,
                    symbol=symbol,
                    cmc_url=extra_data['cmc_url'],
                    website=extra_data['website'],
                    explorer=extra_data['explorer'],
                    announcement=extra_data['announcement'],
                    message_board=extra_data['message_board'],
                    enabled=0,
                    review_status=0,
                )
                # print_log(exec_sql)
                cursor.execute(exec_sql)

            if update_type == 2:  # currency exists
                cols = ('cmc_url', 'website', 'explorer',
                        'announcement', 'message_board')
                update_str = ''
                for col in cols:
                    if not exist_currency_info[col] and extra_data[col]:
                        update_str += "{}='{}', ".format(col, extra_data[col])

                if update_str:
                    exec_sql = 'update currency set {} where id={}'.format(
                        update_str[:-2], exist_currency_info['id'])
                    # print_log(exec_sql)
                    cursor.execute(exec_sql)

            # update max supply
            if ('max_supply' in currency_data[s].keys()):
                max_supply = currency_data[s]['max_supply']
                if max_supply and int(max_supply) > 0:
                    update_max_supply_sql = '''
                        UPDATE  coin_market_cap
                           SET  max_supply={max_supply}
                         WHERE  symbol="{symbol}"
                           AND  name="{name}"
                           AND  max_supply is null
                    '''.format(max_supply=max_supply,
                               symbol=symbol,
                               name=name)
                    # print(update_max_supply_sql)
                    cursor.execute(update_max_supply_sql)

    conn_data.commit()


def update_market_info(market_data, conn_data):
    # base market info
    update_sql_str = '''
        START   TRANSACTION;
        UPDATE  market
        SET     cmc_url = "{cmc_url}",
                updated_at = unix_timestamp(now())
        WHERE   name = "{name}" ;

        INSERT INTO market
                    (
                    `name`,
                    `cmc_url`,
                    `website`,
                    `twitter`,
                    `twitter_name`,
                    `created_at`,
                    `updated_at`
                    )
        SELECT      "{name}" as `name`,
                    "{cmc_url}" as `cmc_url`,
                    "{website}" as `website`,
                    "{twitter}" as `twitter`,
                    "{twitter_name}" as `twitter_name`,
                    unix_timestamp(now()) as `created_at`,
                    unix_timestamp(now()) as `update_at`
        FROM        dual
        WHERE       not exists (
        SELECT      `name`
        FROM        market
        WHERE       `name` = '{name}'
        )
    '''
    # update_sql_str = '''
    #      INSERT INTO  `market`
    #                   (
    #                   `name`,
    #                   `cmc_url`,
    #                   `website`,
    #                   `twitter`,
    #                   `twitter_name`,
    #                   `created_at`,
    #                   `updated_at`
    #                   )
    #           VALUES  (
    #                     "{name}",
    #                     "{cmc_url}",
    #                     "{website}",
    #                     "{twitter}",
    #                     "{twitter_name}",
    #                     unix_timestamp(now()),
    #                     unix_timestamp(now())
    #                   )
    #               ON  DUPLICATE KEY
    #           UPDATE  `cmc_url`="{cmc_url}",
    #                   `updated_at`=unix_timestamp(now())
    # '''

    with conn_data.cursor() as cursor:
        for m in market_data.keys():
            name = market_data[m]['name']
            cmc_url = market_data[m]['url']
            website = ''
            twitter = ''
            twitter_name = ''

            for l in market_data[m]['media']:
                if l[0] == l[1] and website == '':
                    website = l[0]
                elif 'twitter.com' in l[0]:
                    twitter = l[0]
                    twitter_name = l[1]
                else:
                    print_log(
                        'new market link? found {} / {}'.format(l[0], l[1]))

            exec_sql = update_sql_str.format(
                    name=name,
                    cmc_url=cmc_url,
                    website=website,
                    twitter=twitter,
                    twitter_name=twitter_name)

            cursor.execute(exec_sql)

    conn_data.commit()


def update_currency_market_info(currency_data, conn_data,
                                exist_symbols, exist_markets):

    update_sql_str = '''
        START   TRANSACTION;
        UPDATE      `currency_on_market` com
        INNER JOIN  `market` m on m.`id`=com.`market_id`
        SET         com.`volume_24h`={volume_24h},
                    com.`currency`="{currency}",
                    com.`anchor`="{anchor}",
                    com.`updated_at`=unix_timestamp(now())
        WHERE       com.`currency_id`={currency_id}
        AND         com.`market_id`={market_id}
        AND         com.`pair`="{pair}"
        AND         m.`synchronized`=0;

        INSERT INTO `currency_on_market`
                    (
                      `currency_id`,
                      `market_id`,
                      `pair`,
                      `currency`,
                      `anchor`,
                      `volume_24h`,
                      `created_at`,
                      `updated_at`
                    )
        SELECT      {currency_id} as `currency_id`,
                    {market_id} as `market_id`,
                    "{pair}" as `pair`,
                    "{currency}" as `currency`,
                    "{anchor}" as `anchor`,
                    {volume_24h} as `volume_24h`,
                    unix_timestamp(now()) as `created_at`,
                    unix_timestamp(now()) as `update_at`
        FROM        dual
        WHERE       not exists (
        SELECT      *
        FROM        currency_on_market
        WHERE       `currency_id` = {currency_id}
        AND         `market_id` = {market_id}
        AND         `pair` = "{pair}"
        )
    '''

    with conn_data.cursor() as cursor:
        for cur in exist_symbols:
            # 如果是需要更新的
            if cur['currency'] in currency_data.keys() and\
               not (cur['enabled'] is not None and cur['enabled'] == 0):
                currency_id = cur['id']

                for mc in currency_data[cur['currency']]['markets']:
                    market_id = exist_markets.get(mc['markets'], None)

                    if market_id is not None:
                        # print(mc)
                        pair = mc['pair']
                        (currency, anchor) = get_currency_anchor(pair)
                        if currency and anchor:
                            if ('volume' in mc.keys()):
                                volume_24h = float(mc['volume'])
                            else:
                                volume_24h = 0

                            exec_sql = update_sql_str.format(
                                currency_id=currency_id,
                                market_id=market_id,
                                pair=pair,
                                currency=currency,
                                anchor=anchor,
                                volume_24h=volume_24h)
                            # print(exec_sql)
                            cursor.execute(exec_sql)
                        else:
                            print_log('illegal pair found: {}'.format(pair))
                    else:
                        print_log(
                            'market not found when update market/currency')
                        print_log(
                            'currency: {} market: {}'.format(
                                mc['currency'], mc['markets']))

    conn_data.commit()


def get_currency_anchor(pair):
    pos = pair.find('/')
    if pos > -1:
        return (pair[:pos], pair[pos+1:])
    else:
        return False
    return (None, None)


def get_spider_results(conn, project):
    mysql = '''
        select  updatetime,
                result
          from  {}
    '''.format(project)

    with conn.cursor() as cursor:
        cursor.execute(mysql)
        result = cursor.fetchall()

    return result


if __name__ == '__main__':
    try:
        conn_spider = pymysql.connect(**get_mysql_conn_params('cmc_spider_db'))
        print_log('spider connection got...')
        conn_data = pymysql.connect(**get_mysql_conn_params('cmc_data_db'))
        print_log('data connection got...')

        spider_result = get_spider_data(conn_spider)

        exist_currencies = get_exist_currencies(conn_data)
        update_currency_basic_info(spider_result['currencies'], conn_data,
                                   exist_currencies)

        update_market_info(spider_result['markets'], conn_data)

        exist_currencies = get_exist_currencies(conn_data)
        exist_markets = get_exist_markets(conn_data)
        update_currency_market_info(spider_result['currencies'], conn_data,
                                    exist_currencies, exist_markets)

    except aException as e:
        print_log('find exception, terminated!', 'ERROR')
        print_log(e, 'ERROR')
    finally:
        if 'conn_data' in dir():
            conn_data.close()
            print_log('data connection closed!')
        if 'conn_spider' in dir():
            conn_spider.close()
            print_log('spider connection closed!')
