from flask import Blueprint, request, jsonify, current_app
from flask_app.flask_connect_to_db import get_db_connection

add_user_blueprint = Blueprint('add_user', __name__)

@add_user_blueprint.route('/add_user', methods=['POST'])
def add_user_to_db():
    username = request.json.get('username')
    current_app.logger.debug(f"Received username: {username}")

    conn = get_db_connection()
    if conn is None:
        current_app.logger.error('Database connection failed')
        return jsonify({'message': 'Database connection failed'}), 500

    cur = conn.cursor()

    try:
        current_app.logger.debug('Executing INSERT query')
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
        user_id = cur.fetchone()[0]
        current_app.logger.debug(f"User added with ID: {user_id}")
        conn.commit()
        return jsonify({'message': 'User added successfully', 'user_id': user_id}), 201
    except Exception as e:
        current_app.logger.error(f"Error while inserting user: {str(e)}")
        conn.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()