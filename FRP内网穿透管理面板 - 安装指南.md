# FRP内网穿透管理面板 - 安装指南

## 目录

1. [系统要求](#系统要求)
2. [安装方式](#安装方式)
   - [使用Docker Compose安装](#使用docker-compose安装)
   - [手动安装](#手动安装)
3. [配置说明](#配置说明)
4. [启动服务](#启动服务)
5. [更新升级](#更新升级)
6. [故障排除](#故障排除)

## 系统要求

### 最低配置
- CPU: 1核
- 内存: 1GB
- 存储: 10GB
- 操作系统: Ubuntu 18.04+/CentOS 7+/Debian 10+

### 推荐配置
- CPU: 2核+
- 内存: 2GB+
- 存储: 20GB+
- 操作系统: Ubuntu 20.04+/CentOS 8+/Debian 11+

### 软件依赖
- Docker 20.10+和Docker Compose 2.0+（使用Docker安装时）
- Python 3.8+（手动安装时）
- Node.js 16+（手动安装时）
- Nginx（手动安装时）

## 安装方式

### 使用Docker Compose安装

Docker Compose是最简单的安装方式，只需几个命令即可完成安装。

#### 1. 安装Docker和Docker Compose

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose

# CentOS
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. 下载项目文件

```bash
git clone https://github.com/yourusername/frp-panel.git
cd frp-panel
```

#### 3. 配置环境变量

编辑`docker-compose.yml`文件，修改环境变量：

```bash
nano docker-compose.yml
```

需要修改的环境变量：
- `SECRET_KEY`: 应用密钥，用于会话加密
- `JWT_SECRET_KEY`: JWT密钥，用于令牌加密
- `MAIL_SERVER`: 邮件服务器地址
- `MAIL_PORT`: 邮件服务器端口
- `MAIL_USERNAME`: 邮件账户用户名
- `MAIL_PASSWORD`: 邮件账户密码

#### 4. 启动服务

```bash
docker-compose up -d
```

#### 5. 访问管理面板

服务启动后，访问`http://your_server_ip`即可打开管理面板。

初始管理员账户：
- 用户名: admin
- 密码: admin123

首次登录后请立即修改密码。

### 手动安装

如果您不想使用Docker，也可以手动安装。

#### 1. 安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx

# CentOS
sudo yum install -y python3 python3-pip nodejs npm nginx
```

#### 2. 下载项目文件

```bash
git clone https://github.com/yourusername/frp-panel.git
cd frp-panel
```

#### 3. 安装后端依赖

```bash
cd frp_panel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. 初始化数据库

```bash
python src/init_db.py
```

#### 5. 配置环境变量

创建`.env`文件：

```bash
nano .env
```

添加以下内容：

```
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=True
```

#### 6. 安装前端依赖

```bash
cd ../frp-panel-frontend
npm install
```

#### 7. 构建前端

```bash
npm run build
```

#### 8. 配置Nginx

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/frp-panel
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为您的域名或服务器IP

    location / {
        root /path/to/frp-panel-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/frp-panel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. 启动后端服务

创建Systemd服务文件：

```bash
sudo nano /etc/systemd/system/frp-panel.service
```

添加以下内容：

```ini
[Unit]
Description=FRP Panel Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/frp_panel
ExecStart=/path/to/frp_panel/venv/bin/python src/main.py
Restart=always
Environment="PYTHONPATH=/path/to/frp_panel"

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start frp-panel
sudo systemctl enable frp-panel
```

#### 10. 访问管理面板

服务启动后，访问`http://your_server_ip`或`http://your_domain.com`即可打开管理面板。

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|-------|
| SECRET_KEY | Flask应用密钥 | 无，必须设置 |
| JWT_SECRET_KEY | JWT令牌密钥 | 无，必须设置 |
| MAIL_SERVER | 邮件服务器地址 | 无，必须设置 |
| MAIL_PORT | 邮件服务器端口 | 587 |
| MAIL_USERNAME | 邮件账户用户名 | 无，必须设置 |
| MAIL_PASSWORD | 邮件账户密码 | 无，必须设置 |
| MAIL_USE_TLS | 是否使用TLS | True |
| MAIL_USE_SSL | 是否使用SSL | False |
| DATABASE_URI | 数据库URI | sqlite:///src/database/app.db |

### 数据库配置

默认使用SQLite数据库，如需使用其他数据库，请修改`DATABASE_URI`环境变量：

```
# MySQL
DATABASE_URI=mysql://username:password@localhost/frp_panel

# PostgreSQL
DATABASE_URI=postgresql://username:password@localhost/frp_panel
```

### HTTPS配置

如需启用HTTPS，请在Nginx配置中添加SSL证书：

```nginx
server {
    listen 443 ssl;
    server_name your_domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 其他配置...
}
```

## 启动服务

### Docker Compose方式

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动安装方式

```bash
# 启动后端服务
sudo systemctl start frp-panel

# 查看日志
sudo journalctl -u frp-panel -f

# 停止服务
sudo systemctl stop frp-panel
```

## 更新升级

### Docker Compose方式

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build
docker-compose up -d
```

### 手动安装方式

```bash
# 拉取最新代码
git pull

# 更新后端
cd frp_panel
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart frp-panel

# 更新前端
cd ../frp-panel-frontend
npm install
npm run build
```

## 故障排除

### 常见问题

1. **无法访问管理面板**
   - 检查服务是否正常运行
   - 检查防火墙是否开放80端口
   - 检查Nginx配置是否正确

2. **邮件发送失败**
   - 检查邮件服务器配置是否正确
   - 检查邮件账户和密码是否正确
   - 检查邮件服务器是否支持TLS/SSL

3. **数据库连接错误**
   - 检查数据库配置是否正确
   - 检查数据库服务是否运行
   - 检查数据库用户权限

### 查看日志

#### Docker方式

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

#### 手动安装方式

```bash
# 查看后端日志
sudo journalctl -u frp-panel -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
```

### 重置管理员密码

如果忘记管理员密码，可以使用以下命令重置：

```bash
# Docker方式
docker-compose exec backend python src/reset_admin.py

# 手动安装方式
cd frp_panel
source venv/bin/activate
python src/reset_admin.py
```

### 备份数据

```bash
# Docker方式
cp -r ./data /backup/frp-panel-data-$(date +%Y%m%d)

# 手动安装方式
cp frp_panel/src/database/app.db /backup/frp-panel-db-$(date +%Y%m%d).db
```

