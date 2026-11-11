"""
src/shared_utils.py
Shared utilities used by every Streamlit page.

Provides:
  - inject_css()          : global CSS — premium dark theme
  - init_session_state()  : ensure all shared keys exist before page renders
  - render_sidebar()      : common sidebar (language selector + profile summary)
  - profile_summary_sidebar() : compact profile card shown in every sidebar
"""
import sys
import os
import base64
from pathlib import Path

# Ensure project root is on sys.path so src/ imports work from pages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.config import APP_TITLE, LLM_PROVIDER
from src.language_service import LANGUAGE_CODES, get_label

_APP_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "brand" / "smart_farming_logo.svg"


def _app_logo_data_uri() -> str:
    """Return the shared, project-local logo as an inline SVG image."""
    encoded_logo = base64.b64encode(_APP_LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded_logo}"


APP_LOGO_DATA_URI = _app_logo_data_uri()


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
<style>
/* ── Google Fonts for Indian scripts ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables — Dark Palette ─────────────────────────────────── */
:root {
    --bg-main:        #1F1F1F;
    --bg-sidebar:     #191919;
    --bg-panel:       #262626;
    --bg-card:        #2D2D2D;
    --bg-input:       #303030;
    --text-primary:   #F2F2F2;
    --text-secondary: #B7B7B7;
    --text-muted:     #8A8A8A;
    --border:         #3D3D3D;
    --accent:         #A3BFA8;
    --accent-hover:   #B8D0BC;
    --success:        #79B88A;
    --warning:        #E5B567;
    --error:          #E17B7B;
    --radius-sm:      8px;
    --radius-md:      12px;
    --radius-lg:      16px;
}

/* ── Root / global ────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans Tamil', 'Noto Sans Telugu',
                 'Noto Sans Devanagari', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Main app background ──────────────────────────────────────────── */
body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.main .block-container {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}

/* ── Top header bar ───────────────────────────────────────────────── */
[data-testid="stHeader"] {
    background-color: var(--bg-main) !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 1rem !important;
    color: #A3BFA8 !important;
    font-weight: 600 !important;
    margin-bottom: 0.3rem !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 0.88rem;
    line-height: 1.55;
    color: #B4B4B4 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #3A3A3A !important;
    margin: 0.75rem 0 !important;
}

/* ── Sidebar navigation links ─────────────────────────────────────── */
section[data-testid="stSidebar"] a {
    color: #B4B4B4 !important;
    text-decoration: none !important;
    font-size: 0.88rem;
    transition: color 0.15s ease;
}
section[data-testid="stSidebar"] a:hover {
    color: #A3BFA8 !important;
}

/* ── Sidebar selectbox ────────────────────────────────────────────── */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #2B2B2B !important;
    border: 1px solid #3A3A3A !important;
    border-radius: 8px !important;
    color: #F5F5F5 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
    border-color: #A3BFA8 !important;
}

