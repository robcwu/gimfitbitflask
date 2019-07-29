import sqlalchemy
from fitbit.exceptions import BadResponse
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify

from urllib.parse import quote,unquote

from app import db
from app.fitbit_client import fitbit_client, get_permission_screen_url, do_fitbit_auth
from app.main.forms import DeviceUserForm
from app.models import get_user_fitbit_credentials, get_all_fitbit_credentials
from . import main

from oauthlib.oauth2.rfc6749.errors import InvalidGrantError


@main.route('/', methods=['GET', 'POST'])
def index():
    form = DeviceUserForm(request.form)
    creds = get_all_fitbit_credentials()
    user_profiles = []
    user_state = request.args.get('state')
    
    if user_state:
        perm_url = get_permission_screen_url(user_state)
    else:
        perm_url = None
    
    for cred in creds:
        with fitbit_client(cred) as client:
            try:
                profile_response = client.user_profile_get()
                user_profiles.append({
                    'username': cred.user_id,
                    'fullName': profile_response['user']['fullName']
                })
            except BadResponse:
                flash("Api Call Failed") 
            except InvalidGrantError:
                user_profiles.append({
                    'username': cred.user_id,
                    'fullName': 'PROFILE LOAD FAILED PLEASE REAUTHENTICATE'
                })
                				
        
    return render_template('index.html',
                           user_state=user_state,
                           form=form,
                           user_profiles=user_profiles,
                           permission_url=perm_url)


@main.route('/oauth-redirect', methods=['GET'])
def handle_redirect():
    code = request.args.get('code')
    user_id = request.args.get('state')
    do_fitbit_auth(code, user_id)
    return redirect(url_for('main.index'))

@main.route('/users', methods=['GET'])
def get_users():
    """
    endpoint that returns a json list of authenticated users
    
    """
    return jsonify([cred.user_id for cred in get_all_fitbit_credentials()])

@main.route('/data/<user>/intraday/<resource>/<base_date>/<detail_level>', methods=['GET'])
def get_data(user,resource,base_date,detail_level):
    """
    endpoint that retrieves intraday data
    """
    
    resource_ = resource.replace('-','/')
    
    if user == 'all':
        creds = get_all_fitbit_credentials()
        response = {}

        for cred in creds:
            with fitbit_client(cred) as client:
                try:
                    response[cred.user_id] = client.intraday_time_series(resource_,base_date=base_date,detail_level=detail_level)
                except BadResponse:
                    flash("Api Call Failed")        
        
        
    else:
        cred = get_user_fitbit_credentials(unquote(user))
        with fitbit_client(cred) as client:
            try:
                response = client.intraday_time_series(resource_,base_date=base_date,detail_level=detail_level)
            except BadResponse:
                flash("Api Call Failed, malformed query?")
        
    
    return jsonify(response)
    
    