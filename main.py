from contextlib import asynccontextmanager

from gemini_webapi import GeminiClient
from fastapi import FastAPI
from openai import models_router
from openai import chat_completion_router
import uvicorn
import os

# 代理设置
# os.environ["HTTP_PROXY"] = ""
# os.environ["HTTPS_PROXY"] = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行：初始化 GeminiClient 并挂载到全局 state
    # 若无火狐浏览器，在.env文件中手动输入对应cookie
    Secure_1PSID = os.getenv("SECURE_1PSID")
    Secure_1PSIDTS = os.getenv("SECURE_1PSIDTS")
    client = GeminiClient(Secure_1PSID, Secure_1PSIDTS)
    # client = GeminiClient()
    await client.init(timeout=30, auto_close=True, close_delay=300, auto_refresh=True)
    app.state.client = client
    yield

app = FastAPI(title="Gemini-API OpenAI Wrapper", lifespan=lifespan)
app.include_router(models_router)
app.include_router(chat_completion_router)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8082)


if __name__ == "__main__":
    main()