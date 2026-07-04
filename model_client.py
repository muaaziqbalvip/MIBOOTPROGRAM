"""
MI AI - Model Client
GitHub Actions par models load nahi hote (RAM/time limit).
Yeh Hugging Face Space ke API ko call karta hai jahan models host hain.
"""

import requests
import logging

from config import HF_SPACE_URL

logger = logging.getLogger(__name__)


def generate_reply(user_text: str, mode: str, history: list, system_identity: str) -> str:
    """
    HF Space API ko call karta hai.
    system_identity: har bot ki apni fixed identity (config.py se banti hai)
    """
    if not HF_SPACE_URL:
        return "⚠️ HF_SPACE_URL set nahi hai. GitHub Secrets me add karein."

    try:
        resp = requests.post(
            f"{HF_SPACE_URL}/generate",
            json={
                "text": user_text,
                "mode": mode,
                "history": history,
                "system_identity": system_identity,
            },
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json().get("reply", "❌ Khali jawab mila server se.")
    except requests.exceptions.Timeout:
        return "⏳ Model server response me time zyada lag raha hai, dobara try karein."
    except requests.exceptions.ConnectionError:
        return "❌ Model server (Hugging Face Space) se connect nahi ho saka. Space chal raha hai check karein."
    except Exception as e:
        logger.error(f"Model API error: {e}")
        return f"❌ Error: {e}"