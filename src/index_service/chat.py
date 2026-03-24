from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from index_service.config import Settings
from index_service.models import SearchHit
from index_service.search import SearchService


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(slots=True)
class SuggestedAction:
    label: str
    path: str
    mode: str


@dataclass(slots=True)
class ChatReply:
    message: str
    reply: str
    citations: list[SearchHit]
    actions: list[SuggestedAction]
    used_llm: bool


class ChatService:
    def __init__(self, search_service: SearchService, settings: Settings) -> None:
        self.search_service = search_service
        self.settings = settings

    def reply(self, message: str, history: list[ChatMessage], limit: int) -> ChatReply:
        cleaned = message.strip()
        if not cleaned:
            raise ValueError("Message must not be empty.")

        # 内容和文件名都查一遍，先让绯铃具备“像人一样综合找”的感觉。
        content_hits = self.search_service.search(cleaned, limit=max(1, limit)).results
        file_hits = self.search_service.search_files(cleaned, limit=max(1, min(limit, 4))).results
        citations = self._merge_hits(content_hits, file_hits, limit)
        actions = self._build_actions(citations)

        reply = self._build_fallback_reply(cleaned, citations, actions)
        used_llm = False

        if self._llm_ready():
            llm_reply = self._build_llm_reply(cleaned, history, citations, actions)
            if llm_reply:
                reply = llm_reply
                used_llm = True

        return ChatReply(
            message=cleaned,
            reply=reply,
            citations=citations,
            actions=actions,
            used_llm=used_llm,
        )

    def _merge_hits(self, content_hits: list[SearchHit], file_hits: list[SearchHit], limit: int) -> list[SearchHit]:
        merged: list[SearchHit] = []
        seen: set[tuple[str, str, int, int]] = set()

        for hit in [*content_hits, *file_hits]:
            key = (hit.path, hit.match_type, hit.chunk_index, hit.start_line)
            if key in seen:
                continue
            seen.add(key)
            merged.append(hit)
            if len(merged) >= limit:
                break

        return merged

    def _build_actions(self, citations: list[SearchHit]) -> list[SuggestedAction]:
        if not citations:
            return []

        top_hit = citations[0]
        return [
            SuggestedAction(label="打开文件", path=top_hit.path, mode="file"),
            SuggestedAction(label="打开目录", path=top_hit.path, mode="parent"),
        ]

    def _build_fallback_reply(
        self,
        message: str,
        citations: list[SearchHit],
        actions: list[SuggestedAction],
    ) -> str:
        if not citations:
            return (
                f"这次我先没替你找到“{message}”。"
                " 你可以换个说法，或者多给我一点线索。"
            )

        top = citations[0]
        if len(citations) == 1:
            base = (
                f"我先帮你锁到一个最像的结果，在 {top.path}。"
                f" 我看到的是：{top.snippet}"
            )
        else:
            others = "、".join(hit.path for hit in citations[1:3])
            base = (
                f"我先替你翻到 {len(citations)} 个相关结果，最像的是 {top.path}。"
                f" 另外还有 {others}。"
            )

        if actions:
            return base + " 要我现在帮你打开这个文件吗？"
        return base

    def _llm_ready(self) -> bool:
        return bool(
            self.settings.llm_base_url
            and self.settings.llm_api_key
            and self.settings.llm_model
        )

    def _build_llm_reply(
        self,
        message: str,
        history: list[ChatMessage],
        citations: list[SearchHit],
        actions: list[SuggestedAction],
    ) -> str | None:
        if not self._llm_ready():
            return None

        system_prompt = (
            "你是桌宠绯铃，一只很喜欢主人的白尾灵狐小助理。"
            " 语气要轻快一点、柔和、稍微傲娇，但不要阴阳怪气，不要夸张卖萌。"
            " 你要根据给定检索结果，用简洁中文回答。"
            " 如果结果不为空，要自然地提一句是否要帮主人打开文件。"
            " 不要编造未提供的文件路径或内容。"
            " 回复控制在 2 到 5 句。"
        )

        citations_payload = [
            {
                "path": hit.path,
                "match_type": hit.match_type,
                "snippet": hit.snippet,
                "score": hit.score,
            }
            for hit in citations
        ]
        actions_payload = [action.__dict__ for action in actions]

        messages = [{"role": "system", "content": system_prompt}]
        for item in history[-6:]:
            messages.append({"role": item.role, "content": item.content})
        messages.append(
            {
                "role": "user",
                "content": (
                    f"用户刚刚说：{message}\n"
                    f"检索结果：{json.dumps(citations_payload, ensure_ascii=False)}\n"
                    f"可执行动作：{json.dumps(actions_payload, ensure_ascii=False)}"
                ),
            }
        )

        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(
                    self.settings.llm_base_url.rstrip("/") + "/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.settings.llm_model,
                        "messages": messages,
                        "temperature": 0.7,
                    },
                )
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return None

        try:
            content = payload["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

        return content or None
