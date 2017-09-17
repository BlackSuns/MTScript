import os
import time

import arrow
import requests
from google.cloud import translate

from social_models.social import (SocialContent,
                                  SocialCurrency,
                                  local_session,
                                  remote_session,
                                  SocialTimeline)
from utils import get_config, print_log

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'
POST_TIME_SPAN = 60 * 60 * 24 * 10  # 处理过去多长时间的数据


def get_translation(text):
    trans_client = translate.Client(target_language='zh-CN')
    try:
        trans_data = trans_client.translate(text)
        return trans_data['translatedText']
    except Exception as e:
        print_log(e)
        return ''


def post(data):
    host = 'http://internal.mytoken.iknowapp.com:12306'
    endpoint = '/social/addtimeline'

    request_url = '{host}{endpoint}'.format(
        host=host, endpoint=endpoint)

    r = requests.post(request_url, data=data)

    if r.status_code == 200 and r.json()['code'] == 0\
       and r.json()['data']:
        # self.print_log(
        #     'post success: {symbol}/{anchor} on {market}'.format(
        #         symbol=params['symbol'],
        #         anchor=params['anchor'],
        #         market=self.exchange))
        return r.json()
    else:
        error_info = "someting wrong when dealing {}"\
                     " and return http code: {}".format(
                        data['social_content_id'],
                        r.status_code)
        if r.status_code == 200:
            try:
                error_info += ' and server return error: {}'.format(
                    r.json())
            except:
                pass
        print_log(error_info)


if __name__ == '__main__':
    time.sleep(60)
    sync_ts = arrow.now().timestamp
    for content, currency in\
        local_session.query(SocialContent, SocialCurrency).\
            filter(SocialContent.account == SocialCurrency.social_account).\
            filter(SocialContent.created_at > sync_ts - POST_TIME_SPAN).\
            filter(SocialContent.synchronized == 0).\
            all():
        print_log('handling id {} by {}'.format(content.social_id,
                                                content.account))
        if not content.text_chinese:
            print_log('start tranlate..')
            content.text_chinese = get_translation(content.html_text)

        rd = {}
        rd['currency_id'] = currency.currency_id
        rd['social_nickname'] = content.author
        rd['social_account'] = content.account
        rd['social_account_remark'] = currency.remark
        rd['social_content_id'] = content.social_id
        rd['content'] = content.html_text
        rd['content_translation'] = content.text_chinese
        if content.retweet:
            rd['content'] = 'retweet {}:\n {}'.format(content.retweet_author,
                                                      content.html_text)
            rd['content_translation'] = '转推 {}:\n {}'.format(
                content.retweet_author,
                content.text_chinese)
        rd['source'] = 'twitter'
        rd['review_status'] = 1 - int(currency.need_review)
        rd['posted_at'] = content.created_at
        rd['created_at'] = arrow.now().timestamp
        rd['updated_at'] = arrow.now().timestamp

        content.synchronized = 1

        print('rd: ', rd)
        result = post(rd)
        print(result)

        try:
            local_session.commit()
        except Exception as e:
            print_log(e)
