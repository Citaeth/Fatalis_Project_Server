from flask import Blueprint, jsonify, current_app
from flask_app.flask_connect_to_db import get_db_connection

get_files_blueprint = Blueprint('get_files', __name__)

@get_files_blueprint.route('/get_files', methods=['GET'])
def get_files():
    """
    request to get files data information in files database and send it to the user.
    :return:
    """
    conn = get_db_connection()
    if conn is None:
        current_app.logger.error('Database connection failed')
        return jsonify({'message': 'Database connection failed'}), 500

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM files;")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        files_data = {
            'columns': columns,
            'data': [dict(zip(columns, row)) for row in rows]
        }

        return jsonify({'files': files_data}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching files: {str(e)}")
        return jsonify({'message': 'Error fetching files'}), 500

    finally:
        cur.close()
        conn.close()