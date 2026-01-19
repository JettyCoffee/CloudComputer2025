from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import httpx

from models import Chunk, SourceInfo, ValidationInfo
from prompts import CLASSIFY_PROMPT, VALIDATE_PROMPT

logger = logging.getLogger("search-agent")

def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _hash_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


@dataclass
class SearchItem:
    url: str
    title: str
    content: str


class SearchAgent:
    def __init__(self) -> None:
        self.search_provider = os.getenv("SEARCH_PROVIDER", "wikipedia").strip().lower()
        self.tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.timeout_s = float(os.getenv("HTTP_TIMEOUT_S", "30"))
        self.knowledge_engine_url = os.getenv("KNOWLEDGE_ENGINE_URL", "http://knowledge-engine:8002").strip()
        self.wiki_lang = os.getenv("WIKIPEDIA_LANG", "zh").strip().lower()

    async def classify(self, concept: str, max_disciplines: int = 5, min_relevance: float = 0.3) -> dict[str, Any]:
        if self.openai_key:
            try:
                payload = await self._llm_json(CLASSIFY_PROMPT.format(concept=concept))
                disciplines = payload.get("disciplines") or []
                disciplines = [d for d in disciplines if float(d.get("relevance_score", 0)) >= min_relevance]
                disciplines = disciplines[:max_disciplines]
                for i, d in enumerate(disciplines, start=1):
                    d.setdefault("id", f"d{i}")
                    d.setdefault("is_primary", i == 1)
                payload["disciplines"] = disciplines
                payload["primary_discipline"] = payload.get("primary_discipline") or (disciplines[0]["name"] if disciplines else "综合")
                payload.setdefault("suggested_additions", [])
                return payload
            except Exception:
                pass

        # fallback（保证无 key 也能演示）
        default = [
            ("数学", ["概率论 熵", "KL散度", "最大熵 原理"]),
            ("物理学-热力学", [f"{concept} 热力学 第二定律", "克劳修斯 熵", "熵增原理"]),
            ("信息论", [f"{concept} 香农", "信息熵 定义", "编码 定理"]),
            ("统计力学", [f"{concept} 玻尔兹曼", "微观态 宏观态", "配分函数"]),
            ("机器学习", [f"{concept} 交叉熵 损失", "信息增益 决策树", "最大熵模型"]),
        ][:max_disciplines]

        ds = []
        for i, (name, kws) in enumerate(default, start=1):
            score = max(0.4, 1.0 - (i - 1) * 0.12)
            if score < min_relevance:
                continue
            ds.append(
                {
                    "id": f"d{i}",
                    "name": name,
                    "relevance_score": score,
                    "reason": f"规则模板生成（fallback），用于启动跨学科检索：{name}",
                    "search_keywords": kws,
                    "is_primary": i == 1,
                }
            )
        return {
            "concept": concept,
            "primary_discipline": ds[0]["name"] if ds else "综合",
            "disciplines": ds,
            "suggested_additions": [],
        }

    async def tavily_search(self, query: str, max_results: int) -> list[SearchItem]:
        if not self.tavily_key:
            return []

        url = "https://api.tavily.com/search"
        body = {
            "api_key": self.tavily_key,
            "query": query,
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(url, json=body)
            r.raise_for_status()
            data = r.json()

        items: list[SearchItem] = []
        for it in data.get("results", []) or []:
            items.append(
                SearchItem(
                    url=it.get("url", "") or "",
                    title=it.get("title", "") or "",
                    content=_clean_text(it.get("content", "") or it.get("snippet", "") or ""),
                )
            )
        return items
    
    async def wikipedia_search(self, query: str, max_results: int) -> list[SearchItem]:
        """
        Free provider using MediaWiki APIs:
        1) opensearch -> titles
        2) summary REST -> extract
        """
        lang = "zh" if self.wiki_lang not in ("zh", "en") else self.wiki_lang
        opensearch = f"https://{lang}.wikipedia.org/w/api.php"

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.get(
                opensearch,
                params={
                    "action": "opensearch",
                    "search": query,
                    "limit": str(max(1, min(max_results, 10))),
                    "namespace": "0",
                    "format": "json",
                },
                headers={"User-Agent": "CloudComputer2025-SearchAgent/0.1"},
            )
            r.raise_for_status()
            data = r.json()

            titles = data[1] if isinstance(data, list) and len(data) > 1 else []
            urls = data[3] if isinstance(data, list) and len(data) > 3 else []

            items: list[SearchItem] = []
            for title, page_url in list(zip(titles, urls))[:max_results]:
                # summary endpoint (REST)
                # Use title in URL; MediaWiki REST expects URL-encoded title
                summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{httpx.URL(title)}"
                try:
                    sr = await client.get(summary_url, headers={"User-Agent": "CloudComputer2025-SearchAgent/0.1"})
                    if sr.status_code != 200:
                        continue
                    sdata = sr.json()
                    extract = _clean_text(sdata.get("extract", "") or "")
                    if len(extract) < 80:
                        continue
                    items.append(SearchItem(url=page_url, title=title, content=extract))
                except Exception:
                    continue

        return items

    async def mock_search(self, query: str, max_results: int) -> list[SearchItem]:
        base = (
            f"Mock result for query='{query}'. "
            "This is offline demo text. It should be replaced by real provider in production."
        )
        return [
            SearchItem(
                url="about:mock",
                title="mock-search",
                content=base + " " + ("More details. " * 20),
            )
        ][:max_results]

    async def search(self, query: str, max_results: int) -> list[SearchItem]:
        if self.search_provider == "tavily":
            return await self.tavily_search(query, max_results)
        if self.search_provider == "mock":
            return await self.mock_search(query, max_results)
        # default wikipedia
        return await self.wikipedia_search(query, max_results)
    
    async def run_search(
        self,
        concept: str,
        disciplines: list[dict[str, Any]],
        max_results_per_discipline: int,
        enable_validation: bool,
        status_cb: Optional[callable] = None,
        cancelled_flag: Optional[callable] = None,
        auto_ingest: bool = True,
    ) -> list[Chunk]:
        def update(stage: str, overall: int, extra: dict[str, Any] | None = None) -> None:
            if status_cb:
                status_cb(stage=stage, overall=overall, extra=extra or {})

        update("search", 10)

        queries: list[tuple[str, str]] = []
        for d in disciplines:
            name = d["name"]
            kws = d.get("search_keywords") or [name]
            for kw in kws[:3]:
                queries.append((name, f"{concept} {kw}"))

        async def one(discipline: str, q: str) -> list[SearchItem]:
            if cancelled_flag and cancelled_flag():
                return []
            try:
                return await self.search(q, max_results=max_results_per_discipline)
            except Exception as e:
                logger.exception("search provider failed. discipline=%s query=%s err=%s", discipline, q, e)
                return []

        results_nested = await asyncio.gather(*[one(d, q) for d, q in queries])

        if cancelled_flag and cancelled_flag():
            return []

        update("aggregation", 55)

        # flatten + clean + dedup
        seen = set()
        flat: list[tuple[str, SearchItem]] = []
        for (disc, _q), items in zip(queries, results_nested):
            for it in items:
                key = (it.url or "") + "|" + _hash_text(it.content)
                if key in seen:
                    continue
                seen.add(key)
                if len(it.content) < 80:
                    continue
                flat.append((disc, it))

        if not flat:
            # no results fallback chunk
            return [
                Chunk(
                    id=f"chunk-{uuid.uuid4().hex[:8]}",
                    content=(
                        "没有检索到内容。请检查：\n"
                        f"- SEARCH_PROVIDER={self.search_provider}\n"
                        "- 如果用 tavily：是否设置了 TAVILY_API_KEY\n"
                        "- 如果用 wikipedia：网络是否可访问 wikipedia\n"
                    ),
                    discipline=disciplines[0]["name"] if disciplines else "综合",
                    source=SourceInfo(url="about:blank", title="search-agent notice"),
                    relevance_score=0.1,
                    academic_value=0.1,
                    validation=ValidationInfo(is_validated=False, confidence=0.1, notes="no results"),
                    extracted_entities=[],
                )
            ]

        update("validation", 70)

        validated_meta: dict[str, dict[str, Any]] = {}
        if enable_validation and self.openai_key and flat:
            try:
                cand = [{"url": it.url, "title": it.title, "content": it.content[:800]} for _, it in flat[:30]]
                resp = await self._llm_json(
                    VALIDATE_PROMPT.format(concept=concept, items_json=json.dumps(cand, ensure_ascii=False))
                )
                for v in resp.get("validated", []) or []:
                    validated_meta[v.get("url", "")] = v
                # rejected 忽略即可
            except Exception:
                pass

        chunks: list[Chunk] = []
        by_disc: dict[str, int] = {}

        for disc, it in flat:
            meta = validated_meta.get(it.url, {})
            if enable_validation and self.openai_key and meta.get("is_valid") is False:
                continue

            rel = float(meta.get("relevance_score", 0.65))
            acad = float(meta.get("academic_value", 0.55))

            chunks.append(
                Chunk(
                    id=f"chunk-{uuid.uuid4().hex[:8]}",
                    content=it.content,
                    discipline=disc,
                    source=SourceInfo(url=it.url, title=it.title),
                    relevance_score=max(0.0, min(1.0, rel)),
                    academic_value=max(0.0, min(1.0, acad)),
                    validation=ValidationInfo(
                        is_validated=bool(enable_validation and self.openai_key),
                        confidence=max(0.0, min(1.0, rel)),
                        notes=meta.get("notes"),
                    ),
                    extracted_entities=[],
                )
            )
            by_disc[disc] = by_disc.get(disc, 0) + 1

        update("completed", 100, extra={"by_discipline": by_disc, "total": len(chunks)})

        if auto_ingest and chunks:
            await self._post_to_knowledge_engine(concept, chunks)

        return chunks

    async def _post_to_knowledge_engine(self, concept: str, chunks: list[Chunk]) -> None:
        # Knowledge Engine: POST /api/ingest（按 Technical.md）
        url = f"{self.knowledge_engine_url.rstrip('/')}/api/ingest"
        payload = {"concept": concept, "chunks": [c.model_dump() for c in chunks]}
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            try:
                await client.post(url, json=payload)
            except Exception:
                # ingest失败不影响search结果返回（容错）
                return

    async def _llm_json(self, prompt: str) -> dict[str, Any]:
        url = f"{self.openai_base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        body = {
            "model": self.openai_model,
            "messages": [
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)