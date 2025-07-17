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
- MySQL 5.7+ 或 8.0+ (如果选择MySQL作为数据库)

## 安装方式

### 使用Docker Compose安装

Docker Compose是最简单的安装方式，只需几个命令即可完成安装。它会自动为您设置好后端、前端和数据库（如果使用默认的SQLite）。如果您想使用MySQL，请参考[配置说明](#配置说明)部分。

#### 1. 安装Docker和Docker Compose

请根据您的操作系统，参考Docker官方文档安装Docker Engine和Docker Compose：
- [Docker官方安装指南](https://docs.docker.com/engine/install/)
- [Docker Compose官方安装指南](https://docs.docker.com/compose/install/)

```bash
# 示例：Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker-compose --version
```

#### 2. 下载项目文件

```bash
git clone https://github.com/XIMOYA/HyperZoneFRP_Panel/frp-panel.git
cd frp-panel
```

#### 3. 配置环境变量

编辑`docker-compose.yml`文件，修改环境变量。这些变量将传递给后端服务。

```bash
nano docker-compose.yml
```

找到 `backend` 服务下的 `environment` 部分，根据您的实际情况修改以下变量：

```yaml
    environment:
      - SECRET_KEY=your_flask_secret_key_here # Flask应用密钥，请替换为随机生成的字符串
      - JWT_SECRET_KEY=your_jwt_secret_key_here # JWT令牌密钥，请替换为随机生成的字符串
      - MAIL_SERVER=smtp.example.com # 您的SMTP邮件服务器地址
      - MAIL_PORT=587 # 邮件服务器端口，通常是587或465
      - MAIL_USERNAME=your_email@example.com # 您的邮件账户用户名
      - MAIL_PASSWORD=your_email_password # 您的邮件账户密码
      - MAIL_USE_TLS=True # 是否使用TLS加密，通常为True
      # - MAIL_USE_SSL=False # 是否使用SSL加密，如果使用TLS则通常为False
      # - DATABASE_URI=mysql+pymysql://root:password@db:3306/frp_panel # 如果使用MySQL，请取消注释并修改为您的MySQL连接字符串
```

**重要提示**：请务必将 `SECRET_KEY` 和 `JWT_SECRET_KEY` 替换为长而复杂的随机字符串，以确保应用安全。

#### 4. 启动服务

在项目根目录下运行以下命令启动所有服务：

```bash
docker-compose up -d
```

这将会在后台启动后端API服务、前端Web服务以及（如果使用默认SQLite）数据库服务。首次启动可能需要一些时间来下载镜像和构建。

#### 5. 访问管理面板

服务启动并运行后，您可以通过浏览器访问您的服务器IP地址或域名来打开管理面板：

`http://your_server_ip` 或 `http://your_domain.com`

初始管理员账户：
- 用户名: admin
- 密码: admin123

**强烈建议您首次登录后立即修改管理员密码！**

### 手动安装

如果您不想使用Docker，也可以手动安装。这需要您手动配置Python环境、Node.js环境、Nginx和数据库。

#### 1. 安装系统依赖

根据您的操作系统安装Python、Node.js、Nginx以及MySQL客户端库（如果使用MySQL）：

```bash
# 示例：Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx
# 如果使用MySQL，还需要安装MySQL客户端开发库
sudo apt install -y libmysqlclient-dev

# 示例：CentOS
sudo yum install -y python3 python3-pip nodejs npm nginx
# 如果使用MySQL，还需要安装MySQL客户端开发库
sudo yum install -y mysql-devel
```

#### 2. 下载项目文件

```bash
git clone https://github.com/XIMOYA/HyperZoneFRP_Panel/frp-panel.git
cd frp-panel
```

#### 3. 安装后端依赖

进入后端项目目录，创建并激活Python虚拟环境，然后安装所需的Python库：

```bash
cd frp_panel
python3 -m venv venv
source venv/bin/activate # Linux/macOS
# 或 venv\Scripts\activate # Windows
pip install -r requirements.txt
```

#### 4. 初始化数据库

**重要提示**：在初始化数据库之前，请确保您的MySQL服务已经运行，并且您已经在MySQL中创建了相应的数据库和用户（如果使用MySQL）。

```bash
# 如果使用MySQL，请确保DATABASE_URI环境变量已设置或在init_db.py中修改为正确的MySQL连接字符串
# 例如：export DATABASE_URI="mysql+pymysql://root:password@127.0.0.1:3306/frp_panel"
python src/init_db.py
```

这将创建所有必要的数据库表，并初始化默认的管理员账户、用户组和套餐数据。

#### 5. 配置环境变量

在 `frp_panel` 目录下创建一个 `.env` 文件，并添加以下内容。这些变量将用于后端服务。

```ini
SECRET_KEY=your_flask_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=True
# MAIL_USE_SSL=False

# 如果使用MySQL，请设置以下变量
DATABASE_URI=mysql+pymysql://root:password@127.0.0.1:3306/frp_panel
```

请务必替换所有 `your_..._here` 和 `your_email...` 为您的实际信息。

#### 6. 安装前端依赖

进入前端项目目录，安装Node.js依赖：

```bash
cd ../frp-panel-frontend
pnpm install # 或者 npm install / yarn install
```

#### 7. 构建前端

```bash
pnpm run build # 或者 npm run build / yarn build
```

这将生成用于生产环境的静态文件，位于 `dist` 目录下。

#### 8. 配置Nginx

Nginx将作为反向代理，将前端请求和API请求分别转发到前端静态文件和后端服务。创建一个Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/frp-panel
```

添加以下内容，并根据您的实际情况修改 `your_domain.com` 和 `/path/to/frp-panel-frontend/dist`：

```nginx
server {
    listen 80;
    server_name your_domain.com; # 替换为您的域名或服务器IP

    # 前端静态文件
    location / {
        root /path/to/frp-panel-frontend/dist; # 替换为前端dist目录的绝对路径
        try_files $uri $uri/ /index.html;
    }

    # API代理，转发到后端Flask服务
    location /api {
        proxy_pass http://127.0.0.1:5000; # 后端Flask服务地址和端口
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

创建软链接并测试Nginx配置，然后重启Nginx服务：

```bash
sudo ln -s /etc/nginx/sites-available/frp-panel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. 启动后端服务

为了让后端服务在后台持续运行，建议使用Systemd进行管理。创建一个Systemd服务文件：

```bash
sudo nano /etc/systemd/system/frp-panel.service
```

添加以下内容，并根据您的实际情况修改 `/path/to/venv/bin/python` 和 `/path/to/frp-panel`：

```ini
[Unit]
Description=FRP Panel Backend
After=network.target

[Service]
User=www-data # 运行服务的用户，可以根据实际情况修改
WorkingDirectory=/path/to/frp-panel/frp_panel # 后端项目根目录
ExecStart=/path/to/frp-panel/frp_panel/venv/bin/python src/main.py # 虚拟环境中的Python解释器路径和main.py路径
Restart=always
Environment="PYTHONPATH=/path/to/frp-panel/frp_panel" # 设置PYTHONPATH，确保模块能被正确导入

[Install]
WantedBy=multi-user.target
```

重新加载Systemd配置，启动并启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start frp-panel
sudo systemctl enable frp-panel
```

#### 10. 访问管理面板

服务启动后，访问 `http://your_server_ip` 或 `http://your_domain.com` 即可打开管理面板。

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|-------|
| SECRET_KEY | Flask应用密钥，用于会话加密和数据签名。**务必替换为随机生成的字符串。** | 无，必须设置 |
| JWT_SECRET_KEY | JWT令牌密钥，用于生成和验证用户认证令牌。**务必替换为随机生成的字符串。** | 无，必须设置 |
| MAIL_SERVER | 邮件服务器地址，用于发送注册验证码、密码重置等邮件。 | 无，必须设置 |
| MAIL_PORT | 邮件服务器端口，通常是587（TLS）或465（SSL）。 | 587 |
| MAIL_USERNAME | 邮件账户用户名，用于登录SMTP服务器。 | 无，必须设置 |
| MAIL_PASSWORD | 邮件账户密码，用于登录SMTP服务器。 | 无，必须设置 |
| MAIL_USE_TLS | 是否使用TLS加密连接邮件服务器。 | True |
| MAIL_USE_SSL | 是否使用SSL加密连接邮件服务器。如果`MAIL_USE_TLS`为True，此项通常为False。 | False |
| DATABASE_URI | 数据库连接URI。默认配置为MySQL，如果未设置此环境变量，将使用`mysql+pymysql://root:password@db:3306/frp_panel`作为默认值。**强烈建议在生产环境中使用环境变量设置此项。** | `mysql+pymysql://root:password@db:3306/frp_panel` |

### 数据库配置

项目默认配置为使用MySQL数据库。您可以通过设置 `DATABASE_URI` 环境变量来指定不同的数据库连接。

**MySQL连接示例：**

```
DATABASE_URI=mysql+pymysql://username:password@host:port/database_name
```

- `username`: 您的MySQL用户名
- `password`: 您的MySQL密码
- `host`: MySQL服务器地址（例如：`localhost` 或 `127.0.0.1`，如果是Docker Compose内部服务，则为`db`）
- `port`: MySQL服务端口，默认为3306
- `database_name`: 您在MySQL中创建的数据库名称

**SQLite连接示例（如果您想切换回SQLite）：**

```
DATABASE_URI=sqlite:///path/to/your/database/app.db
```

- `path/to/your/database/app.db`: SQLite数据库文件的绝对路径。

### HTTPS配置

为了生产环境的安全，强烈建议为您的管理面板启用HTTPS。您可以通过Nginx配置SSL证书来实现：

```nginx
server {
    listen 443 ssl;
    server_name your_domain.com;

    ssl_certificate /path/to/your/fullchain.pem; # 您的SSL证书路径
    ssl_certificate_key /path/to/your/private.key; # 您的SSL私钥路径

    # 其他Nginx配置，与HTTP部分类似
    location / {
        root /path/to/frp-panel-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 可选：将HTTP请求重定向到HTTPS
server {
    listen 80;
    server_name your_domain.com;
    return 301 https://$host$request_uri;
}
```

## 启动服务

### Docker Compose方式

```bash
# 启动所有服务（-d 表示后台运行）
docker-compose up -d

# 查看所有服务的日志
docker-compose logs -f

# 停止并移除所有服务
docker-compose down
```

### 手动安装方式

```bash
# 启动后端服务
sudo systemctl start frp-panel

# 查看后端服务日志
sudo journalctl -u frp-panel -f

# 停止后端服务
sudo systemctl stop frp-panel

# 启动Nginx服务
sudo systemctl start nginx

# 查看Nginx服务日志
sudo tail -f /var/log/nginx/error.log
```

## 更新升级

### Docker Compose方式

```bash
# 停止并移除旧服务
docker-compose down

# 拉取最新代码
git pull

# 重新构建镜像（如果Dockerfile有更新）
docker-compose build

# 启动新服务
docker-compose up -d
```

### 手动安装方式

```bash
# 拉取最新代码
git pull

# 更新后端依赖（如果requirements.txt有更新）
cd frp_panel
source venv/bin/activate
pip install -r requirements.txt

# 重启后端服务
sudo systemctl restart frp-panel

# 更新前端依赖（如果package.json或pnpm-lock.yaml有更新）
cd ../frp-panel-frontend
pnpm install # 或者 npm install / yarn install

# 重新构建前端
pnpm run build # 或者 npm run build / yarn build

# 重新加载Nginx配置并重启（如果Nginx配置有更新）
sudo nginx -t
sudo systemctl reload nginx
```

## 故障排除

### 常见问题

1. **无法访问管理面板**
   - 检查后端和前端服务是否正常运行（`docker-compose ps` 或 `sudo systemctl status frp-panel nginx`）
   - 检查防火墙是否开放了80（HTTP）或443（HTTPS）端口
   - 检查Nginx配置是否正确，特别是 `root` 路径和 `proxy_pass` 地址
   - 检查 `docker-compose.yml` 或 `.env` 文件中的端口映射和环境变量是否正确

2. **邮件发送失败**
   - 检查 `.env` 或 `docker-compose.yml` 中邮件服务器的配置（`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_USE_SSL`）
   - 确保您的邮件账户允许通过SMTP发送邮件，并且密码正确
   - 检查服务器的网络连接，确保可以访问邮件服务器

3. **数据库连接错误**
   - **MySQL**: 确保MySQL服务正在运行，并且您在 `DATABASE_URI` 中提供的用户名、密码、主机、端口和数据库名称都正确。
   - **SQLite**: 确保 `app.db` 文件有正确的读写权限，并且路径正确。
   - 检查后端服务日志（`docker-compose logs backend` 或 `sudo journalctl -u frp-panel -f`）以获取详细错误信息。

4. **前端页面空白或加载失败**
   - 检查前端服务是否正常运行（`docker-compose ps` 或 `nginx` 状态）
   - 检查浏览器控制台是否有JavaScript错误或网络请求失败
   - 确保Nginx的 `root` 路径指向了正确的前端 `dist` 目录
   - 尝试清除浏览器缓存

### 查看日志

#### Docker方式

```bash
# 查看后端服务日志
docker-compose logs -f backend

# 查看前端服务日志
docker-compose logs -f frontend
```

#### 手动安装方式

```bash
# 查看后端服务日志
sudo journalctl -u frp-panel -f

# 查看Nginx服务日志
sudo tail -f /var/log/nginx/error.log
```

### 重置管理员密码

如果忘记管理员密码，可以使用以下命令重置。请在后端项目根目录 `frp_panel` 下执行：

```bash
# Docker方式
docker-compose exec backend python src/reset_admin.py

# 手动安装方式
cd frp_panel
source venv/bin/activate
python src/reset_admin.py
```

### 备份数据

定期备份您的数据库文件非常重要。

```bash
# Docker方式 (假设您的数据卷映射到 ./data 目录)
cp -r ./data /backup/frp-panel-data-$(date +%Y%m%d)

# 手动安装方式 (SQLite)
cp frp_panel/src/database/app.db /backup/frp-panel-db-$(date +%Y%m%d).db

# 手动安装方式 (MySQL) - 请使用mysqldump工具备份
mysqldump -u your_mysql_user -p your_database_name > /backup/frp-panel-mysql-$(date +%Y%m%d).sql
```

