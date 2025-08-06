# app.py

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS  # Notun import
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Ei line-ti CORS error thik korbe

# Session data secure rakhar jonno ekta secret key proyojon.
app.secret_key = os.urandom(24)

# --- Configuration ---
REWARD_PER_AD = 0.10
REWARD_PER_MONETAG_REWARDED_AD = 0.08
REWARD_PER_MONETAG_INTERSTITIAL = 0.05
DAILY_BONUS = 0.50
REFERRAL_BONUS = 1.00
COOLDOWN_SECONDS = 30

# --- User Data Management (In-memory for simplicity) ---
# Real project e ekhane database (jemon SQLite, PostgreSQL) use kora hobe.
users_data = {}

def get_user_data():
    """Session theke user data neowa ba notun user toiri kora."""
    user_id = session.get('user_id')
    if not user_id:
        # Notun user er jonno ekta simple ID toiri kora hocche
        user_id = str(len(users_data) + 1)
        session['user_id'] = user_id

    if user_id not in users_data:
        users_data[user_id] = {
            'balance': 0.0,
            'lifetime_points': 0.0,
            'history': [],
            'last_ad_time': 0,
            'last_daily_bonus': None
        }
    return users_data[user_id]

def add_transaction(user_data, type, amount):
    """Notun transaction history jog kora."""
    transaction = {
        'type': type,
        'amount': amount,
        'date': datetime.now().isoformat()
    }
    user_data['history'].insert(0, transaction)
    if len(user_data['history']) > 50:
        user_data['history'].pop()

@app.route('/')
def index():
    """Web app-er main page render kora."""
    # Ekhon amra shudhu API hishebe kaaj korbo, tai HTML render korar proyojon nei.
    return "Backend is running!"


@app.route('/api/data')
def get_data():
    """User-er shob data JSON format e pathano."""
    user_data = get_user_data()
    return jsonify(user_data)

@app.route('/api/reward', methods=['POST'])
def give_reward():
    """Ad dekhar por reward dewa."""
    user_data = get_user_data()
    data = request.json
    ad_type = data.get('type')

    # Cooldown check
    current_time = datetime.now().timestamp()
    if current_time - user_data['last_ad_time'] < COOLDOWN_SECONDS:
        return jsonify({'error': 'Please wait for cooldown'}), 429

    reward = 0
    transaction_type = ''
    if ad_type == 'adsgram':
        reward = REWARD_PER_AD
        transaction_type = 'AdsGram Reward'
    elif ad_type == 'monetag_rewarded':
        reward = REWARD_PER_MONETAG_REWARDED_AD
        transaction_type = 'Monetag Reward'
    elif ad_type == 'monetag_interstitial':
        reward = REWARD_PER_MONETAG_INTERSTITIAL
        transaction_type = 'Monetag Ad'
    
    if reward > 0:
        user_data['balance'] += reward
        user_data['lifetime_points'] += reward
        user_data['last_ad_time'] = current_time
        add_transaction(user_data, transaction_type, reward)
        return jsonify({'success': True, 'balance': user_data['balance'], 'lifetime_points': user_data['lifetime_points']})
    
    return jsonify({'error': 'Invalid ad type'}), 400

@app.route('/api/daily_bonus', methods=['POST'])
def claim_daily_bonus():
    """Daily bonus claim kora."""
    user_data = get_user_data()
    today = datetime.now().date()

    if user_data['last_daily_bonus'] and datetime.fromisoformat(user_data['last_daily_bonus']).date() == today:
        return jsonify({'error': 'Already claimed today'}), 400

    user_data['balance'] += DAILY_BONUS
    user_data['lifetime_points'] += DAILY_BONUS
    user_data['last_daily_bonus'] = datetime.now().isoformat()
    add_transaction(user_data, 'Daily Bonus', DAILY_BONUS)
    
    return jsonify({'success': True, 'message': f'You received {DAILY_BONUS} bonus points!'})

if __name__ == '__main__':
    # Real project e 'debug=True' use kora hobe na.
    app.run(debug=True, port=5000)
