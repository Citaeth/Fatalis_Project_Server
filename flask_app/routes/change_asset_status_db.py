from flask import Blueprint, request, jsonify, current_app
from flask_app.flask_connect_to_db import get_db_connection

update_asset_blueprint = Blueprint('update_asset_status', __name__)

@update_asset_blueprint.route('/update_asset_status', methods=['PUT'])
def update_asset_status():
    """
    Request who allow to the client user to change the status of a selected assets (ex: WIP, Awaiting Feedback...)
    :return: a json message, depending on the fail or succeed of the request.
    """
    data = request.get_json()
    if not data or 'asset_id' not in data or 'status' not in data:
        return jsonify({'message': 'Invalid request. "asset_id" and "status" are required.'}), 400

    asset_id = data['asset_id']
    status = data['status']

    connection = get_db_connection()
    if connection is None:
        current_app.logger.error('Database connection failed')
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE assets SET status = %s WHERE id = %s;",
            (status, asset_id)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'message': 'Asset not found or no change made.'}), 404

        return jsonify({'message': 'Asset status updated successfully.'}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating asset status: {str(e)}")
        return jsonify({'message': 'Error updating asset status'}), 500

    finally:
        cursor.close()
        connection.close()