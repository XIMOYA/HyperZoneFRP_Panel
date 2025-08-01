# FRP内网穿透管理面板 - 用户手册

## 目录

1. [简介](#简介)
2. [账户管理](#账户管理)
3. [节点管理](#节点管理)
4. [隧道管理](#隧道管理)
5. [套餐购买](#套餐购买)
6. [流量统计](#流量统计)
7. [常见问题](#常见问题)

## 简介

FRP内网穿透管理面板是一个功能强大且用户友好的Web应用，旨在帮助您轻松管理和监控frp内网穿透服务。无论您是个人开发者、小团队还是企业用户，都可以通过这个面板来简化frp的配置和使用。

**核心功能：**

- **直观的Web界面**：告别繁琐的命令行配置，通过图形化界面轻松管理所有frp节点和隧道。
- **多用户支持**：支持多用户注册和登录，每个用户可以管理自己的隧道。
- **权限控制**：管理员可以管理所有节点和用户，普通用户只能管理自己的隧道。
- **套餐系统**：通过购买套餐来获取更多的隧道数量、流量配额和更快的速率。
- **流量统计**：实时监控每个隧道的流量使用情况，提供详细的流量报表。
- **美观易用**：基于Ant Design的现代化UI设计，提供流畅的操作体验。

## 账户管理

### 注册账户

1. 打开管理面板的登录页面，点击右上角的“注册”标签。
2. 填写您的用户名、邮箱地址和密码。
3. 点击“发送验证码”按钮，系统会向您填写的邮箱发送一封包含验证码的邮件。
4. 查收邮件，将收到的验证码填入输入框中。
5. 点击“注册”按钮，即可完成账户创建。

### 登录账户

1. 打开管理面板的登录页面。
2. 输入您的用户名或邮箱地址和密码。
3. 点击“登录”按钮即可进入管理面板。

### 实名认证

为了符合相关法规要求，部分功能可能需要进行实名认证。

1. 登录后，点击页面右上角的用户头像，在下拉菜单中选择“个人资料”。
2. 在个人资料页面，找到“实名认证”部分，点击“立即认证”按钮。
3. 按照提示，填写真实姓名和身份证号码。
4. 点击“提交”按钮，等待系统审核。

## 节点管理

节点是指运行frps服务的服务器。所有用户都可以查看节点列表，但只有管理员可以添加、编辑和删除节点。

### 查看节点列表

1. 登录后，在左侧菜单中点击“节点管理”。
2. 页面将展示所有可用的frps节点列表，包括节点名称、服务器地址、状态、区域等信息。

### 添加节点（仅管理员）

1. 在节点管理页面，点击右上角的“添加节点”按钮。
2. 在弹出的对话框中，填写节点信息：
   - **节点名称**：为节点起一个易于识别的名称，例如“香港节点”、“美国节点”。
   - **服务器地址**：frps服务器的IP地址或域名。
   - **服务端口**：frps服务的端口，默认为7000。
   - **Dashboard端口**：frps的Dashboard端口，默认为7500。
   - **Dashboard用户名和密码**：frps Dashboard的登录凭据。
   - **认证Token**：frps的认证Token，用于客户端连接。
   - **区域**：节点所在的地理区域，例如“亚洲”、“北美”。
   - **描述**：节点的其他说明信息。
3. 点击“创建”按钮保存节点。

### 编辑节点（仅管理员）

1. 在节点列表中，找到要编辑的节点，点击操作列中的“编辑”按钮。
2. 在弹出的对话框中修改节点信息。
3. 点击“更新”按钮保存修改。

### 删除节点（仅管理员）

1. 在节点列表中，找到要删除的节点，点击操作列中的“删除”按钮。
2. 在弹出的确认对话框中点击“确定”。

### 查看节点状态

1. 在节点列表中，找到要查看的节点，点击操作列中的“查看状态”按钮。
2. 系统将显示节点的详细状态信息，包括服务器信息、在线代理列表等。

## 隧道管理

隧道是将您的内网服务暴露到公网的通道。您可以为您的网站、远程桌面、SSH等服务创建隧道。

### 查看隧道列表

1. 登录后，在左侧菜单中点击“隧道管理”。
2. 页面将展示您创建的所有隧道列表，包括隧道名称、类型、本地地址、远程端口、状态等信息。

### 创建隧道

1. 在隧道管理页面，点击右上角的“创建隧道”按钮。
2. 在弹出的对话框中，填写隧道信息：
   - **隧道名称**：为隧道起一个易于识别的名称，例如“我的网站”、“远程桌面”。
   - **隧道类型**：选择TCP、UDP、HTTP或HTTPS。
   - **本地IP**：您内网服务的IP地址，通常是`127.0.0.1`。
   - **本地端口**：您内网服务的端口，例如网站的80端口、SSH的22端口。
   - **远程端口**：您希望通过公网访问的端口。如果留空，系统会自动为您分配一个端口。
   - **选择节点**：选择一个可用的frps节点。
   - **子域名**（仅HTTP/HTTPS类型）：如果您想通过子域名访问您的服务，可以在这里设置。
   - **自定义域名**（仅HTTP/HTTPS类型）：如果您有自己的域名，可以在这里绑定。
   - **描述**：隧道的其他说明信息。
3. 点击“创建”按钮保存隧道。

### 编辑隧道

1. 在隧道列表中，找到要编辑的隧道，点击操作列中的“编辑”按钮。
2. 在弹出的对话框中修改隧道信息。
3. 点击“更新”按钮保存修改。

### 删除隧道

1. 在隧道列表中，找到要删除的隧道，点击操作列中的“删除”按钮。
2. 在弹出的确认对话框中点击“确定”。

### 启动/停止隧道

1. 在隧道列表中，找到要操作的隧道。
2. 点击操作列中的“启动”按钮来启动隧道，或点击“停止”按钮来停止隧道。

### 批量操作

1. 在隧道列表中，勾选您想要操作的多个隧道。
2. 点击列表上方的“批量启动”、“批量停止”或“批量删除”按钮。
3. 在弹出的确认对话框中点击“确定”。

## 套餐购买

通过购买套餐，您可以获得更多的隧道数量、更大的流量配额和更快的网络速率。

### 查看套餐列表

1. 登录后，在左侧菜单中点击“套餐购买”。
2. 页面将展示所有可用的套餐列表，包括套餐名称、价格、有效期、隧道数量、流量限制等详细信息。

### 购买套餐

1. 在套餐列表中，选择您需要的套餐，点击“立即购买”按钮。
2. 在弹出的确认对话框中，选择您的支付方式（例如支付宝、微信支付）。
3. 点击“确认支付”按钮，按照提示完成支付流程。

### 查看我的套餐

1. 在“套餐购买”页面，您可以看到“我的套餐”区域。
2. 这里会显示您当前已购买的所有套餐信息，包括套餐的开始时间、结束时间、已用流量等。

## 流量统计

流量统计功能可以帮助您详细了解每个隧道的流量使用情况。

### 查看流量汇总

1. 登录后，在左侧菜单中点击“流量统计”。
2. 页面顶部会以卡片的形式显示您的总上传流量、总下载流量和总使用流量。

### 查看每日流量统计

1. 在流量统计页面，您可以看到“每日流量统计”图表。
2. 您可以通过下拉菜单选择要查看的隧道（所有隧道或单个隧道）、时间范围（最近7天或最近30天）以及图表类型（面积图、折线图、柱状图）来查看不同的统计数据。

### 查看实时流量监控

1. 在流量统计页面，您可以看到“实时流量监控”图表。
2. 该图表会实时显示最近10分钟的流量数据，帮助您了解当前的流量使用情况。

### 查看隧道流量表格

1. 在流量统计页面底部，您可以看到“隧道流量统计”表格。
2. 该表格会列出您每个隧道的详细流量使用情况，包括上传流量、下载流量、总流量以及占总流量的百分比。

## 常见问题

### 如何修改密码？

1. 点击页面右上角的用户头像，在下拉菜单中选择“个人资料”。
2. 在个人资料页面，找到“修改密码”部分。
3. 输入您的当前密码和新密码。
4. 点击“保存”按钮即可完成密码修改。

### 如何查看隧道的连接状态？

在“隧道管理”页面的隧道列表中，每个隧道都有一个状态列，显示了隧道的当前状态：
- **绿色“运行中”**：表示隧道已成功连接并正常运行。
- **灰色“已停止”**：表示隧道已手动停止或未启动。
- **红色“错误”**：表示隧道连接出现错误，请检查您的配置或网络连接。

### 如何解决隧道连接失败的问题？

1. **检查本地服务**：确保您要穿透的内网服务（例如网站、SSH服务）正在本地正常运行。
2. **检查本地IP和端口**：在隧道配置中，确保您填写的本地IP和端口是正确的。
3. **检查节点状态**：在“节点管理”页面，检查您使用的节点是否处于在线状态。
4. **检查网络连接**：确保您的本地设备和frps服务器之间的网络连接是稳定的。
5. **查看日志**：检查frpc客户端的日志，获取详细的错误信息。
6. **尝试重启**：尝试在管理面板中停止并重新启动隧道。

### 如何联系客服？

如果您在使用过程中遇到任何问题或有任何建议，请通过以下方式联系我们：
- **邮箱**：3589564653@qq.com
- **在线客服**：在管理面板右下角点击“客服”按钮

