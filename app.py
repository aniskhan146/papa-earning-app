from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import datetime
import os
import sqlite3
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

DATABASE = 'users.db'

# ডাটাবেস কানেকশন ফাংশন
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ডাটাবেস ইনিশিয়ালাইজ করার জন্য
def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

# ইউজার ডেটা নেওয়া বা তৈরি করা
def get_user_data():
    user_id = session.get('user_id')
    db = get_db()

    if not user_id:
        cursor = db.execute(
            'INSERT INTO users (balance, lifetime_points, history, last_ad_time, last_daily_bonus) VALUES (?, ?, ?, ?, ?)',
            (0.0, 0.0, json.dumps([]), 0, None)
        )
        db.commit()
        user_id = str(cursor.lastrowid)
        session['user_id'] = user_id

    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        # যদি না পাওয়া যায়, সেশন রিসেট করে আবার কল করো
        session.pop('user_id', None)
        return get_user_data()

    user_data = dict(user)
    user_data['history'] = json.loads(user_data['history'])
    return user_data

# ইউজার ডেটা আপডেট করা
def update_user_data(user_data):
    db = get_db()
    history_json = json.dumps(user_data['history'])
    db.execute('UPDATE users SET balance = ?, lifetime_points = ?, history = ?, last_ad_time = ?, last_daily_bonus = ? WHERE id = ?',
               (user_data['balance'], user_data['lifetime_points'], history_json, user_data['last_ad_time'], user_data['last_daily_bonus'], user_data['id']))
    db.commit()

# ট্রানজেকশন যোগ করা
def add_transaction(user_data, type_, amount):
    transaction = {'type': type_, 'amount': amount, 'date': datetime.now().isoformat()}
    user_data['history'].insert(0, transaction)
    if len(user_data['history']) > 50:
        user_data['history'].pop()

# কনফিগারেশন
REWARD_PER_AD = 0.10
REWARD_PER_MONETAG_REWARDED_AD = 0.08
REWARD_PER_MONETAG_INTERSTITIAL = 0.05
DAILY_BONUS = 0.50
COOLDOWN_SECONDS = 30

# Routes
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

    if ad_type not in reward_map:
        return jsonify({'error': 'Invalid ad type'}), 400

    reward, transaction_type = reward_map[ad_type]
    user_data['balance'] += reward
    user_data['lifetime_points'] += reward
    user_data['last_ad_time'] = current_time
    add_transaction(user_data, transaction_type, reward)
    update_user_data(user_data)
    return jsonify({'success': True, 'balance': user_data['balance']})

@app.route('/api/daily_bonus', methods=['POST'])
def claim_daily_bonus():
    user_data = get_user_data()
    today_str = datetime.now().date().isoformat()

    if user_data['last_daily_bonus'] == today_str:
        return jsonify({'error': 'Already claimed today'}), 400

    user_data['balance'] += DAILY_BONUS
    user_data['lifetime_points'] += DAILY_BONUS
    user_data['last_daily_bonus'] = today_str
    add_transaction(user_data, 'Daily Bonus', DAILY_BONUS)
    update_user_data(user_data)
    return jsonify({'success': True, 'message': f'You received {DAILY_BONUS} bonus points!'})

@app.route('/api/withdraw', methods=['POST'])
def withdraw_points():
    user_data = get_user_data()
    data = request.json
    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    if amount <= 0:
        return jsonify({'error': 'Withdrawal amount must be positive'}), 400

    if user_data['balance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    user_data['balance'] -= amount
    add_transaction(user_data, 'Withdrawal', -amount)
    update_user_data(user_data)
    return jsonify({'success': True, 'message': f'Withdrawal request for {amount} points submitted.'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
