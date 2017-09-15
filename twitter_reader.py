# -*- coding: utf-8 -*-
import hashlib
from urllib import parse
import os

import arrow
from twitter import Twitter, OAuth
import requests

from utils import get_config, print_log
from social_models.social import SocialContent, Media, local_session


def get_settings():
    settings = get_config(CONFIG_PATH, 'twitter', {
        'consumer_key': 'string',
        'consumer_secret': 'string',
        'access_token': 'string',
        'access_token_secret': 'string',
    })

    return settings

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'
settings = get_settings()
auth = OAuth(
    consumer_key=settings['consumer_key'],
    consumer_secret=settings['consumer_secret'],
    token=settings['access_token'],
    token_secret=settings['access_token_secret']
)


def analyze_twitter(msg):
    if 'id' in msg.keys():
        result = {
            'msg_type': 'direct',
            'id': msg['id'],
            'created_at': arrow.get(msg['created_at'],
                                    'ddd MMM DD HH:mm:ss ZZ YYYY').timestamp,
            'author': msg['user']['name'],
            'account': msg['user']['screen_name'],
            'retweet_author': '',
            'retweet_account': '',
        }

        if 'retweeted_status' in msg.keys():
            result['msg_type'] = 'retweet'
            msg = msg['retweeted_status']
            result['retweet_author'] = msg['user']['name']
            result['retweet_account'] = msg['user']['screen_name']

        result['text'] = msg['full_text'][
            msg['display_text_range'][0]:msg['display_text_range'][1]]\
            .replace("'", "\'")

        result['html_text'] = result['text']
        if 'entities' in msg.keys() and 'urls' in msg['entities'].keys():
            text = result['text']
            for url in msg['entities']['urls'][::-1]:
                text = text[:url['indices'][0]]\
                     + '<a href="{}" target="_blank">'.format(
                        url['expanded_url'])\
                     + url['display_url']\
                     + '</a>'\
                     + text[url['indices'][1]:]
            result['html_text'] = text

        if 'entities' in msg.keys() and 'media' in msg['entities'].keys():
            result['media'] = []
            for media in msg['entities']['media']:
                result['media'].append({
                    'media_type': media['type'],
                    'http_url': media['media_url'],
                    'https_url': media['media_url_https'],
                })

        return result
    else:
        return False


def filter_twitters(session, messages):
    start_time = messages[-1]['created_at']

    twitters = session.query(SocialContent)\
                      .filter(SocialContent.created_at >= start_time)
    exist_ids = [t.social_id for t in twitters]

    filtered_msgs = []
    for msg in messages:
        if msg['id'] not in exist_ids:
            filtered_msgs.append(msg)

    return filtered_msgs


def save_twitter(session, messages):
    for msg in messages:
        content = SocialContent()
        content.social_id = msg['id']
        content.source = 'twitter'
        content.created_at = msg['created_at']
        content.text = msg['text']
        content.html_text = msg['html_text']
        content.author = msg['author']
        content.account = msg['account']
        content.retweet = 1 if msg['msg_type'] == 'retweet' else 0
        content.retweet_author = msg['retweet_author']
        content.retweet_account = msg['retweet_account']
        if 'media' in msg.keys():
            for media in msg['media']:
                m = Media()
                m.social_content = content
                m.media_type = media['media_type']
                m.http_url = media['http_url']
                m.https_url = media['https_url']
                m.created_at = msg['created_at']
        session.add(content)
    session.commit()


def read_twitter(cnx):
    sql = '''
            select * from social_content
    '''
    cursor = cnx.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    print(data)


def get_translate(text, target_lang='zh-CHS'):
    app_key = '5479f92f6b8976fd'
    app_secret = 'TK4X01ekWwWLZaUhOl0mbhKHT6EMDPqJ'
    salt = 'mytk'
    support_lang = ('zh-CHS', 'ja', 'EN', 'ko', 'fr', 'ru', 'pt', 'es')
    if target_lang not in support_lang:
        return None

    host = "https://openapi.youdao.com/api"
    params = {
        'from': 'auto',
        'to': target_lang,
        'q': text,
        'appKey': app_key,
        'salt': salt,
        'sign': hashlib.md5('{}{}{}{}'.format(app_key,
                                              text,
                                              salt,
                                              app_secret)
                                      .encode(encoding='utf-8'))
                       .hexdigest()
    }

    encode_params = parse.urlencode(params)

    request_url = '{host}?{param}'.format(
                    host=host,
                    param=encode_params)

    try:
        r = requests.get(request_url, timeout=10)

        if r.status_code == 200 and r.json()['errCode'] == '0':
            return r.json()['translation'][0]
        else:
            print_log('someting wrong and return http code: {}'.format(
                r.status_code))
            return None
    except Exception as e:
        print_log('translate error: {}'.format(e))
        return None


def addslashes(s):
    try:
        d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\"}
        return ''.join(d.get(c, c) for c in s)
    except:
        return s


if __name__ == '__main__':
    # ts = TwitterStream(auth=auth, domain='userstream.twitter.com')
    # for msg in ts.user(tweet_mode='extended'):
    #     # print_log(json.dumps(msg, indent=4))
    #     tweete = analyze_twitter(msg)
    #     if tweete:
    #         save_twitter(session, [tweete, ])

    t = Twitter(auth=auth)

    while True:
        print_log('start work...')
        messages = t.statuses.home_timeline(tweet_mode='extended')
        to_insert = []

        for msg in messages:
            # print_log(json.dumps(msg, indent=4))
            to_insert.append(analyze_twitter(msg))

        to_insert = filter_twitters(local_session, to_insert)

        save_twitter(local_session, to_insert)
        print_log('{} twitters saved'.format(len(to_insert)))
        break
