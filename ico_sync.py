import os
import json

import requests

from models.project import Project, ProjectRater, Tag, local_session
from utils import print_log, get_config

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/script.conf'
BASE_URL = get_config(
    CONFIG_PATH, 'exchange_settings', {'base_url': 'string'})['base_url']


def post(data):
    endpoint = '/ico/mergeico?source=script'

    request_url = '{host}{endpoint}'.format(
        host=BASE_URL, endpoint=endpoint)

    data = {'ico_json': json.dumps(data)}

    # print(request_url)
    # print(data)
    r = requests.post(request_url, data=data)
    # print(r.text)
    return r

if __name__ == '__main__':
    projects = local_session.query(Project)\
                            .filter(Project.project_id != '')\
                            .filter(Project.sync_status == 0)
    count = projects.count()
    for i, p in enumerate(projects, 1):
        print_log('start dealing {}/{}: {}'.format(i, count, p.name))
        data = {}
        data['name'] = p.project_id
        data['currency_symbol'] = p.symbol
        data['brief_intro'] = p.brief_intro
        data['description'] = p.detail_intro.decode('utf-8') if p.detail_intro else ''
        data['logo'] = p.logo
        data['country'] = p.country
        data['website'] = p.website
        data['whitepaper'] = p.whitepaper
        data['github'] = p.github
        data['slack'] = p.slack
        data['twitter'] = p.twitter
        data['facebook'] = p.facebook
        data['email'] = p.email
        data['reddit'] = p.reddit
        data['telegram'] = p.telegram
        data['blog'] = p.blog
        data['linkedin'] = p.linkedin
        data['bitcointalk'] = p.bitcointalk
        data['blockchain'] = p.blockchain
        data['ico_hardcap'] = p.hardcap
        data['ico_accepts'] = p.accepts
        data['ico_bounty'] = p.bounty.decode('utf-8') if p.bounty else ''
        data['ico_price'] = p.ico_price.decode('utf-8') if p.ico_price else ''
        data['ico_distribution'] = p.token_distribution.decode('utf-8') if p.token_distribution else ''
        data['features'] = p.features.decode('utf-8') if p.features else ''
        data['ico_started_at'] = p.opening_date_standard if p.opening_date_standard > 0 else None
        data['ico_ended_at'] = p.close_date_standard if p.close_date_standard > 0 else None
        data['team'] = p.team.decode('utf-8') if p.team else ''
        data['source'] = p.info_source

        tags = []
        for t in p.tags:
            tags.append(t.tag)
        data['tags'] = tags
        rates = []
        for pr in p.raters:
            rates.append({
                'name': pr.rater.name,
                'grade': pr.grade,
                'report_link': pr.report_url,
            })

        data['rates'] = rates

        res = post(data)

        try:
            if res.json()['message'] == 'success' and 'result' in dict(res.json()['data']).keys():
                p.sync_status = int(res.json()['data']['result'])
                local_session.commit()
                print_log('{} done'.format(p.name))
            else:
                print_log('post failed: {}'.format(res.text))
        except wException as e:
            print(e)
