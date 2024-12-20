import os
import zipfile
from flask import Blueprint, jsonify, request, send_file
from flask_app.flask_connect_to_db import get_db_connection

download_blueprint = Blueprint('download', __name__)

@download_blueprint.route('/get_file', methods=['GET'])
def get_file_path():
    """
    request to get the file location path in server, using the asset_id, and send it to the user.
    The database assets (containing information that the user deal with) and files (that contain server information) are
    linked by the asset_id.
    :return:
    """
    asset_id = request.args.get('asset_id')
    if not asset_id:
        return jsonify({"error": "Asset ID is required"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get the file path using asset_id
        query = "SELECT file_path FROM files WHERE asset_id = %s"
        cursor.execute(query, (asset_id,))
        folder_path = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if not os.path.exists(folder_path):
            return jsonify({"error": "No file found for the given asset_id"}), 404

        # Create temporary zip file
        zip_path = os.path.join("/tmp", f"asset_{asset_id}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

        # Send zip file to user
        return send_file(zip_path, as_attachment=True, download_name=f"asset_{asset_id}.zip")

    except Exception as e:
        return jsonify({'error': str(e)}), 500
