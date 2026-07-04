"""
MI AI - Web Search
DuckDuckGo Instant Answer API use karta hai (free, koi API key nahi chahiye).
"""

import requests


def web_search(query: str) -> str:
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("AbstractText"):
            result = data["AbstractText"]
            if data.get("AbstractURL"):
                result += f"\n\n🔗 {data['AbstractURL']}"
            return result

        if data.get("RelatedTopics"):
            lines = []
            for topic in data["RelatedTopics"][:5]:
                if isinstance(topic, dict) and topic.get("Text"):
                    lines.append(f"• {topic['Text']}")
            if lines:
                return "\n".join(lines)

        return "❌ Is query ke liye direct jawab nahi mila. Zyada specific search try karein."

    except Exception as e:
        return f"❌ Search me error aaya: {e}"