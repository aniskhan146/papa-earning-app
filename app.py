import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

# --- অ্যাপ সেটআপ ---
app = Flask(__name__)
CORS(app)  # ফ্রন্টএন্ডকে অ্যাক্সেস দেওয়ার জন্য

# --- ইন-মেমোরি ডেটাবেস (শুধুমাত্র ডেমোর জন্য) ---
# একটি বাস্তব অ্যাপ্লিকেশনে এখানে PostgreSQL, MongoDB বা Redis ব্যবহার করা উচিত।
# Render-এর ফ্রি সার্ভার রিস্টার্ট হলে এই ডেটা রিসেট হয়ে যাবে।
user_data = {
    'balance': 15.75,
    'lifetime_points': 150.25,
    'last_ad_time': 0,  # UNIX timestamp for cooldown
    'last_daily_bonus': None,  # ISO format string date
    'history': [
        {'type': 'Initial Bonus', 'amount': 10.00, 'date': '2023-10-27T10:00:00Z'},
        {'type': 'Ad Reward', 'amount': 5.75, 'date': '2023-10-27T11:30:00Z'},
    ]
}

# --- পুরস্কারের পরিমাণ ---
REWARDS = {
    'adsgram': 2.50,
    'monetag_rewarded': 5.00,
    'monetag_interstitial': 1.25,
    'daily_bonus': 25.00
}

# ৩০ সেকেন্ডের গ্লোবাল কুলডাউন
AD_COOLDOWN_SECONDS = 30

# --- API রুটস ---

@app.route('/')
def home():
    """সার্ভার চলছে কিনা তা নিশ্চিত করার জন্য মূল রুট"""
    return "PAPA Earning API is running successfully!"

@app.route('/api/data', methods=['GET'])
def get_user_data():
    """ব্যবহারকারীর সমস্ত ডেটা প্রদান করে"""
    return jsonify(user_data)

@app.route('/api/reward', methods=['POST'])
def grant_reward():
    """বিজ্ঞাপন দেখার জন্য ব্যবহারকারীকে পুরস্কৃত করে"""
    global user_data

    # কুলডাউন চেক করা
    current_time = datetime.now().timestamp()
    time_since_last_ad = current_time - user_data['last_ad_time']
    
    if time_since_last_ad < AD_COOLDOWN_SECONDS:
        remaining_time = AD_COOLDOWN_SECONDS - time_since_last_ad
        return jsonify({'error': f'Please wait {int(remaining_time)} more seconds'}), 429 # 429 = Too Many Requests

    # পুরস্কার যোগ করা
    data = request.json
    ad_type = data.get('type')
    
    if ad_type not in REWARDS:
        return jsonify({'error': 'Invalid reward type'}), 400

    amount = REWARDS[ad_type]
    user_data['balance'] += amount
    user_data['lifetime_points'] += amount
    user_data['last_ad_time'] = current_time

    # ইতিহাস যুক্ত করা
    user_data['history'].insert(0, {
        'type': f'{ad_type.replace("_", " ").title()} Reward',
        'amount': amount,
        'date': datetime.utcnow().isoformat() + 'Z'
    })

    return jsonify({
        'message': f'Successfully rewarded {amount} points!',
        'new_balance': user_data['balance']
    })

@app.route('/api/daily_bonus', methods=['POST'])
def claim_daily_bonus():
    """প্রতি ২৪ ঘণ্টায় একবার ডেইলি বোনাস প্রদান করে"""
    global user_data
    
    today_str = datetime.utcnow().date().isoformat()
    
    if user_data['last_daily_bonus'] == today_str:
        return jsonify({'error': 'Daily bonus already claimed for today'}), 400
        
    amount = REWARDS['daily_bonus']
    user_data['balance'] += amount
    user_data['lifetime_points'] += amount
    user_data['last_daily_bonus'] = today_str

    user_data['history'].insert(0, {
        'type': 'Daily Bonus',
        'amount': amount,
        'date': datetime.utcnow().isoformat() + 'Z'
    })

    return jsonify({
        'message': f'🎉 Congratulations! You have claimed your daily bonus of {amount} points!',
        'new_balance': user_data['balance']
    })

# --- সার্ভার রান করা ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)