/* ── Sidebar success / warning badges ────────────────────────────── */
section[data-testid="stSidebar"] [data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.8rem !important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"][data-baseweb="notification"][kind="positive"],
section[data-testid="stSidebar"] .stSuccess {
    background-color: rgba(121, 184, 138, 0.12) !important;
    border: 1px solid rgba(121, 184, 138, 0.28) !important;
    color: #79B88A !important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
section[data-testid="stSidebar"] .stWarning {
    background-color: rgba(229, 181, 103, 0.1) !important;
    border: 1px solid rgba(229, 181, 103, 0.25) !important;
    color: #E5B567 !important;
}

/* ── Heading hierarchy ────────────────────────────────────────────── */
h1 { font-size: 1.9rem !important; font-weight: 700 !important; margin-bottom: 0.3rem !important; color: #F5F5F5 !important; }
h2 { font-size: 1.45rem !important; font-weight: 600 !important; color: #F5F5F5 !important; }
h3 { font-size: 1.15rem !important; font-weight: 600 !important; color: #F5F5F5 !important; }

/* ── Tamil / Telugu / Devanagari script class ─────────────────────── */
.lang-ta { font-family: 'Noto Sans Tamil', sans-serif !important; font-size: 1.05em; }
.lang-te { font-family: 'Noto Sans Telugu', sans-serif !important; font-size: 1.05em; }
.lang-hi { font-family: 'Noto Sans Devanagari', sans-serif !important; font-size: 1.05em; }

/* ── Cards — dark elevated surfaces ──────────────────────────────── */
.sf-card {
    background: #2B2B2B;
    border: 1px solid #3A3A3A;
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    color: #F5F5F5;
}
.sf-card-green  { border-left: 3px solid #79B88A; }
.sf-card-yellow { border-left: 3px solid #E5B567; }
.sf-card-red    { border-left: 3px solid #E17B7B; }
.sf-card-blue   { border-left: 3px solid #A3BFA8; }

/* ── Welcome / Hero section ───────────────────────────────────────── */
.sf-hero {
    background: #242424;
    border: 1px solid #3A3A3A;
    border-radius: 20px;
    padding: 2.2rem 2.4rem 1.8rem;
    margin: 0.5rem 0 1.8rem;
}
.sf-hero-title {
    font-size: clamp(1.8rem, 3.5vw, 2.8rem);
    font-weight: 700;
    color: #F5F5F5;
    line-height: 1.2;
    margin: 0 0 0.5rem;
    display: block;
}
.sf-hero-tagline {
    font-size: 1.15rem;
    font-weight: 400;
    color: #A3BFA8;
    margin: 0 0 1rem;
    display: block;
}
.sf-hero-intro {
    font-size: 1rem;
    color: #B4B4B4;
    line-height: 1.7;
    max-width: 700px;
    margin: 0;
}
.sf-mark {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    display: block;
}
.sf-welcome {
    max-width: 760px;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #B4B4B4;
}

/* ── Feature grid ─────────────────────────────────────────────────── */
.sf-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
    margin-top: 1.2rem;
}
.sf-feature {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    background: #2B2B2B;
    border: 1px solid #3A3A3A;
    border-radius: var(--radius-md);
    padding: 0.95rem 1rem;
    color: #F5F5F5;
    transition: border-color 0.15s ease;
}
.sf-feature:hover {
    border-color: #A3BFA8;
}
.sf-feature b {
    font-weight: 600;
    color: #F5F5F5;
    font-size: 0.93rem;
}
.sf-feature span {
    color: #858585;
    font-size: 0.87rem;
    line-height: 1.5;
}

/* ── Language selector column ─────────────────────────────────────── */
.sf-lang-panel {
    background: #2B2B2B;
    border: 1px solid #3A3A3A;
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem 1.6rem;
}
.sf-lang-panel h3 {
    color: #F5F5F5 !important;
    margin-top: 0 !important;
}

/* ── Buttons — primary ────────────────────────────────────────────── */
button[kind="primary"],
button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    background-color: #A3BFA8 !important;
    color: #171717 !important;
    border: 1px solid #A3BFA8 !important;
    border-radius: var(--radius-md) !important;
    min-height: 2.75rem;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    box-shadow: none !important;
}
button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background-color: #B8D0BC !important;
    border-color: #B8D0BC !important;
}

/* ── Buttons — secondary ──────────────────────────────────────────── */
button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    color: #B4B4B4 !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: border-color 0.15s ease, color 0.15s ease;
}
button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #A3BFA8 !important;
    color: #A3BFA8 !important;
}

/* ── Form submit button ───────────────────────────────────────────── */
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"] {
    background-color: #A3BFA8 !important;
    color: #171717 !important;
    border-color: #A3BFA8 !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0 !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background-color: #B8D0BC !important;
    border-color: #B8D0BC !important;
}

/* ── Container / card borders (st.container(border=True)) ─────────── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #3A3A3A !important;
    border-radius: var(--radius-lg) !important;
    background: #242424 !important;
    box-shadow: none !important;
}

/* ── Input / select fields ────────────────────────────────────────── */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    background: #303030 !important;
    color: #F5F5F5 !important;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within {
    border-color: #A3BFA8 !important;
    box-shadow: 0 0 0 2px rgba(163, 191, 168, 0.15) !important;
}
/* Select dropdown menu ────────────────────────────────────────────── */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[data-baseweb="select"] ul {
    background-color: #2B2B2B !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
}
[role="option"],
[data-baseweb="menu"] li {
    background-color: #2B2B2B !important;
    color: #F5F5F5 !important;
}
[role="option"]:hover,
[data-baseweb="menu"] li:hover,
[role="option"][aria-selected="true"] {
    background-color: #3A3A3A !important;
    color: #A3BFA8 !important;
}

/* ── Text input placeholder ───────────────────────────────────────── */
input::placeholder, textarea::placeholder {
    color: #858585 !important;
}
input, textarea {
    color: #F5F5F5 !important;
    background-color: #303030 !important;
}

/* ── Widget labels ────────────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p,
.stTextInput label, .stSelectbox label, .stTextArea label {
    color: #B4B4B4 !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
}

/* ── Alerts / Notices ─────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    font-size: 0.92rem !important;
}
/* success */
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"],
.stSuccess, div[data-testid="stAlert"].stSuccess {
    background-color: rgba(121, 184, 138, 0.1) !important;
    border: 1px solid rgba(121, 184, 138, 0.25) !important;
    color: #79B88A !important;
}
/* warning */
[data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
.stWarning, div[data-testid="stAlert"].stWarning {
    background-color: rgba(229, 181, 103, 0.1) !important;
    border: 1px solid rgba(229, 181, 103, 0.25) !important;
    color: #E5B567 !important;
}
/* error */
[data-testid="stAlert"][data-baseweb="notification"][kind="negative"],
.stError, div[data-testid="stAlert"].stError {
    background-color: rgba(225, 123, 123, 0.1) !important;
    border: 1px solid rgba(225, 123, 123, 0.25) !important;
    color: #E17B7B !important;
}
/* info */
[data-testid="stAlert"][data-baseweb="notification"][kind="info"],
.stInfo, div[data-testid="stAlert"].stInfo {
    background-color: rgba(163, 191, 168, 0.08) !important;
    border: 1px solid rgba(163, 191, 168, 0.2) !important;
    color: #A3BFA8 !important;
}

/* ── Metrics ──────────────────────────────────────────────────────── */
[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    color: #858585 !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.1rem !important;
    color: #F5F5F5 !important;
    font-weight: 600 !important;
}
[data-testid="metric-container"] {
    background: #242424 !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1rem !important;
}

/* ── Expanders ────────────────────────────────────────────────────── */
details {
    background: #242424 !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 0.5rem !important;
}
details summary {
    padding: 0.65rem 1rem !important;
    cursor: pointer;
    color: #B4B4B4 !important;
}
details summary:hover {
    color: #F5F5F5 !important;
}
details summary p {
    font-weight: 600;
    color: #B4B4B4 !important;
}
details[open] {
    border-color: #A3BFA8 !important;
}
details[open] summary {
    color: #F5F5F5 !important;
    border-bottom: 1px solid #3A3A3A;
}

/* ── Tabs ─────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #3A3A3A !important;
    gap: 0.1rem;
}
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #858585 !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: color 0.15s ease, border-color 0.15s ease;
}
button[data-baseweb="tab"]:hover {
    color: #B4B4B4 !important;
    background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #A3BFA8 !important;
    border-bottom-color: #A3BFA8 !important;
    background: transparent !important;
}
button[data-baseweb="tab"] p {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}
[data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 1rem !important;
}

/* ── Radio buttons ────────────────────────────────────────────────── */
div[role="radiogroup"] label {
    font-size: 0.88rem !important;
    color: #B4B4B4 !important;
    padding: 4px 8px !important;
    border-radius: var(--radius-sm) !important;
}
div[role="radiogroup"] label:hover {
    color: #F5F5F5 !important;
}

/* ── Dataframe / table ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
}
[data-testid="stTable"] table {
    background: #242424 !important;
    border-collapse: collapse;
    width: 100%;
}
[data-testid="stTable"] th {
    background: #2B2B2B !important;
    color: #A3BFA8 !important;
    border-bottom: 1px solid #3A3A3A !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 0.8rem !important;
}
[data-testid="stTable"] td {
    color: #B4B4B4 !important;
    border-bottom: 1px solid #3A3A3A !important;
    font-size: 0.87rem !important;
    padding: 0.55rem 0.8rem !important;
}
[data-testid="stTable"] tr:hover td {
    background: #2B2B2B !important;
    color: #F5F5F5 !important;
}
/* Markdown tables ─────────────────────────────────────────────────── */
.stMarkdown table {
    background: #242424;
    border-collapse: collapse;
    width: 100%;
    border: 1px solid #3A3A3A;
    border-radius: var(--radius-md);
    overflow: hidden;
}
.stMarkdown th {
    background: #2B2B2B !important;
    color: #A3BFA8 !important;
    border-bottom: 1px solid #3A3A3A !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 0.8rem !important;
    text-align: left !important;
}
.stMarkdown td {
    color: #B4B4B4 !important;
    border-bottom: 1px solid #3A3A3A !important;
    font-size: 0.87rem !important;
    padding: 0.55rem 0.8rem !important;
}
.stMarkdown tr:last-child td {
    border-bottom: none !important;
}

/* ── Chat messages ────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}
/* User message bubble */
[data-testid="stChatMessage"][data-testid*="user"],
[data-testid="stChatMessageContainer"][data-role="user"] {
    background: #2B2B2B !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.8rem 1rem !important;
    margin: 0.4rem 0 !important;
}
.stChatMessage p {
    font-size: 0.95rem;
    line-height: 1.7;
    color: #F5F5F5 !important;
}
/* User turns use a restrained elevated bubble; assistant turns stay open. */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.8rem 1rem !important;
    margin: 0.45rem 0 0.75rem auto !important;
    max-width: 92%;
}

/* ── Chat input ───────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: #242424 !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-lg) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #A3BFA8 !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #F5F5F5 !important;
}
[data-testid="stChatInput"] button {
    background-color: #A3BFA8 !important;
    color: #171717 !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"] button:hover {
    background-color: #B8D0BC !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Links follow the shared accent across every page. */
.stMarkdown a, a:not([data-testid]) {
    color: var(--accent) !important;
}
.stMarkdown a:hover, a:not([data-testid]):hover {
    color: var(--accent-hover) !important;
}

/* ── Caption / muted text ─────────────────────────────────────────── */
.stCaption, [data-testid="stCaption"], small {
    color: #858585 !important;
    font-size: 0.82rem !important;
}

/* ── Code blocks ──────────────────────────────────────────────────── */
code {
    background: #2B2B2B !important;
    color: #A3BFA8 !important;
    border-radius: 4px !important;
    padding: 0.1em 0.35em !important;
    font-size: 0.87em !important;
}

/* ── Horizontal rule ──────────────────────────────────────────────── */
hr {
    border-color: #3A3A3A !important;
    margin: 1rem 0 !important;
}

/* ── Spinner ──────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: #A3BFA8 !important;
}

/* ── Location onboarding ──────────────────────────────────────────── */
.sf-location-hero {
    position: relative;
    isolation: isolate;
    display: flex;
    min-height: 200px;
    align-items: flex-end;
    overflow: hidden;
    margin: 0.35rem 0 1.5rem;
    padding: 1.6rem 2rem;
    border: 1px solid #3A3A3A;
    border-radius: 20px;
    background: linear-gradient(110deg, #242424 0%, #2B2B2B 60%, #252525 100%);
}
.sf-location-art {
    position: absolute;
    z-index: -1;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0.4;
}
.sf-location-copy {
    position: relative;
    max-width: 70%;
    padding: 1rem 1.4rem 1rem 0;
}
.sf-location-title {
    display: block;
    margin: 0 0 0.6rem;
    color: #F5F5F5;
    font-size: clamp(1.7rem, 3.2vw, 2.5rem);
    font-weight: 700;
    line-height: 1.2;
}
.sf-location-description {
    display: block;
    color: #B4B4B4;
    font-size: 1rem;
    line-height: 1.6;
}

/* ── Panel containers (location, crop, field) ─────────────────────── */
.st-key-location-panel,
.st-key-crop-panel,
.st-key-field-panel {
    margin: 0.8rem 0 1.2rem;
    padding: 1.2rem 1.4rem 1.1rem;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-lg) !important;
    background: #242424 !important;
}
.st-key-location-panel h3,
.st-key-crop-panel h3,
.st-key-field-panel h3 {
    color: #F5F5F5 !important;
}
.st-key-location-panel [data-testid="stWidgetLabel"] p,
.st-key-crop-panel [data-testid="stWidgetLabel"] p,
.st-key-field-panel [data-testid="stWidgetLabel"] p {
    color: #B4B4B4 !important;
    font-weight: 500 !important;
}

/* Save profile button container ──────────────────────────────────── */
.st-key-save-profile {
    max-width: 420px;
    margin: 0.9rem auto 1rem;
}

/* ── Profile chips ────────────────────────────────────────────────── */
.profile-chip {
    display: inline-block;
    background: #2B2B2B;
    color: #A3BFA8;
    border: 1px solid #3A3A3A;
    border-radius: 9999px;
    padding: 3px 10px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 2px;
}

/* ── Page link button ─────────────────────────────────────────────── */
[data-testid="stPageLink"] a {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #2B2B2B !important;
    color: #B4B4B4 !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.88rem !important;
    text-decoration: none !important;
    transition: border-color 0.15s ease, color 0.15s ease;
    width: 100%;
    justify-content: center;
}
[data-testid="stPageLink"] a:hover {
    border-color: #A3BFA8 !important;
    color: #A3BFA8 !important;
}

/* ── Link buttons (st.link_button) ───────────────────────────────── */
a[data-testid="stLinkButton"],
a[data-testid="stBaseButton-secondary"] {
    background: #2B2B2B !important;
    color: #B4B4B4 !important;
    border: 1px solid #3A3A3A !important;
    border-radius: var(--radius-md) !important;
    transition: border-color 0.15s ease, color 0.15s ease;
}
a[data-testid="stLinkButton"]:hover,
a[data-testid="stBaseButton-secondary"]:hover {
    border-color: #A3BFA8 !important;
    color: #A3BFA8 !important;
}

/* ── Spinner ──────────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: #A3BFA8 !important;
}

/* ── Mobile responsiveness ────────────────────────────────────────── */
@media (max-width: 768px) {
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    .sf-hero { padding: 1.4rem 1.4rem 1.2rem; border-radius: 14px; }
    .sf-hero-title { font-size: 1.7rem; }
    .sf-card { padding: 0.85rem 1rem; }
    .sf-feature-grid { grid-template-columns: 1fr; }
    .sf-location-hero { min-height: 190px; padding: 1rem 1.15rem; border-radius: 16px; }
    .sf-location-art { opacity: 0.25; }
    .sf-location-copy { max-width: 100%; padding-right: 0; }
    .sf-location-title { font-size: 1.5rem; }
    .sf-location-description { font-size: 0.95rem; }
    .st-key-location-panel, .st-key-crop-panel, .st-key-field-panel { padding: 1rem; border-radius: 14px; }
    .st-key-save-profile { max-width: none; }
}
</style>
"""


def inject_css() -> None:
    """Inject global CSS once per page render."""
    st.markdown(_CSS, unsafe_allow_html=True)
    # Use the translated shared page links below as the only navigation list.
    # Streamlit's generated multipage list is English-only and duplicates them.
    st.markdown(
        "<style>section[data-testid='stSidebarNav'],div[data-testid='stSidebarNav'],[data-testid='stSidebarNav']{display:none !important;}</style>",
        unsafe_allow_html=True,
    )


# ── Session state ─────────────────────────────────────────────────────────────

def init_session_state() -> None:
    """
    Ensure all shared session state keys exist with safe defaults.
    Call this at the top of every page before reading session state.
    Profile is NEVER reset when language changes.
    """
    if st.session_state.get("language") not in LANGUAGE_CODES:
        st.session_state.language = "English"
    # Keep the code derived from the selected display name so the UI and RAG
    # prompts cannot drift into different languages.
    st.session_state.lang_code = LANGUAGE_CODES[st.session_state.language]
    if "farmer_profile" not in st.session_state:
        st.session_state.farmer_profile = st.session_state.get("profile", {})
    if not isinstance(st.session_state.farmer_profile, dict):
        st.session_state.farmer_profile = {}
    # `profile` remains a compatibility alias for existing modules. Both names
    # point to the same dictionary; there is only one profile state to update.
    st.session_state.profile = st.session_state.farmer_profile
    for key, field in (("selected_state", "state"), ("selected_district", "district"), ("selected_village", "locality")):
        if key not in st.session_state:
            st.session_state[key] = st.session_state.farmer_profile.get(field, "")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "onboarding_started" not in st.session_state:
        st.session_state.onboarding_started = bool(
            st.session_state.get("onboarding_language_selected", False)
            or st.session_state.farmer_profile.get("state")
        )
    if "onboarding_completed" not in st.session_state:
        st.session_state.onboarding_completed = bool(st.session_state.farmer_profile.get("state"))
    # Backward-compatible flag for any existing page code still reading it.
    st.session_state.onboarding_language_selected = st.session_state.onboarding_started


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(page_title: str = "") -> str:
    """
    Render the common sidebar used by every page.
    Returns the current lang_code (may have changed if user switched language).

    The profile is preserved across language switches.
    """
    lang = st.session_state.lang_code
    logo_uri = _app_logo_data_uri()

    with st.sidebar:
        # ── Logo and app name ──────────────────────────────────────────────
        st.markdown(
            '<div style="display:flex;align-items:center;gap:0.65rem;padding:0.2rem 0 0.7rem;">'
            f'<img src="{logo_uri}" alt="Smart Farming AI logo" width="44" height="44" '
            'style="display:block;flex:0 0 44px;">'
            '<span style="font-size:1.1rem;font-weight:700;color:#F5F5F5;letter-spacing:-0.02em;line-height:1.15;">'
            'Smart Farming AI</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr style="border-color:#3A3A3A;margin:0.4rem 0 0.75rem;">', unsafe_allow_html=True)

        # ── Language selector ──────────────────────────────────────────────
        st.markdown(
            f'<p style="font-size:0.75rem;color:#858585;font-weight:500;margin:0 0 0.3rem;text-transform:uppercase;letter-spacing:0.05em;">'
            f'{get_label("select_language", lang)}</p>',
            unsafe_allow_html=True,
        )
        new_lang_display = st.selectbox(
            get_label("select_language", lang),
            options=list(LANGUAGE_CODES.keys()),
            index=list(LANGUAGE_CODES.keys()).index(st.session_state.language),
            key="language_selector",
            label_visibility="collapsed",
        )
        if new_lang_display != st.session_state.language:
            # Preserve profile; only update language keys
            st.session_state.language = new_lang_display
            st.session_state.lang_code = LANGUAGE_CODES[new_lang_display]
            st.session_state.farmer_profile["language"] = new_lang_display
            st.session_state.farmer_profile["lang_code"] = LANGUAGE_CODES[new_lang_display]
            st.rerun()

        st.markdown('<hr style="border-color:#3A3A3A;margin:0.75rem 0;">', unsafe_allow_html=True)

        # ── Provider badge ─────────────────────────────────────────────────
        if LLM_PROVIDER == "ibm_granite":
            st.markdown(
                '<div style="background:rgba(163,191,168,0.1);border:1px solid rgba(163,191,168,0.25);'
                'border-radius:8px;padding:0.45rem 0.7rem;margin-bottom:0.5rem;">'
                f'<span style="font-size:0.8rem;color:#A3BFA8;font-weight:600;">{get_label("ibm_granite_mode", lang)}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="background:rgba(229,181,103,0.08);border:1px solid rgba(229,181,103,0.2);'
                'border-radius:8px;padding:0.45rem 0.7rem;margin-bottom:0.5rem;">'
                '<span style="font-size:0.8rem;color:#E5B567;font-weight:600;">◈ Demo Mode</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="border-color:#3A3A3A;margin:0.5rem 0 0.75rem;">', unsafe_allow_html=True)

        # ── Profile summary ────────────────────────────────────────────────
        _render_profile_chip(lang)

        st.markdown('<hr style="border-color:#3A3A3A;margin:0.75rem 0;">', unsafe_allow_html=True)

        # ── Navigation appears after the farmer has completed location setup ──
        nav_items = [
            ("🏠", get_label("home", lang), "app.py"),
            ("👤", get_label("farmer_profile", lang), "pages/1_Farmer_Profile.py"),
            ("🌱", get_label("crop_explorer", lang), "pages/2_Crop_Explorer.py"),
            ("📋", get_label("crop_roadmap", lang), "pages/3_Crop_Roadmap.py"),
            ("🤖", get_label("ai_assistant", lang), "pages/4_AI_Farming_Assistant.py"),
            ("🌿", get_label("natural_farming", lang), "pages/5_Natural_Farming.py"),
            ("🐛", get_label("pest_management", lang), "pages/6_Pest_Management.py"),
            ("⛈️", get_label("weather_safety", lang), "pages/7_Weather_and_Safety.py"),
            ("💰", get_label("market_guidance", lang), "pages/8_Market_Guidance.py"),
        ]
        if st.session_state.get("profile", {}).get("state"):
            st.markdown(
                f'<p style="font-size:0.72rem;color:#858585;font-weight:500;margin:0 0 0.5rem;'
                f'text-transform:uppercase;letter-spacing:0.05em;">{get_label("navigation", lang)}</p>',
                unsafe_allow_html=True,
            )
            for icon, label, link in nav_items:
                st.page_link(link, label=label, icon=icon)

    return st.session_state.lang_code


def _render_profile_chip(lang: str) -> None:
    """Compact profile summary in the sidebar."""
    p = st.session_state.profile
    label = get_label("your_profile_sidebar", lang)
    st.markdown(
        f'<p style="font-size:0.75rem;color:#858585;font-weight:500;margin:0 0 0.5rem;'
        f'text-transform:uppercase;letter-spacing:0.05em;">{label}</p>',
        unsafe_allow_html=True,
    )

    if not p.get("state"):
        st.markdown(
            f'<p style="font-size:0.83rem;color:#858585;margin:0;">'
            f'{get_label("setup_profile_hint", lang)}</p>',
            unsafe_allow_html=True,
        )
        return

    chips = []
    if p.get("state"):
        chips.append(f"📍 {p['state']}")
    if p.get("district"):
        chips.append(f"🏘 {p['district']}")
    if p.get("crop"):
        chips.append(f"🌾 {p['crop']}")
    if p.get("soil_type"):
        chips.append(f"🧱 {p['soil_type']}")
    if p.get("irrigation"):
        chips.append(f"💧 {p['irrigation']}")

    for chip in chips:
        st.markdown(
            f'<span class="profile-chip">{chip}</span>',
            unsafe_allow_html=True,
        )
    if chips:
        st.markdown("")  # spacer
