# app.py

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import datetime
import os
import sqlite3
import json

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
DATABASE = 'users.db'

# --- Database Functions ---
def get_db():
    """Database connection toiri kora."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Database table toiri kora (jodi na thake)."""
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Configuration ---
REWARD_PER_AD = 0.10
REWARD_PER_MONETAG_REWARDED_AD = 0.08
REWARD_PER_MONETAG_INTERSTITIAL = 0.05
DAILY_BONUS = 0.50
COOLDOWN_SECONDS = 30

# --- User Data Management ---
def get_user_data():
    """Session theke user data neowa ba notun user toiri kora."""
    user_id = session.get('user_id')
    if not user_id:
        db = get_db()
        # Notun user toiri kora hocche
        cursor = db.execute('INSERT INTO users (balance, lifetime_points, history, last_ad_time, last_daily_bonus) VALUES (?, ?, ?, ?, ?)',
                            (0.0, 0.0, '[]', 0, None))
        db.commit()
        user_id = str(cursor.lastrowid)
        session['user_id'] = user_id
    
    db = get_db()
    user_row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user_row:
        # Jodi kono karone user na pawa jay, abar toiri kora hobe
        session.pop('user_id', None)
        return get_user_data()

    user_data = dict(user_row)
    user_data['history'] = json.loads(user_data['history']) # JSON string theke list e porinoto kora
    return user_data

def update_user_data(user_data):
    """User data database e update kora."""
    db = get_db()
    history_json = json.dumps(user_data['history']) # List ke JSON string e porinoto kora
    db.execute('UPDATE users SET balance = ?, lifetime_points = ?, history = ?, last_ad_time = ?, last_daily_bonus = ? WHERE id = ?',
               (user_data['balance'], user_data['lifetime_points'], history_json, user_data['last_ad_time'], user_data['last_daily_bonus'], user_data['id']))
    db.commit()

def add_transaction(user_data, type, amount):
    """Notun transaction history jog kora."""
    transaction = {'type': type, 'amount': amount, 'date': datetime.now().isoformat()}
    user_data['history'].insert(0, transaction)
    if len(user_data['history']) > 50:
        user_data['history'].pop()

# --- API Routes ---
@app.route('/')
def index():
    return "Backend is running!"

@app.route('/api/data')
def get_data_api():
    user_data = get_user_data()
    return jsonify(user_data)

@app.route('/api/reward', methods=['POST'])
def give_reward():
    user_data = get_user_data()
    data = request.json
    ad_type = data.get('type')
    current_time = datetime.now().timestamp()

    if current_time - user_data['last_ad_time'] < COOLDOWN_SECONDS:
        return jsonify({'error': 'Please wait for cooldown'}), 429

    reward_map = {
        'adsgram': (REWARD_PER_AD, 'AdsGram Reward'),
        'monetag_rewarded': (REWARD_PER_MONETAG_REWARDED_AD, 'Monetag Reward'),
        'monetag_interstitial': (REWARD_PER_MONETAG_INTERSTITIAL, 'Monetag Ad')
    }
    
    if ad_type in reward_map:
        reward, transaction_type = reward_map[ad_type]
        user_data['balance'] += reward
        user_data['lifetime_points'] += reward
        user_data['last_ad_time'] = current_time
        add_transaction(user_data, transaction_type, reward)
        update_user_data(user_data)
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid ad type'}), 400

@app.route('/api/daily_bonus', methods=['POST'])
def claim_daily_bonus():
    user_data = get_user_data()
    today_str = datetime.now().date().isoformat()

    if user_data['last_daily_bonus'] and user_data['last_daily_bonus'] == today_str:
        return jsonify({'error': 'Already claimed today'}), 400

    user_data['balance'] += DAILY_BONUS
    user_data['lifetime_points'] += DAILY_BONUS
    user_data['last_daily_bonus'] = today_str
    add_transaction(user_data, 'Daily Bonus', DAILY_BONUS)
    update_user_data(user_data)
    
    return jsonify({'success': True, 'message': f'You received {DAILY_BONUS} bonus points!'})

if __name__ == '__main__':
    init_db() # Server shuru howar age database toiri kore nebe
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
