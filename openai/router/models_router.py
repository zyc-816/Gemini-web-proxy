# models_router.py
from fastapi import APIRouter, Request, Depends
from gemini_webapi import GeminiClient
from openai.protocol.models import ModelList, ModelCard


router = APIRouter()

# --- 辅助依赖函数：从 app.state 获取 client ---
async def get_client(request: Request) -> GeminiClient:
    return request.app.state.client

@router.get("/v1/models", response_model=ModelList)
async def list_models(client: GeminiClient = Depends(get_client)):
    """
    返回可用的模型列表。
    通过调用 GeminiClient 动态获取账户支持的模型。
    """
    # 调用 GeminiClient 的动态获取模型方法
    available_gemini_models = client.list_models()
    
    # 将获取到的模型信息转换为 OpenAI 格式的 ModelCard 列表
    model_cards = []
    
    if available_gemini_models:
        for model in available_gemini_models:
            model_id = model.model_name
            model_cards.append(
                ModelCard(id=model_id, owned_by="google")
            )
            
    return ModelList(data=model_cards)