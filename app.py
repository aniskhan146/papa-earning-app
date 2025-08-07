import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# --- অ্যাপ সেটআপ ---
app = Flask(__name__)
CORS(app)

# --- ডেমো ডেটাবেস (সার্ভার রিস্টার্ট হলে ডেটা রিসেট হবে) ---
user_database = {
    "default_user": {
        "profile": {"name": "PAPA Player", "league": "Bronze"},
        "balance": {"coins": 125000.0, "usdt": 0.0, "ton": 0.0},
        "energy": {"current": 500, "max": 500, "last_updated": datetime.now().timestamp()},
        "tap_stats": {"coins_per_tap": 1},
        "completed_tasks": []
    }
}

# --- টাস্কের তালিকা এবং পুরস্কার ---
TASKS = {
    "task1": {"coins": 50000, "usdt": 0.1, "title": "Join our Community"},
    "task2": {"coins": 100000, "usdt": 0.0, "title": "Follow us on X"},
}

def get_user(user_id):
    if user_id not in user_database:
        # নতুন ব্যবহারকারী তৈরি
        user_database[user_id] = user_database["default_user"].copy() 
    return user_database[user_id]

# --- API রুটস ---

@app.route('/')
def home():
    return "PAPA TAP Game API v2 is running!"

@app.route('/api/data/<user_id>', methods=['GET'])
def get_game_data(user_id):
    user = get_user(user_id)
    # শক্তি পুনরুৎপাদন
    time_passed = datetime.now().timestamp() - user["energy"]["last_updated"]
    energy_to_add = int(time_passed)  # প্রতি সেকেন্ডে ১ এনার্জি
    user["energy"]["current"] = min(user["energy"]["max"], user["energy"]["current"] + energy_to_add)
    user["energy"]["last_updated"] = datetime.now().timestamp()
    
    return jsonify(user)

@app.route('/api/tap', methods=['POST'])
def process_taps():
    data = request.json
    user_id = data.get("userId", "default_user")
    tap_count = data.get("taps", 0)
    user = get_user(user_id)
    
    earned_coins = tap_count * user["tap_stats"]["coins_per_tap"]
    user["balance"]["coins"] += earned_coins
    user["energy"]["current"] -= tap_count # প্রতিটি ট্যাপে ১ এনার্জি খরচ
    if user["energy"]["current"] < 0: user["energy"]["current"] = 0
    
    return jsonify({
        "message": f"Earned {earned_coins} coins!",
        "new_coins": user["balance"]["coins"],
        "new_energy": user["energy"]["current"]
    })

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    user_id = data.get("userId", "default_user")
    task_id = data.get("taskId")
    user = get_user(user_id)

    if task_id not in TASKS:
        return jsonify({"error": "Invalid Task ID"}), 400
    if task_id in user["completed_tasks"]:
        return jsonify({"error": "Task already completed"}), 400

    reward = TASKS[task_id]
    user["balance"]["coins"] += reward.get("coins", 0)
    user["balance"]["usdt"] += reward.get("usdt", 0)
    user["completed_tasks"].append(task_id)

    return jsonify({
        "message": "Task completed successfully!",
        "new_balance": user["balance"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)