from flask import Flask, redirect, render_template, Markup
from flask import session as Flask_Session
import random, string
import Google_Oauth2
import json
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
Google_Oauth2.init(app, Flask_Session)

@app.route('/')
def index():
    return redirect('/Login')

@app.route('/Login/', methods=['GET', 'POST'])
def Login(DATA_SCOPE="openid email", Client_Secret='client_secrets.json', data_Approvalprompt="force"):
    DATA_CLIENT_ID = json.loads(open(Client_Secret, 'r').read())['web']['client_id']
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    Flask_Session['state'] = state

    # return "The current session state is %s" % Flask_Session['state']
    return render_template('Login.html', app=app, STATE=state, DATA_CLIENT_ID=DATA_CLIENT_ID, DATA_SCOPE=DATA_SCOPE,
                           data_Approvalprompt=data_Approvalprompt)

@app.route('/Home')
def Home():
    output = '<h1>Welcome, '
    output += Flask_Session['username']
    output += '!</h1> <a href = "/gdisconnect">Log out </a>'
    output += '<img src="'
    output += Flask_Session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 3150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

if __name__ == "__main__":
    import platform
    app.secret_key = 'super_secret_key'
    if platform.system() == "Linux":
        app.run(host = "0.0.0.0", port= 8000, debug= True)
    else:
        app.run(host = "Localhost", port=8000, debug=True)
