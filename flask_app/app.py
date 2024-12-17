import os
from flask import Flask

from routes.add_user_db import add_user_blueprint
from routes.delete_user_db import delete_user_blueprint
from routes.get_users_infos_db import get_users_blueprint
from routes.get_assets_infos_db import get_assets_blueprint
from routes.get_files_infos_db import get_files_blueprint
from routes.flask_upload import upload_blueprint
from routes.flask_download import download_blueprint
from routes.change_asset_status_db import update_asset_blueprint

import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)

UPLOAD_FOLDER = '/srv/Fatalis_Project/FTS/uploads'
BASE_HIERARCHY = '/srv/Fatalis_Project/FTS'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BASE_HIERARCHY, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BASE_HIERARCHY'] = BASE_HIERARCHY

#User gestion
app.register_blueprint(add_user_blueprint, url_prefix='/db_add_user')
app.register_blueprint(delete_user_blueprint, url_prefix='/db_delete_user')

#DB get infos
app.register_blueprint(get_users_blueprint, url_prefix='/db_get_users')
app.register_blueprint(get_assets_blueprint, url_prefix='/db_get_assets')
app.register_blueprint(get_files_blueprint, url_prefix='/db_get_files')

#DB Update asset status
app.register_blueprint(update_asset_blueprint, url_prefix='/db_change_asset_status')

#DB upload/download assets
app.register_blueprint(upload_blueprint, url_prefix='/upload_file')
app.register_blueprint(download_blueprint, url_prefix='/download_file')

if __name__ == "__main__":
    app.logger.debug('Flask app is starting...')
    app.run(debug=True, host="0.0.0.0", port=5000)
