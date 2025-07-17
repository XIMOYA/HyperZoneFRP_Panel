import os
import sys
import datetime
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入数据库模型
from src.models.user import db, User
from src.models.node import Node
from src.models.tunnel import Tunnel
from src.models.verification import EmailVerification
from src.models.log import OperationLog, SystemLog
from src.models.user_group import UserGroup
from src.models.package import Package, UserPackage
from src.models.traffic import TrafficLog, TrafficSummary

# 创建Flask应用
from flask import Flask
app = Flask(__name__)

# 配置数据库
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

def init_db():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建默认管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_active=True,
                email_verified=True,
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(admin)
            
            # 创建默认用户组
            default_group = UserGroup(
                name='默认用户组',
                max_tunnels=3,
                max_traffic=1073741824,  # 1GB
                description='新用户默认分组',
                is_default=True
            )
            db.session.add(default_group)
            
            # 创建基础套餐
            basic_package = Package(
                name='基础套餐',
                price=9.9,
                duration=30,
                max_tunnels=5,
                max_traffic=5368709120,  # 5GB
                description='适合个人使用的基础套餐'
            )
            db.session.add(basic_package)
            
            # 创建标准套餐
            standard_package = Package(
                name='标准套餐',
                price=19.9,
                duration=30,
                max_tunnels=10,
                max_traffic=21474836480,  # 20GB
                description='适合小团队使用的标准套餐'
            )
            db.session.add(standard_package)
            
            # 创建高级套餐
            premium_package = Package(
                name='高级套餐',
                price=49.9,
                duration=30,
                max_tunnels=20,
                max_traffic=107374182400,  # 100GB
                description='适合企业使用的高级套餐'
            )
            db.session.add(premium_package)
            
            # 提交更改
            db.session.commit()
            
            print("数据库初始化成功！")
            print("默认管理员账户：")
            print("  用户名: admin")
            print("  密码: admin123")
        else:
            print("数据库已存在，无需初始化。")

if __name__ == '__main__':
    init_db()

