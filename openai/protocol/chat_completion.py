from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
import time

# ==========================================
# 1. 请求体数据结构 (Request)
# ==========================================

class ImageUrl(BaseModel):
    url: str
    detail: Optional[str] = "auto"

class ContentPart(BaseModel):
    type: str  # "text" 或 "image_url"
    text: Optional[str] = None
    image_url: Optional[ImageUrl] = None

class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant" 等
    # content 可以是简单的纯文本字符串，也可以是多模态的数组（包含文本和图片）
    content: Union[str, List[ContentPart]]
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="要调用的模型名称，例如 gemini-1.5-pro")
    messages: List[ChatMessage] = Field(..., description="至今为止的对话消息列表")
    stream: Optional[bool] = Field(False, description="是否以流式 Server-Sent Events (SSE) 格式返回")
    temperature: Optional[float] = Field(0.7, description="采样温度")
    top_p: Optional[float] = Field(1.0, description="核采样参数")
    max_tokens: Optional[int] = Field(None, description="生成的最大 token 数量")


# ==========================================
# 2. 流式响应数据结构 (Streaming Chunk Response)
# ==========================================

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class ChunkChoice(BaseModel):
    index: int = 0
    delta: DeltaMessage
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChunkChoice]