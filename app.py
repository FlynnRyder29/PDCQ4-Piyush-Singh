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

# --- Phase 2: Printing Logic ---

def generate_diamond(n):
    # Pattern Logic derived from analysis:

    text_source = "FORMULAQSOLUTIONS"
    text_len = len(text_source)
    
    peak_row = (n // 2) + 1
    max_width = (2 * peak_row) - 1
    
    
    lines = []
    
    for r in range(1, n + 1):
        # Calculate width
        if r <= peak_row:
            width = 2 * r - 1
        else:
            width = (2 * peak_row - 1) - 2 * (r - peak_row)
            
        # Current Row Start Index
        start_idx = r - 1
        
        # Build the string
        row_str = ""
        
        # Even rows are boundary rows (with dashes)
        is_gap_row = (r % 2 == 0)
        
        if is_gap_row:
            # First char
            char_idx = start_idx
            row_str += text_source[char_idx % text_len]
            
            # Dashes
            gap_size = max(0, width - 2)
            row_str += '-' * gap_size
            
            # Last char (if width > 1)
            if width > 1:
                # The last char corresponds to index `start_idx + width - 1`
                char_idx = start_idx + width - 1
                row_str += text_source[char_idx % text_len]
        else:
            # Fill row - continuous substring
            for k in range(width):
                char_idx = start_idx + k
                row_str += text_source[char_idx % text_len]
        
        lines.append(row_str)
        
    # Formatting: Center align based on max width
    formatted_lines = []
    
    # IMPORTANT: The max width for centering could be larger than the design max width
    # if we want a generous canvas, or exactly the max width. Here we use the calculated max_width.
    
    for line in lines:
        padding = (max_width - len(line)) // 2
        formatted_lines.append(" " * padding + line)
        
    return "\n".join(formatted_lines)

@app.route('/print', methods=['POST'])
def print_pattern():
    data = request.json
    try:
        n = int(data.get('lines', 0))
        if n > 100:
            return jsonify({'error': 'Big numbers buddy, try scoring runs by imagining you are an opener in cricket, its an t20 match how much you can score, Now dont get too greedy'}), 400
        result = generate_diamond(n)
        return jsonify({'result': result})
    except ValueError:
         return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
