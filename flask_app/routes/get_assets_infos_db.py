from flask import Blueprint, jsonify, current_app
from flask_app.flask_connect_to_db import get_db_connection

get_assets_blueprint = Blueprint('get_assets', __name__)

@get_assets_blueprint.route('/get_assets', methods=['GET'])
def get_assets():
    """
    request to get assets data from assets database, and send it to the user.
    """
    conn = get_db_connection()
    if conn is None:
        current_app.logger.error('Database connection failed')
        return jsonify({'message': 'Database connection failed'}), 500

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM assets;")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        assets_data = {
            'columns': columns,
            'data': [dict(zip(columns, row)) for row in rows]
        }

        return jsonify({'assets': assets_data}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching assets: {str(e)}")
        return jsonify({'message': 'Error fetching assets'}), 500

    finally:
        cur.close()
        conn.close()