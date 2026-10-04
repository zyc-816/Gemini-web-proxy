from gemini_webapi import GeminiClient
from fastapi import FastAPI
from openai import models_router
from openai import chat_completion_router


async def getClient():
    client = GeminiClient()
    await client.init(timeout=30, auto_close=True, close_delay=300, auto_refresh=True)
    return client

def main():
    app = FastAPI(title="Gemini-API OpenAI Wrapper")
    app.include_router(models_router)
    app.include_router(chat_completion_router)
    client = getClient()


