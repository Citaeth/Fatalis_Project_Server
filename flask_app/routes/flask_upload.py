from flask import current_app, request, jsonify, Blueprint
from flask_app.flask_connect_to_db import get_db_connection
from flask_app.utils import organize_files

upload_blueprint = Blueprint('upload', __name__)

@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    """
    server request to upload files on server from user UI. It should receive the file, and the information needed to
    fill the assets and files database.
    It will download the file into a "upload" temp directory in FTS project, and build the path depending on the
    information given.
    :return:
    """
    current_app.logger.debug(f"Received file")
    if 'file' not in request.files:
        current_app.logger.debug('No file part in the request')
        return 'No file part in the request', 400
    required_fields = ['asset_version_name', 'asset_name', 'user_name', 'task','status', 'infos']
    missing_fields = [field for field in required_fields if field not in request.form]
    if missing_fields:
        current_app.logger.debug(f'Missing required fields: {", ".join(missing_fields)}')
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    file = request.files['file']
    if file.filename == '':
        current_app.logger.debug('No file selected for upload')
        return 'No file selected for upload', 400

    asset_version_name = request.form.get('asset_version_name', 'unknown_asset')
    asset_name = request.form.get('asset_name', 'unknown_asset')
    user_name = request.form.get('user_name', 'unknown_user')
    task = request.form.get('task', 'unknown_task')
    status = request.form.get('status', 'Ignore')
    infos = request.form.get('infos', 'infos')

    try:
        conn = get_db_connection()
        if conn is None:
            current_app.logger.error('Database connection failed')
            return jsonify({'message': 'Database connection failed'}), 500
        cursor = conn.cursor()

        user_query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(user_query, (user_name,))
        user_result = cursor.fetchone()
        if not user_result:
            return jsonify({"error": f"User '{user_name}' not found"}), 404
        user_id = user_result[0]

        # Look for the new version number of the asset for this task
        query = """
                SELECT MAX(version) 
                FROM assets 
                WHERE asset_name = %s AND task = %s
            """
        cursor.execute(query, (asset_name, task))
        result = cursor.fetchone()
        max_version = result[0] if result[0] is not None else 0
        next_version = f"v{int(max_version[1:]) + 1}" if max_version else "v1"

    except Exception as e:
        current_app.logger.debug("error: {}".format(e))
        return jsonify({"error": str(e)}), 500

    #Check if it's a ZIP file (for group of files), or a simple file.
    try:
        if file.filename.endswith('.zip'):
            dest_folder = organize_files.organize_zip(current_app, file, asset_name, asset_version_name, user_name, task, next_version)
            filename = file.filename
            extension = 'group'
        else:
            dest_folder, extension = organize_files.organize_asset(current_app, file, asset_name, asset_version_name, user_name, task, next_version)
            filename = asset_version_name


        insert_query = """
                        INSERT INTO assets (name, version, task, user_id, description, asset_name, extension, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """
        cursor.execute(insert_query, (filename, next_version, task, user_id, infos, asset_name, extension, status))
        asset_id = cursor.fetchone()[0]
        conn.commit()

        file_insert_query = """
                    INSERT INTO files (file_name, file_path, asset_id)
                    VALUES (%s, %s, %s)
                """
        cursor.execute(file_insert_query, (filename, dest_folder, asset_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': f'Files extracted and stored at {dest_folder}'}), 200
    except Exception as e:
        conn.rollback()
        current_app.logger.debug("error: {}".format(e))
        return jsonify({"error": str(e)}), 500