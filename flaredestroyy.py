import json

import requests

from pynyaata.config import CLOUDPROXY_ENDPOINT

json_session = requests.post(CLOUDPROXY_ENDPOINT, data=json.dumps({
    'cmd': 'sessions.list'
}))
response = json.loads(json_session.text)
sessions = response['sessions']

for session in sessions:
    requests.post(CLOUDPROXY_ENDPOINT, data=json.dumps({
        'cmd': 'sessions.destroy',
        'session': session
    }))
    print('Destroyed %s' % session)
