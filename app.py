import os
import datetime
import pytz
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def get_indian_time():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    return now.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    user = session.get('user')
    time_str = ""
    if user:
        time_str = get_indian_time()
    return render_template('index.html', user=user, time=time_str)

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
         session['user'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True, port=5000)
