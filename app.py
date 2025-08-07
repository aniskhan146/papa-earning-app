import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# --- অ্যাপ সেটআপ ---
app = Flask(__name__)
CORS(app)

# --- ডেমো ডেটাবেস ---
user_database = {
    "default_user": {
        "profile": {"name": "PAPA Player", "league": "Gold"},
        "balance": {"coins": 125000.0, "usdt": 0.0, "ton": 0.0},
        "energy": {"current": 500, "max": 500, "last_updated": datetime.now().timestamp()},
        "tap_stats": {"coins_per_tap": 1},
        "completed_tasks": [],
        "completed_ads": [] # কোন কোন বিজ্ঞাপন দেখা হয়েছে তার ট্র্যাক রাখার জন্য
    }
}

TASKS = {
    "task1": {"coins": 50000, "usdt": 0.1, "title": "Join our Community"},
    "task2": {"coins": 100000, "usdt": 0.0, "title": "Follow us on X"},
}

# --- বিজ্ঞাপনের পুরস্কার ---
ADS_REWARDS = {
    "monetag_reward_1": {"coins": 25000},
    "monetag_reward_2": {"coins": 15000}
}


def get_user(user_id):
    if user_id not in user_database:
        user_database[user_id] = user_database["default_user"].copy()
    return user_database[user_id]


@app.route('/api/data/<user_id>', methods=['GET'])
def get_game_data(user_id):
    # (এই অংশটি অপরিবর্তিত)
    user = get_user(user_id)
    time_passed = datetime.now().timestamp() - user["energy"]["last_updated"]
    energy_to_add = int(time_passed)
    user["energy"]["current"] = min(user["energy"]["max"], user["energy"]["current"] + energy_to_add)
    user["energy"]["last_updated"] = datetime.now().timestamp()
    return jsonify(user)

@app.route('/api/tap', methods=['POST'])
def process_taps():
    # (এই অংশটি অপরিবর্তিত)
    data = request.json
    user_id = data.get("userId", "default_user")
    user = get_user(user_id)
    earned_coins = data.get("taps", 0) * user["tap_stats"]["coins_per_tap"]
    user["balance"]["coins"] += earned_coins
    user["energy"]["current"] -= data.get("taps", 0)
    if user["energy"]["current"] < 0: user["energy"]["current"] = 0
    return jsonify({"message": f"Earned {earned_coins} coins!"})

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    # (এই অংশটি অপরিবর্তিত)
    data = request.json; user_id = data.get("userId"); task_id = data.get("taskId")
    user = get_user(user_id)
    if task_id in user["completed_tasks"]: return jsonify({"error": "Task already completed"}), 400
    reward = TASKS[task_id]
    user["balance"]["coins"] += reward.get("coins", 0)
    user["balance"]["usdt"] += reward.get("usdt", 0)
    user["completed_tasks"].append(task_id)
    return jsonify({"message": "Task completed!", "new_balance": user["balance"]})

# --- নতুন API রুট: বিজ্ঞাপন দেখার পুরস্কার দেওয়ার জন্য ---
@app.route('/api/reward_ad', methods=['POST'])
def reward_for_ad():
    data = request.json
    user_id = data.get("userId", "default_user")
    ad_id = data.get("adId")
    user = get_user(user_id)

    if ad_id not in ADS_REWARDS:
        return jsonify({"error": "Invalid Ad ID"}), 400
    
    # ব্যবহারকারী এই বিজ্ঞাপনটি আগে দেখে থাকলে আর পয়েন্ট পাবে না (ঐচ্ছিক)
    # if ad_id in user["completed_ads"]:
    #     return jsonify({"error": "Ad already watched for reward"}), 400

    reward = ADS_REWARDS[ad_id]
    user["balance"]["coins"] += reward.get("coins", 0)
    # user["completed_ads"].append(ad_id) # চাইলে এই লাইনটি চালু করতে পারেন

    return jsonify({
        "message": f"Successfully rewarded {reward.get('coins', 0)} coins!",
        "new_balance": user["balance"]
    })

# (বাকি অংশ অপরিবর্তিত)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)