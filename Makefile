# 目标: 启动服务器
start-server:
	@uvicorn main:app --host=0.0.0.0 --port=8000 --reload

# 目标: 关闭服务器
stop-server:
	@pkill -f "uvicorn"

# 目标: 发送 POST 请求
run:
	@curl -v -X POST "http://127.0.0.1:8000/api/layout/generate" \
	-H "Content-Type: application/json" \
	-d @test.json
#启动网页服务器

html:
	@python -m http.server 8001

# 开头执行初始化
all:
	@make start-server &
	sleep 3  # 等待服务器启动
	@make run

