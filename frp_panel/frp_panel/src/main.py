import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db
from src.models.node import Node
from src.models.tunnel import Tunnel
from src.models.verification import EmailVerification
from src.models.log import OperationLog, SystemLog
from src.models.user_group import UserGroup
from src.models.package import Package, UserPackage
from src.models.traffic import TrafficLog, TrafficSummary
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.nodes import nodes_bp
from src.routes.tunnels import tunnels_bp
from src.routes.packages import packages_bp
from src.routes.user_groups import user_groups_bp
from src.routes.traffic import traffic_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-me'

# 启用CORS支持
CORS(app)

# 初始化JWT
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(nodes_bp, url_prefix='/api')
app.register_blueprint(tunnels_bp, url_prefix='/api')
app.register_blueprint(packages_bp, url_prefix='/api')
app.register_blueprint(user_groups_bp, url_prefix='/api')
app.register_blueprint(traffic_bp, url_prefix='/api')

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
