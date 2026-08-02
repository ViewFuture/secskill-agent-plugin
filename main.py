# -*- coding: utf-8 -*-

import json
import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field


# ============================================================
# 1. FastAPI应用配置
# ============================================================

app = FastAPI(
    title="SecSkill Agent Plugin API",
    description=(
        "岗安智练 SecSkill Agent 插件服务，"
        "提供能力掌握度查询和学习资源推荐接口。"
    ),
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============================================================
# 2. 环境变量与鉴权
# ============================================================

PLUGIN_API_KEY = os.getenv(
    "PLUGIN_API_KEY",
    "secskill_demo_2026_key"
).strip()


async def verify_plugin_key(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization"
    ),
    x_plugin_key: Optional[str] = Header(
        default=None,
        alias="X-Plugin-Key"
    ),
    x_plugin_key_compat: Optional[str] = Header(
        default=None,
        alias="XPluginKey"
    ),
    plugin_key: Optional[str] = Query(
        default=None,
        description="兼容部分平台的Query参数鉴权"
    )
):
    """
    兼容以下鉴权方式：

    1. Authorization: <key>
    2. Authorization: Bearer <key>
    3. X-Plugin-Key: <key>
    4. XPluginKey: <key>
    5. ?plugin_key=<key>
    """

    provided_key = (
        authorization
        or x_plugin_key
        or x_plugin_key_compat
        or plugin_key
        or ""
    ).strip()

    if provided_key.lower().startswith("bearer "):
        provided_key = provided_key[7:].strip()

    if not provided_key or provided_key != PLUGIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid plugin API key"
        )


# ============================================================
# 3. 统一响应模型
# ============================================================

class StringResultResponse(BaseModel):
    """
    星辰工作流工具节点更容易识别简单顶层字段。

    result内部保存一个序列化后的JSON字符串。
    """

    result: str = Field(
        ...,
        description="接口业务结果，内容为严格JSON字符串"
    )


# ============================================================
# 4. 演示掌握度数据
# ============================================================

DEMO_MASTERY = {
    "demo_user": [
        {
            "ability_code": "SEC-LOG-01",
            "ability": "日志采集与异常识别",
            "mastery": 0.35,
            "evidence_count": 2
        },
        {
            "ability_code": "SEC-AUTH-01",
            "ability": "授权与合规",
            "mastery": 0.72,
            "evidence_count": 3
        },
        {
            "ability_code": "SEC-EVD-01",
            "ability": "证据留痕",
            "mastery": 0.50,
            "evidence_count": 1
        },
        {
            "ability_code": "SEC-ROLLBACK-01",
            "ability": "变更与回退",
            "mastery": 0.64,
            "evidence_count": 2
        }
    ]
}


# ============================================================
# 5. 演示学习资源数据
# ============================================================

DEMO_RESOURCES = {
    "SEC-LOG-01": [
        {
            "resource_code": "RES-LOG-001",
            "title": "日志采集与异常识别基础练习",
            "resource_type": "practice",
            "url": "",
            "difficulty": 1,
            "duration_minutes": 30,
            "source_ref": "DEMO-RESOURCE-001（待教师核验）",
            "pass_standard": "",
            "checkpoint": "",
            "remediation": ""
        },
        {
            "resource_code": "RES-LOG-002",
            "title": "安全日志分析任务单",
            "resource_type": "task",
            "url": "",
            "difficulty": 2,
            "duration_minutes": 45,
            "source_ref": "DEMO-RESOURCE-002（待教师核验）",
            "pass_standard": "",
            "checkpoint": "",
            "remediation": ""
        }
    ],
    "SEC-AUTH-01": [
        {
            "resource_code": "RES-AUTH-001",
            "title": "授权边界与合规判断练习",
            "resource_type": "practice",
            "url": "",
            "difficulty": 1,
            "duration_minutes": 25,
            "source_ref": "DEMO-RESOURCE-003（待教师核验）",
            "pass_standard": "",
            "checkpoint": "",
            "remediation": ""
        }
    ],
    "SEC-EVD-01": [
        {
            "resource_code": "RES-EVD-001",
            "title": "验收证据识别与整理练习",
            "resource_type": "practice",
            "url": "",
            "difficulty": 2,
            "duration_minutes": 30,
            "source_ref": "DEMO-RESOURCE-004（待教师核验）",
            "pass_standard": "",
            "checkpoint": "",
            "remediation": ""
        }
    ],
    "SEC-ROLLBACK-01": [
        {
            "resource_code": "RES-ROLLBACK-001",
            "title": "变更与回退基础学习任务",
            "resource_type": "task",
            "url": "",
            "difficulty": 2,
            "duration_minutes": 40,
            "source_ref": "DEMO-RESOURCE-005（待教师核验）",
            "pass_standard": "",
            "checkpoint": "",
            "remediation": ""
        }
    ]
}


# ============================================================
# 6. 基础接口
# ============================================================

@app.get(
    "/",
    summary="插件服务首页"
)
def root():
    return {
        "service": "SecSkill Agent Plugin API",
        "version": "1.2.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get(
    "/health",
    summary="健康检查"
)
def health():
    return {
        "status": "ok",
        "service": "SecSkill Agent Plugin API",
        "version": "1.2.0"
    }


# ============================================================
# 7. 查询能力掌握度
# ============================================================

@app.get(
    "/plugin/v1/mastery",
    response_model=StringResultResponse,
    summary="查询用户岗位能力掌握度",
    description=(
        "按外部用户标识和目标岗位查询能力掌握度。"
        "顶层只返回result字符串，result内部是完整JSON对象。"
    ),
    dependencies=[Depends(verify_plugin_key)]
)
def get_mastery(
    user_external_id: str = Query(
        ...,
        min_length=1,
        max_length=64,
        description="外部用户标识，例如demo_user"
    ),
    job_name: str = Query(
        default="网络安全运维工程师",
        max_length=120,
        description="目标岗位名称"
    )
):
    items = DEMO_MASTERY.get(
        user_external_id,
        []
    )

    payload = {
        "count": len(items),
        "items": items,
        "user_external_id": user_external_id,
        "job_name": job_name
    }

    result_text = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":")
    )

    return StringResultResponse(
        result=result_text
    )


# ============================================================
# 8. 推荐薄弱能力学习资源
# ============================================================

@app.get(
    "/plugin/v1/resource/recommend",
    response_model=StringResultResponse,
    summary="推荐薄弱能力学习资源",
    description=(
        "按能力编码、最高难度和数量限制推荐学习资源。"
        "顶层只返回result字符串，result内部是完整JSON对象。"
    ),
    dependencies=[Depends(verify_plugin_key)]
)
def recommend_resource(
    competency_code: str = Query(
        ...,
        min_length=1,
        max_length=80,
        description="能力编码，例如SEC-LOG-01"
    ),
    max_difficulty: int = Query(
        default=3,
        ge=1,
        le=5,
        description="允许返回的最高资源难度"
    ),
    limit: int = Query(
        default=6,
        ge=1,
        le=20,
        description="最大返回资源数量"
    )
):
    resources = DEMO_RESOURCES.get(
        competency_code,
        []
    )

    filtered = [
        item
        for item in resources
        if int(item.get("difficulty", 1)) <= max_difficulty
    ]

    filtered = filtered[:limit]

    payload = {
        "count": len(filtered),
        "items": filtered,
        "competency_code": competency_code,
        "max_difficulty": max_difficulty,
        "limit": limit
    }

    result_text = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":")
    )

    return StringResultResponse(
        result=result_text
    )
