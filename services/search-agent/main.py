from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from agent import SearchAgent
from models import (
    APIResponse,
    CancelTaskResult,
    ClassifyRequest,
    ClassifyResult,
    Pagination,
    SearchResultsResponseData,
    SearchStartRequest,
    SearchStartResult,
    SearchStatusData,
    SearchSummary,
)

app = FastAPI(title="Search Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = SearchAgent()

# MVP：内存任务表（容器重启会丢，后面可换 Redis/Celery）
TASKS: dict[str, dict[str, Any]] = {}


@app.get("/api/health")
async def health() -> APIResponse:
    return APIResponse(data={"status": "ok", "service": "search-agent", "time": datetime.utcnow().isoformat() + "Z"})


@app.post("/api/search/classify")
async def classify(req: ClassifyRequest) -> APIResponse:
    data = await agent.classify(req.concept, req.max_disciplines, req.min_relevance)
    return APIResponse(data=ClassifyResult(**data))


@app.post("/api/search/start")
async def start(req: SearchStartRequest) -> APIResponse:
    if not req.disciplines:
        raise HTTPException(status_code=400, detail="disciplines不能为空")

    task_id = f"task-{uuid.uuid4()}"
    TASKS[task_id] = {
        "task_id": task_id,
        "concept": req.concept,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "progress": {"overall": 0, "current_stage": "pending", "stages": {}},
        "partial": {"total_chunks_found": 0, "validated_chunks": 0, "by_discipline": {}},
        "result_chunks": [],
        "cancelled": False,
        "error": None,
    }

    async def runner() -> None:
        TASKS[task_id]["status"] = "processing"
        TASKS[task_id]["progress"]["stages"] = {
            "classification": "completed",
            "search": "in_progress",
            "aggregation": "pending",
            "validation": "pending",
        }
        TASKS[task_id]["updated_at"] = datetime.utcnow()

        def status_cb(stage: str, overall: int, extra: dict[str, Any]) -> None:
            TASKS[task_id]["progress"]["current_stage"] = stage
            TASKS[task_id]["progress"]["overall"] = overall
            if stage in ("search", "aggregation", "validation"):
                TASKS[task_id]["progress"]["stages"][stage] = "in_progress"
            if stage == "completed":
                for k in TASKS[task_id]["progress"]["stages"].keys():
                    TASKS[task_id]["progress"]["stages"][k] = "completed"
            TASKS[task_id]["updated_at"] = datetime.utcnow()
            if "by_discipline" in extra:
                TASKS[task_id]["partial"]["by_discipline"] = extra["by_discipline"]
            if "total" in extra:
                TASKS[task_id]["partial"]["total_chunks_found"] = extra["total"]
                TASKS[task_id]["partial"]["validated_chunks"] = extra["total"]

        def cancelled_flag() -> bool:
            return bool(TASKS[task_id].get("cancelled"))

        try:
            chunks = await agent.run_search(
                concept=req.concept,
                disciplines=[d.model_dump() for d in req.disciplines],
                max_results_per_discipline=req.search_config.max_results_per_discipline,
                enable_validation=req.search_config.enable_validation,
                status_cb=status_cb,
                cancelled_flag=cancelled_flag,
                auto_ingest=True,  # docker-compose 里有 KNOWLEDGE_ENGINE_URL
            )
            if cancelled_flag():
                TASKS[task_id]["status"] = "cancelled"
            else:
                TASKS[task_id]["status"] = "completed"
                TASKS[task_id]["result_chunks"] = [c.model_dump() for c in chunks]
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            TASKS[task_id]["error"] = str(e)
        finally:
            TASKS[task_id]["updated_at"] = datetime.utcnow()

    asyncio.create_task(runner())

    return APIResponse(
        data=SearchStartResult(
            task_id=task_id,
            status="processing",
            created_at=TASKS[task_id]["created_at"],
            estimated_duration_seconds=30,
        )
    )


@app.get("/api/search/status/{task_id}")
async def status(task_id: str) -> APIResponse:
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="搜索任务不存在")

    data = SearchStatusData(
        task_id=task_id,
        status=t["status"],
        progress=t["progress"],
        partial_results=t["partial"],
        started_at=t["created_at"],
        updated_at=t["updated_at"],
    )
    return APIResponse(data=data)


@app.get("/api/search/results/{task_id}")
async def results(
    task_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    discipline: str | None = None,
    min_relevance: float = Query(0.0, ge=0.0, le=1.0),
) -> APIResponse:
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="搜索任务不存在")
    if t["status"] != "completed":
        raise HTTPException(status_code=400, detail="搜索任务未完成")

    chunks = t["result_chunks"]
    if discipline:
        chunks = [c for c in chunks if c.get("discipline") == discipline]
    chunks = [c for c in chunks if float(c.get("relevance_score", 0.0)) >= min_relevance]

    total = len(chunks)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = chunks[start:end]

    avg_rel = sum(float(c.get("relevance_score", 0.0)) for c in chunks) / total if total else 0.0
    disciplines_covered = len({c.get("discipline") for c in chunks if c.get("discipline")}) if total else 0

    data = SearchResultsResponseData(
        task_id=task_id,
        concept=t["concept"],
        summary=SearchSummary(total_chunks=total, disciplines_covered=disciplines_covered, average_relevance=avg_rel),
        chunks=page_items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if page_size else 1,
        ),
    )
    return APIResponse(data=data)


@app.delete("/api/search/tasks/{task_id}")
async def cancel(task_id: str) -> APIResponse:
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="搜索任务不存在")
    t["cancelled"] = True
    t["status"] = "cancelled"
    t["updated_at"] = datetime.utcnow()
    return APIResponse(message="Task cancelled successfully", data=CancelTaskResult(task_id=task_id))