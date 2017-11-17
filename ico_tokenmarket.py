# -*-  coding=utf8  -*-

import json
import os

import arrow
import pymysql

from utils import print_log, get_config
from models.project import Tag, Project, Rater, local_session
from sqlalchemy.sql import func

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'
BASE_URL = get_config(
    CONFIG_PATH, 'exchange_settings', {'base_url': 'string'})['base_url']

INFOSOURCE = 'TokenMarket'


def get_mysql_conn_params(section):
    return get_config(CONFIG_PATH, section, {
        'host':       'string',
        'port':       'int',
        'user':       'string',
        'password':   'string',
        'db':         'string',
        'charset':    'string',
    })


def escape_text(txt):
    es_chars = ('"',)
    for char in es_chars:
        txt = txt.replace(char, '\{}'.format(char))

    return txt


def analyze_project(cnx, taskid, source_url, item):
    opening_date_standard = 0
    close_date_standard = 0

    if 'Crowdsale opening date' in item.keys():
        try:
            opening_date_standard = arrow.get(item['Crowdsale opening date'], 'D. MMM YYYY').timestamp
            if opening_date_standard < 0:
                opening_date_standard = 0
        except Exception as e:
            print(e)

    if 'Crowdsale closing date' in item.keys():
        try:
            close_date_standard = arrow.get(item['Crowdsale closing date'], 'D. MMM YYYY').timestamp
            if close_date_standard < 0:
                close_date_standard = 0
        except Exception as e:
            print(e)

    symbol = item.get('Symbol', '')
    symbol = symbol if len(symbol) < 10 else ''

    project = {
        'task_id': taskid,
        'info_source': INFOSOURCE,
        'info_source_url': source_url,
        'name': item['name'],
        'logo': item.get('logo', ''),
        'symbol': symbol,
        'country': item.get('Country of origin'),
        'detail_intro': escape_text(item.get('Concept', '')),

        'website':  item.get('Website', ''),
        'blog': item.get('Blog', ''),
        'twitter': item.get('Twitter', ''),
        'facebook': item.get('Facebook', ''),
        'linkedin': item.get('Linkedin', ''),
        'whitepaper': item.get('Whitepaper', ''),
        'slack': item.get('Slack chat', ''),
        'telegram': item.get('Telegram chat', ''),
        'github': item.get('Github', ''),

        'blockchain': item.get('Blockchain', ''),
        'team': escape_text(item.get('Members', '')),

        'opening_date': item.get('Token sale opening date', ''),
        'close_date': item.get('Token sale opening date', ''),
    }

    keys = []
    vals = []
    for k in project.keys():
        keys.append(k)
        vals.append('"{}"'.format(project[k]))

    project_insert_sql = '''
        insert into project
        ({}, opening_date_standard, close_date_standard, created_at, updated_at)
        values
        ({}, {}, {}, unix_timestamp(now()), unix_timestamp(now()))
    '''.format(
        ', '.join(keys),
        ', '.join(vals),
        opening_date_standard,
        close_date_standard)

    with cnx.cursor() as cursor:
        # insert project
        # print(project_insert_sql)
        cursor.execute(project_insert_sql)

    cnx.commit()


def deal_projects(cnx_raw, cnx_tmp):
    sql = '''
        select taskid, url, result from tokenmarket_init
    '''

    with cnx_raw.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    count = len(result)
    exist_taskids = get_current_taskids(cnx_tmp)
    for i, data in enumerate(result, 1):
        if data[0] not in exist_taskids:
            project = json.loads(data[2])
            print('dealing {}/{}: {}'.format(i, count, project['name']))
            analyze_project(cnx_tmp, data[0], data[1], project)


def get_current_taskids(cnx_tmp):
    sql = '''
        select task_id from project where info_source='{}'
    '''.format(INFOSOURCE)

    with cnx_tmp.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    taskids = []
    for row in result:
        taskids.append(row[0])

    return taskids


if __name__ == '__main__':
    cnx_raw = pymysql.connect(**get_mysql_conn_params('cmc_spider_db'))
    cnx_tmp = pymysql.connect(**get_mysql_conn_params('temp_db'))

    deal_projects(cnx_raw, cnx_tmp)
