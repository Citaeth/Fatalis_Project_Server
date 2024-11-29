import os
import zipfile
from flask import jsonify
from pathlib import Path
from werkzeug.utils import secure_filename

def organize_asset(app, file, asset_name, asset_version_name, user_name, task, version):
    """

    :param app:
    :param file:
    :param asset_name:
    :param asset_version_name:
    :param user_name:
    :param task:
    :param version:
    :return:
    """
    destination_path=asset_structure(app, asset_name, user_name, task, version)
    extension = Path(file.filename).suffix
    file_path = os.path.join(destination_path, secure_filename("{}{}".format(asset_version_name, extension)))

    file.save(file_path)
    return destination_path, extension


def asset_structure(app, asset_name, user_name, task, version):
    """
    Create the hierarchy of folder necessary to move the asset in the good place.
    """
    base_path = app.config['BASE_HIERARCHY']
    path = os.path.join(
        base_path,
        secure_filename(asset_name),
        secure_filename(user_name),
        secure_filename(task),
        secure_filename(version)
    )
    os.makedirs(path, exist_ok=True)
    return path


def organize_zip(app, file, asset_name, asset_version_name, user_name, task, version):
    # Sauvegarde temporaire du fichier ZIP
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(zip_path)

    # Extraction et organisation
    try:
        dest_folder = extract_and_organize(app, zip_path, asset_name, user_name, task, version, asset_version_name)
        os.remove(zip_path)
        return dest_folder
    except zipfile.BadZipFile:
        return jsonify({'error': 'Invalid ZIP file'}), 400

def extract_and_organize(app, zip_path, asset_name, user_name, task, version):
    """
    Extrait les fichiers d'une archive ZIP et les organise.
    """
    dest_folder = os.path.join(
        app.config['BASE_HIERARCHY'],
        secure_filename(asset_name),
        secure_filename(user_name),
        secure_filename(task),
        secure_filename(version)
    )
    os.makedirs(dest_folder, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)  # Décompression dans le dossier cible

    return dest_folder