from contextlib import asynccontextmanager

from gemini_webapi import GeminiClient
from fastapi import FastAPI
from openai import models_router
from openai import chat_completion_router
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行：初始化 GeminiClient 并挂载到全局 state
    client = GeminiClient()
    await client.init(timeout=30, auto_close=True, close_delay=300, auto_refresh=True)
    app.state.client = client
    yield

app = FastAPI(title="Gemini-API OpenAI Wrapper")
app.include_router(models_router)
app.include_router(chat_completion_router)

def main():
    uvicorn.run(app, host="127.0.0.1", port=8082)


if __name__ == "__main__":
    main()