import os
import sys
import getpass
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入数据库模型
from src.models.user import db, User

# 创建Flask应用
from flask import Flask
app = Flask(__name__)

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "mysql+pymysql://root:password@db:3306/frp_panel") # 默认使用MySQL，如果未设置环境变量则使用此默认值
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

def reset_admin_password():
    """重置管理员密码"""
    with app.app_context():
        # 查找管理员用户
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("错误：未找到管理员账户！")
            return
        
        # 获取新密码
        while True:
            new_password = getpass.getpass("请输入新密码: ")
            confirm_password = getpass.getpass("请确认新密码: ")
            
            if new_password != confirm_password:
                print("错误：两次输入的密码不一致，请重新输入！")
                continue
            
            if len(new_password) < 8:
                print("错误：密码长度必须至少为8个字符！")
                continue
            
            break
        
        # 更新密码
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        print("管理员密码重置成功！")

if __name__ == '__main__':
    reset_admin_password()

