import base64
from contextlib import contextmanager

import fitbit
import requests

from app.models import save_fitbit_token
from config import get_current_config
import datetime

# These grant permissions for your app to access user data.
# Ask for as little as possible
# Details https://dev.fitbit.com/docs/oauth2/

# aug 9, 2023 - added in more scopes
# oct 16, 2025 - added in ecg

SCOPES = [
    'profile',
    'activity',
    'heartrate',
    'location',
    'nutrition',
    'settings',
    'sleep',
    'social',
    'weight',
    'oxygen_saturation', 
    'respiratory_rate',
    'temperature',
    'electrocardiogram'
]


def dump_dict(obj):
    with open('log.txt', 'w') as f:
        json.dump(obj,f)

@contextmanager
def fitbit_client(fitbit_credentials):
    config = get_current_config()
    client = fitbit.Fitbit(
        config.FITBIT_CLIENT_ID,
        config.FITBIT_CLIENT_SECRET,
        access_token=fitbit_credentials.access_token,
        refresh_token=fitbit_credentials.refresh_token,
        expires_at=fitbit_credentials.expires_at,
        refresh_cb=lambda tokendict: save_fitbit_token(fitbit_credentials.user_id,  #
                                                       tokendict['access_token'],   # refresh_cb takes only a tokendict as a parameter
                                                       tokendict['refresh_token'],  # so save_fitbit_token is rewritten as a lambda
                                                       tokendict['expires_at'])     #
    )
    yield client
    # Save in case we did some refreshes - this is now taken over by refresh_cb above.
    #save_fitbit_token(
    #    fitbit_credentials.user_id,
    #    client.client.session.token['access_token'],
    #    client.client.session.token['refresh_token'],
    #    client.client.session.token['expires_at']
    #)


def get_permission_screen_url(user_state):
    return ('https://fitbit.com/oauth2/authorize'
            '?response_type=code&client_id={client_id}&scope={scope}&prompt=login&state={state}').format(
        client_id=get_current_config().FITBIT_CLIENT_ID,
        scope='%20'.join(SCOPES),
        state=user_state
    )


def get_token():
    config = get_current_config()
    return base64.b64encode(
        "{}:{}".format(
            config.FITBIT_CLIENT_ID,
            config.FITBIT_CLIENT_SECRET
        ).encode('utf-8')
    ).decode('utf-8')


def get_auth_url(code):
    return 'https://api.fitbit.com/oauth2/token?code={code}&client_id={client_id}&grant_type=authorization_code'.format(
        code=code,
        client_id=get_current_config().FITBIT_CLIENT_ID
    )


def do_fitbit_auth(code, user):
    r = requests.post(
        get_auth_url(code),
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(get_token()),
        }
    )
    r.raise_for_status()
    response = r.json()
    return save_fitbit_token(
        user,
        response['access_token'],
        response['refresh_token'],
        response['expires_in']+datetime.datetime.now().timestamp() # for some reason the response contains 'expires_in' but not 'expires_at'
    )
