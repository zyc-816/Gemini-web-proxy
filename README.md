# 项目介绍
实现gemini网页版反代到newapi，支持账号登录

# 重要说明
- 本项目逆向部分依赖[HanaokaYuzu/Gemini-API](https://github.com/HanaokaYuzu/Gemini-API)，网关使用[QuantumNous/new-api](https://github.com/QuantumNous/new-api)
- 使用本项目可能导致不良后果，包括但不限于gemini账号封禁、谷歌账号封禁等，请自行决定是否使用，本项目概不负责

# 使用说明
1. 在浏览器（推荐使用火狐浏览器）手动登录gemini账号，复制cookie中__Secure-1PSID和__Secure-1PSIDTS的值，填写到.env文件的对应位置
2. 修改docker-compose.yml中的端口（默认本地3000端口）、数据库密码等，详情参见[QuantumNous/new-api](https://github.com/QuantumNous/new-api)
3. 运行```docker compose up -d```
4. 根据端口设置使用nginx等反代（可选）
5. 访问部署的newapi界面，手动添加自定义渠道，配置令牌等