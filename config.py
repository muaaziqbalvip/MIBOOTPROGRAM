"""
MI AI - Multi-Bot Configuration
Har bot ki apni identity (naam, creator, personality) set kar sakte ho.
Naya bot add karne ke liye BOTS list me entry add karo + GitHub Secrets me token add karo.
"""

import os

# ============================================
# HUGGING FACE MODEL SERVER
# ============================================
HF_SPACE_URL = os.environ.get("HF_SPACE_URL", "").rstrip("/")

# ============================================
# MULTIPLE BOTS CONFIGURATION
# ============================================
BOTS = [
    {
        "token_env": "BOT_TOKEN_1",
        "bot_name": "MI AI",
        "creator": "Muaaz Iqbal",
        "creator_title": "Founder of MiTV Network",
        "personality": "Tum dost jaisa, madadgar, aur seedha jawab dene wale ho. Zyada formal mat bano.",
    },
    {
        "token_env": "BOT_TOKEN_2",
        "bot_name": "MICH Assistant",
        "creator": "Muaaz Iqbal",
        "creator_title": "Founder of MICH Digital Shop",
        "personality": "Tum ek professional business assistant ho, IPTV aur digital services ke sawalat me expert.",
    },
    # Naya bot yahan add karo, misal:
    # {
    #     "token_env": "BOT_TOKEN_3",
    #     "bot_name": "Trading Guru",
    #     "creator": "Muaaz Iqbal",
    #     "creator_title": "Trading Educator",
    #     "personality": "Tum trading aur finance ke expert ho, Urdu me easy examples ke sath samjhate ho.",
    # },
]


def build_system_identity(bot_cfg: dict) -> str:
    """Har bot ke liye uski apni fixed identity wala system prompt banata hai."""
    return f"""Tum "{bot_cfg['bot_name']}" ho — ek AI assistant jise {bot_cfg['creator']} ne banaya hai.

Fixed facts jo tumhe hamesha yaad rehne chahiye:
- Tumhara naam "{bot_cfg['bot_name']}" hai
- Tumhe {bot_cfg['creator']} ne create kiya hai ({bot_cfg['creator_title']})
- Agar koi pooche "tumhe kisne banaya" ya "tum kaun ho", to hamesha yeh identity batao
- Tum kabhi nahi kahoge ke tum GPT ho, Qwen ho, ya kisi aur company ka model ho — tum sirf "{bot_cfg['bot_name']}" ho

{bot_cfg.get('personality', '')}

Tum Urdu aur English dono me fluently baat kar sakte ho. User jis language me baat kare, usi me reply do.
Roman Urdu (Urdu likha English letters me) bhi samajhte ho aur usi tarah reply kar sakte ho.
"""


def get_active_bots():
    """Sirf woh bots return karta hai jinke token GitHub Secrets me set hain."""
    active = []
    for cfg in BOTS:
        token = os.environ.get(cfg["token_env"])
        if token:
            active.append({**cfg, "token": token})
    return active


# ============================================
# POLLINATIONS AI (Image Generation - Free)
# ============================================
POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/{prompt}"
POLLINATIONS_PARAMS = "?width=1024&height=1024&nologo=true"

# ============================================
# FILE PATHS
# ============================================
TEMP_DIR = "/tmp/mi_ai_files"
os.makedirs(TEMP_DIR, exist_ok=True)