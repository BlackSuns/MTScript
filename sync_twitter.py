import os

import arrow
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


if __name__ == '__main__':
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

        st = SocialTimeline()
        st.currency_id = currency.currency_id
        st.social_nickname = content.author
        st.social_account = content.account
        st.social_content_id = content.social_id
        st.content = content.html_text
        st.content_translation = content.text_chinese
        if content.retweet:
            st.content = 'retweet {}:\n {}'.format(content.retweet_author,
                                                   content.html_text)
            st.content_translation = '转推 {}:\n {}'.format(
                content.retweet_author,
                content.html_text)
        st.source = 'twitter'
        st.review_status = 1 - int(currency.need_review)
        st.posted_at = content.created_at
        st.created_at = arrow.now().timestamp
        st.updated_at = arrow.now().timestamp
        remote_session.add(st)

        content.synchronized = 1

        try:
            local_session.commit()
            remote_session.commit()
        except Exception as e:
            print_log(e)
