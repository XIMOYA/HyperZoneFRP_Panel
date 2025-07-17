# FRP内网穿透管理面板

FRP内网穿透管理面板是一个基于Flask和React的Web应用，用于管理和监控frp内网穿透服务。它提供了用户友好的界面，使用户能够轻松地管理frp服务器节点和隧道，并提供套餐购买、流量统计等增值功能。

## 功能特点

- **用户管理**：注册、登录、邮箱验证、实名认证
- **节点管理**：添加、编辑、删除frp服务器节点，监控节点状态
- **隧道管理**：创建、编辑、删除、启动、停止隧道
- **套餐系统**：套餐购买、管理和续费
- **用户组管理**：基于套餐的用户分组和权限控制
- **流量统计**：实时流量监控、每日流量统计、流量汇总报表
- **美观界面**：基于Ant Design的现代化UI设计

## 技术栈

### 后端
- Python 3.11
- Flask (Web框架)
- MySQL 5.7+ 或 8.0+ (数据库)
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (认证)
- Flask-Mail (邮件服务)
- Flask-CORS (跨域支持)

### 前端
- React 18
- Ant Design (UI组件库)
- React Router (路由)
- Axios (HTTP客户端)
- Recharts (图表库)
- Day.js (日期处理)

## 安装指南
---
详细安装指南
请参阅[详细安装步骤](https://github.com/XIMOYA/HyperZoneFRP_Panel/blob/main/INSTALL_GUIDE.md
---
### 系统要求
- Python 3.8+
- Node.js 16+
- frp 0.37.0+



### 后端安装

1. 克隆仓库
```bash
git clone https://github.com/XIMOYA/HyperZoneFRP_Panel/frp-panel.git
cd frp-panel
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库
```bash
python src/init_db.py
```

5. 配置环境变量
创建`.env`文件并设置以下变量：
```
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=True
```

6. 启动后端服务
```bash
python src/main.py
```

### 前端安装

1. 进入前端目录
```bash
cd frp-panel-frontend
```

2. 安装依赖
```bash
npm install
# 或
yarn install
# 或
pnpm install
```

3. 开发模式启动
```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

4. 构建生产版本
```bash
npm run build
# 或
yarn build
# 或
pnpm build
```

## 部署指南

### 使用Docker部署

1. 构建Docker镜像
```bash
docker build -t frp-panel .
```

2. 运行容器
```bash
docker run -d -p 5000:5000 -p 80:80 --name frp-panel frp-panel
```

### 使用Nginx部署

1. 构建前端
```bash
cd frp-panel-frontend
npm run build
```

2. 配置Nginx
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /path/to/frp-panel-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. 启动后端服务
```bash
cd frp-panel
source venv/bin/activate
python src/main.py
```

4. 使用Supervisor管理后端进程
```ini
[program:frp-panel]
command=/path/to/venv/bin/python /path/to/frp-panel/src/main.py
directory=/path/to/frp-panel
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

## 使用指南

### 管理员账户
初始管理员账户：
- 用户名：admin
- 密码：admin123

首次登录后请立即修改密码。

### 基本使用流程

1. **添加节点**：
   - 登录管理员账户
   - 进入"节点管理"页面
   - 点击"添加节点"按钮
   - 填写frps服务器信息并保存

2. **创建隧道**：
   - 进入"隧道管理"页面
   - 点击"创建隧道"按钮
   - 选择节点并填写隧道信息
   - 保存并启动隧道

3. **查看流量统计**：
   - 进入"流量统计"页面
   - 选择时间范围和隧道
   - 查看流量图表和统计数据

4. **购买套餐**：
   - 进入"套餐购买"页面
   - 选择合适的套餐
   - 完成支付流程

## 常见问题

1. **Q: 如何重置管理员密码？**
   A: 使用以下命令：
   ```bash
   python src/reset_admin.py
   ```

2. **Q: 如何备份数据库？**
   A: 数据库文件位于`src/database/app.db`，直接复制该文件即可备份。

3. **Q: 如何配置邮件服务？**
   A: 在`.env`文件中设置邮件服务器信息，确保SMTP服务可用。

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系：3589564653@qq.com
