"""
MI AI - Website Builder
Pro model (HF Space ke through) ko prompt karta hai poori website
(HTML+CSS+JS) generate karne ke liye, phir ZIP banata hai.
"""

import re
from model_client import generate_reply
from file_gen import generate_website_zip

WEBSITE_PROMPT_TEMPLATE = """Ek complete, professional, modern website bana do is topic/requirement par: "{topic}"

Zaroori instructions:
1. Poora HTML code do, sirf `<!--HTML START-->` aur `<!--HTML END-->` ke darmiyan
2. Poora CSS code do, sirf `/*CSS START*/` aur `/*CSS END*/` ke darmiyan
3. Poora JS code do, sirf `//JS START` aur `//JS END` ke darmiyan
4. Design modern, responsive, aur professional honi chahiye
5. HTML me CSS aur JS ko separate files (style.css, script.js) se link karo
6. Placeholder text mat lagao — real, meaningful content likho is topic ke mutabiq

Format bilkul is tarah follow karo, extra explanation mat do:

<!--HTML START-->
(poora html code yahan)
<!--HTML END-->

/*CSS START*/
(poora css code yahan)
/*CSS END*/

//JS START
(poora js code yahan, agar zaroori na ho to sirf comment likh do)
//JS END
"""


def _extract_block(text: str, start_tag: str, end_tag: str) -> str:
    pattern = re.escape(start_tag) + r"(.*?)" + re.escape(end_tag)
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def build_website(topic: str, system_identity: str) -> str:
    """Topic ke hisaab se poori website generate karta hai aur ZIP path return karta hai."""
    prompt = WEBSITE_PROMPT_TEMPLATE.format(topic=topic)
    raw_output = generate_reply(prompt, mode="pro", history=[], system_identity=system_identity)

    html = _extract_block(raw_output, "<!--HTML START-->", "<!--HTML END-->")
    css = _extract_block(raw_output, "/*CSS START*/", "/*CSS END*/")
    js = _extract_block(raw_output, "//JS START", "//JS END")

    if not html:
        html = f"<!DOCTYPE html><html><head><title>{topic}</title><link rel='stylesheet' href='style.css'></head><body><h1>{topic}</h1><p>{raw_output}</p><script src='script.js'></script></body></html>"
    if not css:
        css = "body { font-family: sans-serif; background: #1a1410; color: #f5f5f5; padding: 40px; }"
    if not js:
        js = "// No custom script needed"

    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", topic.lower())[:30] or "website"
    zip_path = generate_website_zip(safe_name, html, css, js)
    return zip_path