## 程序启动
```
程序启动的时候用supervisor来保持程序的启动状态
```
## 安装
```
supervisor
```
## 设置
```
这个地方设置启动的一些配置
[program:blades]
command=/home/logs/yoursoftware/venv/bin/gunicorn -w4 -b0.0.0.0:5000 multi-bar:app
directory=/home/logs/yoursoftware
stdout_logfile=/var/log/yoursoftware/output.log
autostart=true
autorestart=true
startsecs=5
priority=1
stopasgroup=true
killasgroup=true
```
## 启动&&停止
```
supervisorctl start blades
supervisorctl start blades
```
