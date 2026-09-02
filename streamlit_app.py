import base64
import mimetypes
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Happy Birthday ♡ — Scrapbook",
    page_icon="♡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome and let the scrapbook iframe fill the viewport.
st.markdown(
    """
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"], footer {display: none;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      [data-testid="stAppViewContainer"] > .main {padding: 0 !important;}
      html, body {margin: 0; padding: 0; overflow: hidden;}
      [data-testid="stIFrame"], [data-testid="stIFrame"] iframe {
        width: 100vw !important;
        height: 100vh !important;
        border: 0 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE = Path(__file__).parent
HTML_FILE = BASE / "index.html"


def _data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if mime is None:
        mime = "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


@st.cache_data(show_spinner="Loading scrapbook…")
def build_html(html_mtime_ns: int) -> str:
    html = HTML_FILE.read_text(encoding="utf-8")

    def replace_attr(match: re.Match) -> str:
        attr, quote, filename = match.group(1), match.group(2), match.group(3)
        asset = BASE / filename
        if asset.is_file():
            return f"{attr}={quote}{_data_uri(asset)}{quote}"
        return match.group(0)

    html = re.sub(
        r'(src|href)=(["\'])(?!https?:|data:|#|/)([^"\']+)\2',
        replace_attr,
        html,
    )

    def replace_url(match: re.Match) -> str:
        raw = match.group(1).strip().strip("'\"")
        if raw.startswith(("http:", "https:", "data:", "/", "#")):
            return match.group(0)
        asset = BASE / raw
        if asset.is_file():
            return f'url("{_data_uri(asset)}")'
        return match.group(0)

    html = re.sub(r"url\(([^)]+)\)", replace_url, html)
    return html


components.html(build_html(HTML_FILE.stat().st_mtime_ns), height=1000, scrolling=True)
