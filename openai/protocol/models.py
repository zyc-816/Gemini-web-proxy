from typing import List
from pydantic import BaseModel, Field
import time

# ==========================================
# 4. 模型列表响应数据结构 (Model List Response)
# ==========================================

class ModelCard(BaseModel):
    id: str = Field(..., description="模型标识符，例如 'gemini-1.5-pro'，供客户端在请求中引用")
    object: str = Field("model", description="对象类型，固定为 'model'")
    created: int = Field(default_factory=lambda: int(time.time()), description="模型创建的 Unix 时间戳")
    owned_by: str = Field("google", description="模型所属的组织机构，这里可以写 'google'")

class ModelList(BaseModel):
    object: str = Field("list", description="对象类型，固定为 'list'")
    data: List[ModelCard] = Field(..., description="模型对象列表")