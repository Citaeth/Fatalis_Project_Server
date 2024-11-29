from flask import Blueprint, jsonify
from flask_app.flask_connect_to_db import get_db_connection

delete_user_blueprint = Blueprint('delete_user', __name__)


@delete_user_blueprint.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user_from_db(user_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed'}), 500

    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
        deleted_user_id = cur.fetchone()

        if deleted_user_id:
            conn.commit()
            return jsonify({'message': f'User with ID {user_id} deleted successfully'}), 200
        else:
            return jsonify({'message': f'User with ID {user_id} not found'}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()