import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# --- অ্যাপ সেটআপ ---
app = Flask(__name__)
CORS(app)

# --- কনফিগারেশন ---
AD_REWARD_AMOUNT_USDT = 0.00000551
AD_COOLDOWN_SECONDS = 25

# --- ডেমো ডেটাবেস ---
user_database = {
    "default_user": {
        "profile": {"name": "PAPA Player", "league": "Gold"},
        "balance": {"coins": 125000.0, "usdt": 0.0, "ton": 0.0},
        "energy": {"current": 500, "max": 500, "last_updated": datetime.now().timestamp()},
        "tap_stats": {"coins_per_tap": 1},
        "completed_tasks": [],
        "last_ad_reward_time": 0
    }
}
TASKS = {"task1": {"coins": 50000, "usdt": 0.1, "title": "Join our Community"},"task2": {"coins": 100000, "usdt": 0.0, "title": "Follow us on X"}}
ADS_REWARDS = {"monetag_reward_1": {"usdt": AD_REWARD_AMOUNT_USDT}, "monetag_reward_2": {"usdt": AD_REWARD_AMOUNT_USDT}}

def get_user(user_id):
    if user_id not in user_database:
        # Avoid complex copying, create fresh
        user_database[user_id] = {
            "profile": {"name": "New Player", "league": "Bronze"},
            "balance": {"coins": 0.0, "usdt": 0.0, "ton": 0.0},
            "energy": {"current": 500, "max": 500, "last_updated": datetime.now().timestamp()},
            "tap_stats": {"coins_per_tap": 1},
            "completed_tasks": [],
            "last_ad_reward_time": 0
        }
    return user_database[user_id]

# --- ঠিক করা হয়েছে: সব ফাংশন এখন সঠিক ফরম্যাটে ---
@app.route('/')
def home():
    return "PAPA TAP Game API v2.1 is running!"

@app.route('/api/data/<user_id>', methods=['GET'])
def get_game_data(user_id):
    user = get_user(user_id)
    time_passed = datetime.now().timestamp() - user["energy"]["last_updated"]
    energy_to_add = int(time_passed)
    user["energy"]["current"] = min(user["energy"]["max"], user["energy"]["current"] + energy_to_add)
    return jsonify(user)

@app.route('/api/reward_ad', methods=['POST'])
def reward_for_ad():
    data = request.json
    user_id = data.get("userId", "default_user")
    ad_id = data.get("adId")
    user = get_user(user_id)
    now = datetime.now().timestamp()
    if now - user.get('last_ad_reward_time', 0) < AD_COOLDOWN_SECONDS:
        remaining = int(AD_COOLDOWN_SECONDS - (now - user.get('last_ad_reward_time', 0)))
        return jsonify({"error": f"Please wait {remaining}s"}), 429
    if ad_id not in ADS_REWARDS:
        return jsonify({"error": "Invalid Ad ID"}), 400
    reward = ADS_REWARDS[ad_id]
    user["balance"]["usdt"] += reward.get("usdt", 0)
    user["last_ad_reward_time"] = now
    return jsonify({"message": f"Rewarded {reward.get('usdt')} USDT!","new_balance": user["balance"],"last_ad_reward_time": now})

@app.route('/api/tap', methods=['POST'])
def process_taps():
    data = request.json
    user_id = data.get("userId", "default_user")
    user = get_user(user_id)
    earned_coins = data.get("taps", 0) * user["tap_stats"]["coins_per_tap"]
    user["balance"]["coins"] += earned_coins
    user["energy"]["current"] -= data.get("taps", 0)
    return jsonify({"message": f"Earned {earned_coins} coins!"})

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    user_id = data.get("userId")
    task_id = data.get("taskId")
    user = get_user(user_id)
    if task_id in user["completed_tasks"]: return jsonify({"error": "Task already completed"}), 400
    reward = TASKS[task_id]
    user["balance"]["coins"] += reward.get("coins", 0)
    user["balance"]["usdt"] += reward.get("usdt", 0)
    user["completed_tasks"].append(task_id)
    return jsonify({"message": "Task completed!", "new_balance": user["balance"]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)