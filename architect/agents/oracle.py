import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests

try:
    import openai
except ImportError:  # pragma: no cover - optional
    openai = None

try:
    from mistralai.client import MistralClient
except Exception:  # pragma: no cover - optional
    MistralClient = None

from architect.metrics import (
    agent_errors,
    agent_invocations,
    agent_run_seconds,
)

logger = logging.getLogger(__name__)


class OracleAgent:
    """Fetch and summarize HackerNews articles."""

    def __init__(self, config: Dict):
        self.config = config
        self.memory_path = Path("memory/state.json")
        self.memory_path.parent.mkdir(exist_ok=True)

        provider = config.get("llm_provider")
        self.llm_client = None
        if provider == "openai" and openai:
            openai.api_key = config.get("openai_api_key")
            self.llm_client = "openai"
        elif provider == "mistral" and MistralClient:
            self.llm_client = MistralClient(api_key=config.get("mistral_api_key"))
        else:
            logger.warning("Unsupported or missing LLM provider")

    def fetch_news(self, limit: int = 10) -> List[Dict]:
        """Fetch top stories from HackerNews."""
        try:
            resp = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                timeout=10,
            )
            resp.raise_for_status()
            story_ids = resp.json()[:limit]
        except Exception as exc:  # pragma: no cover - network
            logger.error("Failed to fetch top stories: %s", exc)
            return []

        stories = []
        for sid in story_ids:
            try:
                s_resp = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=10,
                )
                s_resp.raise_for_status()
                data = s_resp.json()
                if data and data.get("type") == "story":
                    stories.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "url": data.get("url"),
                        "score": data.get("score"),
                        "by": data.get("by"),
                        "time": data.get("time"),
                        "descendants": data.get("descendants", 0),
                    })
            except Exception as exc:  # pragma: no cover - network
                logger.warning("Failed to fetch story %s: %s", sid, exc)
        logger.info("Fetched %d stories", len(stories))
        return stories

    def summarize_articles(self, articles: List[Dict]) -> str:
        if not articles:
            return "No articles to summarize."

        text = "\n\n".join(
            f"Title: {a['title']}\nScore: {a['score']}\nURL: {a.get('url','')}" for a in articles
        )
        prompt = (
            "Summarize the main themes from these HackerNews articles:\n\n" + text
        )
        try:
            if self.llm_client == "openai" and openai:
                resp = openai.ChatCompletion.create(
                    model=self.config.get("openai_model", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.3,
                )
                summary = resp.choices[0].message.content.strip()
            elif isinstance(self.llm_client, MistralClient):
                resp = self.llm_client.chat(
                    model=self.config.get("mistral_model", "mistral-small"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.3,
                )
                summary = resp.choices[0].message.content.strip()
            else:
                summary = "LLM provider not configured."
        except Exception as exc:  # pragma: no cover - network
            logger.error("Failed to summarize articles: %s", exc)
            summary = f"Failed to summarize: {exc}"
        return summary

    def log_results(self, articles: List[Dict], summary: str) -> None:
        try:
            state: Dict[str, Dict] = {}
            if self.memory_path.exists():
                with open(self.memory_path) as f:
                    state = json.load(f)
            name = "oracle"
            if name not in state:
                state[name] = {
                    "purpose": "Fetch and summarize HackerNews articles",
                    "created": datetime.utcnow().isoformat(),
                    "invocations": 0,
                    "last_run": None,
                }
            state[name]["invocations"] += 1
            state[name]["last_run"] = datetime.utcnow().isoformat()
            state[name]["latest_results"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "articles_count": len(articles),
                "summary": summary,
            }
            with open(self.memory_path, "w") as f:
                json.dump(state, f, indent=2)
            logger.info("Logged execution to %s", self.memory_path)
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to log results: %s", exc)

    def run(self, limit: int = 10) -> Dict:
        logger.info("Running OracleAgent")
        agent_invocations.inc()
        with agent_run_seconds.time():
            try:
                articles = self.fetch_news(limit)
                summary = self.summarize_articles(articles)
                self.log_results(articles, summary)
            except Exception as exc:  # pragma: no cover - unexpected
                agent_errors.inc()
                logger.error("OracleAgent execution failed: %s", exc)
                raise
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "articles": articles,
            "summary": summary,
        }
