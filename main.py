# -*- coding: utf-8 -*-

import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query


app = FastAPI(
    title="SecSkill Agent Plugin API",
    version="1.1.0"
)

PLUGIN_API_KEY = os.getenv(
    "PLUGIN_API_KEY",
    "secskill_demo_key_change_me"
)


async def verify_plugin_key(
    x_plugin_key: Optional[str] = Header(
        default=None,
        alias="X-Plugin-Key"
    ),
    x_plugin_key_compat: Optional[str] = Header(
        default=None,
        alias="XPluginKey"
    )
):
    provided_key = x_plugin_key or x_plugin_key_compat

    if provided_key != PLUGIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid plugin API key"
        )


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


DEMO_RESOURCES = {
    "SEC-LOG-01": [
        {
            "resource_code": "RES-LOG-001",
            "title": "日志采集与异常识别基础练习",
            "resource_type": "practice",
            "url": "",
            "difficulty": 1,
            "duration_minutes": 30,
            "source_ref": "DEMO-RESOURCE-001（待教师核验）"
        },
        {
            "resource_code": "RES-LOG-002",
            "title": "安全日志分析任务单",
            "resource_type": "task",
            "url": "",
            "difficulty": 2,
            "duration_minutes": 45,
            "source_ref": "DEMO-RESOURCE-002（待教师核验）"
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
            "source_ref": "DEMO-RESOURCE-003（待教师核验）"
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
            "source_ref": "DEMO-RESOURCE-004（待教师核验）"
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
            "source_ref": "DEMO-RESOURCE-005（待教师核验）"
        }
    ]
}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SecSkill Agent Plugin API",
        "version": "1.1.0"
    }


@app.get(
    "/plugin/v1/mastery",
    dependencies=[Depends(verify_plugin_key)]
)
def get_mastery(
    user_external_id: str = Query(
        ...,
        min_length=1,
        max_length=64
    ),
    job_name: str = Query(
        default="网络安全运维工程师",
        max_length=120
    )
):
    items = DEMO_MASTERY.get(
        user_external_id,
        []
    )

    return {
        "count": len(items),
        "items": items
    }


@app.get(
    "/plugin/v1/resource/recommend",
    dependencies=[Depends(verify_plugin_key)]
)
def recommend_resource(
    competency_code: str = Query(
        ...,
        min_length=1,
        max_length=80
    ),
    max_difficulty: int = Query(
        default=3,
        ge=1,
        le=5
    ),
    limit: int = Query(
        default=6,
        ge=1,
        le=20
    )
):
    resources = DEMO_RESOURCES.get(
        competency_code,
        []
    )

    filtered = [
        item
        for item in resources
        if item.get("difficulty", 1) <= max_difficulty
    ]

    filtered = filtered[:limit]

    return {
        "count": len(filtered),
        "items": filtered
    }
