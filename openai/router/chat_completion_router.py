import os
import json
import uuid
import base64
import tempfile
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse


from openai.protocol.chat_completion import (
    ChatCompletionRequest,
    ChatCompletionStreamResponse,
    ChunkChoice,
    DeltaMessage
)

from gemini_webapi import GeminiClient

router = APIRouter()

# ==========================================
# 辅助函数：解析消息历史和提取多模态图片
# ==========================================
async def get_client(request: Request) -> GeminiClient:
    return request.app.state.client

def parse_messages(messages) -> tuple[str, list[str]]:
    """
    将 OpenAI 格式的 messages 转换为 Gemini 支持的单次长文本提示词
    并提取 base64 图片为本地临时文件，以供 files 参数使用
    """
    prompt_parts = []
    file_paths = []
    
    for msg in messages:
        # 转换角色名称
        role_map = {"user": "User", "assistant": "Model", "system": "System Instruction"}
        role = role_map.get(msg.role, "User")
        prompt_parts.append(f"\n--- {role} ---\n")
        
        # 处理纯文本内容
        if isinstance(msg.content, str):
            prompt_parts.append(msg.content)
            
        # 处理多模态内容 (如图片)
        elif isinstance(msg.content, list):
            for part in msg.content:
                if part.type == "text" and part.text:
                    prompt_parts.append(part.text)
                elif part.type == "image_url" and part.image_url:
                    url = part.image_url.url
                    # 处理 Base64 图片 (主流 OpenAI 客户端发送图片的格式)
                    if url.startswith("data:image"):
                        try:
                            header, encoded = url.split(",", 1)
                            ext = header.split(";")[0].split("/")[1]
                            
                            # 保存为临时文件，供 GeminiClient 读取
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
                            temp_file.write(base64.b64decode(encoded))
                            temp_file.close()
                            file_paths.append(temp_file.name)
                        except Exception as e:
                            print(f"解析图片失败: {e}")
                    else:
                        # 如果是 http 链接，直接转为文本让模型处理，或者你可以增加下载逻辑
                        prompt_parts.append(f"[Image URL: {url}]")
                        
    # 添加结束标识，提示模型开始回复
    prompt_parts.append("\n--- Model ---\n")
    return "".join(prompt_parts), file_paths

# ==========================================
# 核心路由：POST /v1/chat/completions
# ==========================================
@router.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest, client: GeminiClient = Depends(get_client)):
    if not request.stream:
        raise HTTPException(status_code=400, detail="此接口目前仅支持流式请求 (stream=True)")

    # 1. 转换请求体中的上下文记录与图片
    prompt, file_paths = parse_messages(request.messages)
    
    # 2. 定义流式生成器函数
    async def sse_generator():
        response_id = f"chatcmpl-{uuid.uuid4().hex}"
        model_name = request.model
        
        try:
            # 标记是否是第一个数据块
            is_first_chunk = True
            async for chunk in client.generate_content_stream(
                prompt, 
                files=file_paths, 
                model=model_name,
                temporary=True
            ):
                if chunk.text_delta:
                    if is_first_chunk:
                        delta = DeltaMessage(role="assistant", content=chunk.text_delta)
                        is_first_chunk = False
                    else:
                        delta = DeltaMessage(content=chunk.text_delta)
                        
                    choice = ChunkChoice(index=0, delta=delta, finish_reason=None)
                    
                    resp = ChatCompletionStreamResponse(
                        id=response_id,
                        model=model_name,
                        choices=[choice]
                    )
                    
                    yield f"data: {resp.model_dump_json(exclude_none=True)}\n\n"
            
            # 生成结束标志
            finish_delta = DeltaMessage()
            finish_choice = ChunkChoice(index=0, delta=finish_delta, finish_reason="stop")
            finish_resp = ChatCompletionStreamResponse(
                id=response_id,
                model=model_name,
                choices=[finish_choice]
            )
            yield f"data: {finish_resp.model_dump_json(exclude_none=True)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = json.dumps({"error": {"message": str(e), "type": "server_error"}})
            yield f"data: {error_msg}\n\n"
            yield "data: [DONE]\n\n"
            
        finally:
            for path in file_paths:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"清理临时文件失败: {path}, 错误: {e}")

    # 3. 返回 FastApi 的 StreamingResponse，指定媒体类型为 text/event-stream
    return StreamingResponse(sse_generator(), media_type="text/event-stream")