@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    current_app.logger.debug(f"Received file")
    if 'file' not in request.files:
        current_app.logger.debug('No file part in the request')
        return 'No file part in the request', 400
    required_fields = ['asset_version_name', 'asset_name', 'user_name', 'task', 'infos']
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
    infos = request.form.get('infos', 'infos')

    try:
        conn = get_db_connection()
        if conn is None:
            current_app.logger.error('Database connection failed')
            return jsonify({'message': 'Database connection failed'}), 500
        cursor = conn.cursor()

        # Récupérer l'user_id
        user_query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(user_query, (user_name,))
        user_result = cursor.fetchone()
        if not user_result:
            return jsonify({"error": f"User '{user_name}' not found"}), 404
        user_id = user_result[0]

        # Calculer la version suivante
        query = """
                SELECT MAX(version) 
                FROM assets 
                WHERE asset_name = %s AND task = %s
            """
        cursor.execute(query, (asset_name, task))
        result = cursor.fetchone()
        max_version = result[0] if result[0] is not None else 0
        next_version = f"v{int(max_version[1:]) + 1}" if max_version else "v1"

        # Insérer dans la table assets et récupérer l'id de l'asset
        insert_query = """
                INSERT INTO assets (name, version, task, user_id, description, asset_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
        cursor.execute(insert_query, (file.filename, next_version, task, user_id, infos, asset_name))
        asset_id = cursor.fetchone()[0]
        conn.commit()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Organiser les fichiers et récupérer leurs chemins
    try:
        if file.filename.endswith('.zip'):
            dest_folder = organize_files.organize_zip(current_app, file, asset_name, asset_version_name, user_name, task, next_version)
            file_paths = organize_files.get_files_from_zip(dest_folder)  # Obtenir les chemins des fichiers extraits
        else:
            dest_folder = organize_files.organize_asset(current_app, file, asset_name, asset_version_name, user_name, task, next_version)
            file_paths = [dest_folder]  # Un seul fichier à insérer

        # Insérer les fichiers dans la table files
        file_insert_query = """
            INSERT INTO files (file_name, file_path, asset_id)
            VALUES (%s, %s, %s)
        """
        for file_path in file_paths:
            cursor.execute(file_insert_query, (file.filename, file_path, asset_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': f'Files extracted and stored at {dest_folder}'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500