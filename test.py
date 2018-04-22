from flask import Flask, redirect
from flask import session as Flask_Session
import Oauth

app = Flask(__name__)
Oauth.init(app)

@app.route('/')
def index():
    return redirect('/Login')

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
    app.secret_key = 'super_secret_key'
    app.run(debug= True)
