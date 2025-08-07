import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# --- App Setup ---
app = Flask(__name__)
CORS(app)

# --- Demo Database (will reset on server restart) ---
# For a real app, use PostgreSQL or Redis on Render
user_data_db = {
    # Default data for a guest user
    'guest_user': {
        'points': 1250.0,
        'coins': 5700000,
        'energy': 500,
        'maxEnergy': 500,
        'last_energy_update': datetime.now().timestamp(),
        'league': 'Gold'
    }
}

# Helper function to get user data safely
def get_user_data(user_id):
    if user_id not in user_data_db:
        # Create a new user with default values if not exists
        user_data_db[user_id] = {
            'points': 0.0, 'coins': 0, 'energy': 500, 'maxEnergy': 500,
            'last_energy_update': datetime.now().timestamp(), 'league': 'Bronze'
        }
    return user_data_db[user_id]

# --- API Routes ---

@app.route('/')
def home():
    """Confirms the server is running."""
    return "PAPA TAP Game API is live!"

@app.route('/api/user_data/<user_id>', methods=['GET'])
def get_full_user_data(user_id):
    """Provides all game data for a specific user."""
    user_data = get_user_data(user_id)
    
    # Regenerate energy based on time passed
    now = datetime.now().timestamp()
    time_passed = now - user_data['last_energy_update']
    energy_to_add = int(time_passed) # 1 energy per second
    
    current_energy = min(user_data['maxEnergy'], user_data['energy'] + energy_to_add)
    user_data['energy'] = current_energy
    user_data['last_energy_update'] = now
    
    return jsonify(user_data)

@app.route('/api/tap', methods=['POST'])
def record_tap():
    """Records user taps and updates points."""
    req_data = request.json
    user_id = req_data.get('userId', 'guest_user')
    taps_count = req_data.get('taps', 0)
    
    if taps_count == 0:
        return jsonify({'error': 'No taps recorded'}), 400

    user_data = get_user_data(user_id)

    # Simple logic: 1 tap = 1 point. Assumes client manages energy.
    user_data['points'] += taps_count
    user_data['energy'] -= taps_count
    
    # Ensure energy doesn't go below zero
    if user_data['energy'] < 0: user_data['energy'] = 0

    user_data['last_energy_update'] = datetime.now().timestamp()
    
    return jsonify({
        'message': f'{taps_count} taps recorded successfully!',
        'new_points': user_data['points'],
        'new_energy': user_data['energy']
    })

# You can later add more routes for Ads, Boosts, etc.

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)