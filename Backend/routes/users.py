
from flask import Blueprint, request, jsonify
from config.db import get_db_connection

users_bp = Blueprint('users', __name__)

#endpoint for google login
@users_bp.route('/google-login', methods=['POST'])
def google_login():
    #data from the request body
    data = request.get_json()

    #getting the google_id, email and username from the request data
    google_id = data.get('google_id')
    email = data.get('email')
    username = data.get('username')

    if not google_id or not email or not username:
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, google_id, email, username FROM users WHERE google_id = %s", (google_id,))
    
    user = cursor.fetchone()

    if user:
        cursor.close()
        conn.close()
        return jsonify({
            'user_id': user[0],
            'google_id': user[1],
            'email': user[2],
            'username': user[3]
        })
    
    #create a new user if not exists
    cursor.execute("INSERT INTO users (google_id, email, username) VALUES (%s, %s, %s) RETURNING user_id", (google_id, email, username))
    
    new_user_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "User created successfully",
        "user_id": new_user_id,
        "google_id": google_id,
        "email": email,
        "username": username
    })
    
