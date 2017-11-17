# -*-  coding=utf8  -*-

import json
import os
import re

import arrow
import pymysql

from utils import print_log, get_config
from models.project import Tag, Project, Rater, local_session
from sqlalchemy.sql import func

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'
BASE_URL = get_config(
    CONFIG_PATH, 'exchange_settings', {'base_url': 'string'})['base_url']

INFOSOURCE = 'ICORating'
PATTERN = {
    'DD.MM.YYYY': r'^\d\d\.\d\d\.\d\d\d\d$',
    'D.M.YYYY': r'^\d\d\.\d\d\.\d\d\d\d$'
}


def get_mysql_conn_params(section):
    return get_config(CONFIG_PATH, section, {
        'host':       'string',
        'port':       'int',
        'user':       'string',
        'password':   'string',
        'db':         'string',
        'charset':    'string',
    })


def get_tag_id(cnx, tag):
    tag_id = 0
    sql = '''
        select id from tag where tag='{}'
    '''.format(tag)

    with cnx.cursor() as cursor:
        # print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()

        if result:
            tag_id = result[0]
        else:
            sql = '''
                insert into tag (tag) values ('{}')
            '''.format(tag)
            cursor.execute(sql)
            tag_id = cnx.insert_id()

    return tag_id


def escape_text(txt):
    es_chars = ('"',)
    for char in es_chars:
        txt = txt.replace(char, '\{}'.format(char))

    return txt


def get_timestamp(date):
    # we will use pattern0 to match DD.MM.YYYY first
    # if failed, use pattern1 to match D.M.YYYY
    # else return 0
    ts = 0
    pattern0 = r'^\d\d\.\d\d\.\d\d\d\d$'
    pattern1 = r'^\d{1,2}.\d{1,2}.\d\d\d\d$'

    try:
        result = re.match(pattern0, date)
        if result:
            ts = arrow.get(date, 'DD.MM.YYYY').timestamp
            return ts
        else:
            result = re.match(pattern1, date)
            if result:
                ts = arrow.get(date, 'D.M.YYYY').timestamp
                return ts
            else:
                return 0
    except:
        return 0


def analyze_project(cnx, taskid, source_url, item):
    rater_id = 1
    opening_date = ''
    close_date = ''
    grade = None
    report = None
    opening_date_standard = 0
    close_date_standard = 0

    if 'ICO date' in item.keys():
        # print(item['ICO date'])
        try:
            item['ICO date'] = item['ICO date'].replace('\u2014', '-')
            (opening_date, close_date) = re.split(r'\s*[-—]\s*', item['ICO date'])
            opening_date_standard = get_timestamp(opening_date)
            close_date_standard = get_timestamp(close_date)
            if opening_date_standard < 0:
                opening_date_standard = 0
            if close_date_standard < 0:
                close_date_standard = 0

        except Exception as e:
            print(opening_date)
            print(close_date)
            print(e)

    tags = None
    if 'Category' in item.keys():
        tags = re.split(r'\s*[,&/\s]\s*', item['Category'])
    # print('tags: {}'.format(tags))

    if 'rating' in item.keys() and 'Invest score' in item['rating'].keys():
        if 'report' in item['rating'].keys():
            grade = item['rating']['deep_rating']
            report = item['rating']['report']

    project = {
        'task_id': taskid,
        'info_source': INFOSOURCE,
        'info_source_url': source_url,
        'name': item['name'],
        'project_id': '',
        'logo': item.get('logo', ''),
        'website':  item.get('Website', ''),
        'twitter': item['Social'].get('twitter', '') if 'Social' in item.keys() else '',
        'facebook': item['Social'].get('facebook', '') if 'Social' in item.keys() else '',
        'bitcointalk': item['Social'].get('bitcointalk', '') if 'Social' in item.keys() else '',
        'email': item['Social'].get('email', '') if 'Social' in item.keys() else '',
        'telegram': item['Social'].get('telegram', '') if 'Social' in item.keys() else '',
        'reddit': item['Social'].get('reddit', '') if 'Social' in item.keys() else '',
        'slack': item['Social'].get('slack', '') if 'Social' in item.keys() else '',
        'whitepaper': item['Social'].get('whitepaper', '') if 'Social' in item.keys() else '',
        'github': item['Social'].get('github', '') if 'Social' in item.keys() else '',
        'brief_intro': escape_text(item.get('Description', '')),
        'features': escape_text(item.get('Features', '')),
        'accepts': item.get('Accepts', ''),
        'ico_price': escape_text(item.get('Token Sales', '')),
        'bounty': escape_text(item.get('Bounty campaign', '')),
        'opening_date': opening_date.strip(),
        'close_date': close_date.strip(),
        'token_distribution': escape_text(item.get('Tokens distribution', '')),
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
        project_id = cnx.insert_id()

        # insert tags
        for tag in tags:
            if tag:
                tag_id = get_tag_id(cnx, tag)
                sql = '''
                    insert into project_tag (project_id, tag_id) values ({}, {})
                '''.format(project_id, tag_id)
                cursor.execute(sql)

        # insert grade
        if grade:
            sql = '''
                insert into project_rater
                (project_id, rater_id, grade, report_url, created_at, updated_at)
                values
                ({}, {}, '{}', '{}', unix_timestamp(now()), unix_timestamp(now()))
            '''.format(project_id, rater_id, grade, report)
            # print(sql)
            cursor.execute(sql)

    cnx.commit()


def deal_projects(cnx_raw, cnx_tmp):
    sql = '''
        select taskid, url, result from icorating
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
