from flask import Blueprint, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as Flask_Session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random, string, httplib2, json, requests


def init(app = None, DATA_SCOPE = "openid email", Client_Secret = 'client_secrets.json', data_Approvalprompt="force"):
    DATA_CLIENT_ID = json.loads(open(Client_Secret, 'r').read())['web']['client_id']
    Oauth = Blueprint('Oauth', __name__, template_folder='templates')

    # Create anti-forgery state token
    @Oauth.route('/Login/')
    def Login():
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        Flask_Session['state'] = state

        #return "The current session state is %s" % Flask_Session['state']
        return render_template('login.html', app=app, STATE=state, DATA_CLIENT_ID=DATA_CLIENT_ID, DATA_SCOPE=DATA_SCOPE, data_Approvalprompt=data_Approvalprompt)

    @Oauth.route('/gconnect', methods=['POST'])
    def gconnect():
        # Validate state token
        if request.args.get('state') != Flask_Session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Obtain authorization code
        code = request.data

        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(Client_Secret, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['issued_to'] != DATA_CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print("Token's client ID does not match app's.")
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_access_token = Flask_Session.get('access_token')
        stored_gplus_id = Flask_Session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        Flask_Session['access_token'] = credentials.access_token
        Flask_Session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        Flask_Session['username'] = data['name']
        Flask_Session['picture'] = data['picture']
        Flask_Session['email'] = data['email']

        return "Conected"

    # DISCONNECT - Revoke a current user's token and reset their Flask_Session

    @Oauth.route('/gdisconnect')
    def gdisconnect():
        access_token = Flask_Session.get('access_token')
        if access_token is None:
            print
            'Access Token is None'
            response = make_response(json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % Flask_Session['access_token']
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            del Flask_Session['access_token']
            del Flask_Session['gplus_id']
            del Flask_Session['username']
            del Flask_Session['email']
            del Flask_Session['picture']
            response = make_response(json.dumps('Successfully disconnected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps('Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response

    app.register_blueprint(Oauth)

