"""
pages/5_Natural_Farming.py
Natural farming and soil health guidance — full i18n.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
from src.config import APP_TITLE, DATA_DIR
from src.language_service import get_label
from src.content_localization import localize_content
from src.shared_utils import inject_css, init_session_state, render_sidebar
from src.farming_advisor import ask

st.set_page_config(page_title=f"{get_label('natural_farming','en')} — {APP_TITLE}", page_icon="🌿", layout="wide")
init_session_state()
inject_css()
lang = render_sidebar("natural_farming")

@st.cache_data
def _load_nf():
    path = DATA_DIR / "natural_farming.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

nf_data = _load_nf()
practices = nf_data.get("practices", [])

PRACTICE_ICONS = {
    "compost":"🌿","farmyard_manure":"🐄","vermicompost":"🪱","green_manure":"🌱",
    "neem_products":"🌳","mulching":"🍂","crop_rotation":"🔄","soil_testing":"🧪",
    "organic_matter_improvement":"⬆️","biological_pest_management":"🐞",
}

SUITABLE_CROP_NAMES = {
    "ta": {"rice": "நெல்", "wheat": "கோதுமை", "maize": "மக்காச்சோளம்", "vegetables": "காய்கறிகள்", "sugarcane": "கரும்பு", "all crops": "அனைத்துப் பயிர்கள்", "flowers": "மலர்கள்", "fruit crops": "பழப் பயிர்கள்", "nursery": "நாற்றங்கால்", "any crop": "எந்தப் பயிரும்", "cotton": "பருத்தி", "pulses": "பருப்பு வகைகள்", "ginger": "இஞ்சி", "turmeric": "மஞ்சள்", "strawberry": "ஸ்ட்ராபெரி", "banana": "வாழை"},
    "te": {"rice": "వరి", "wheat": "గోధుమ", "maize": "మొక్కజొన్న", "vegetables": "కూరగాయలు", "sugarcane": "చెరకు", "all crops": "అన్ని పంటలు", "flowers": "పూలు", "fruit crops": "పండ్ల పంటలు", "nursery": "నర్సరీ", "any crop": "ఏ పంటైనా", "cotton": "పత్తి", "pulses": "పప్పుధాన్యాలు", "ginger": "అల్లం", "turmeric": "పసుపు", "strawberry": "స్ట్రాబెర్రీ", "banana": "అరటి"},
    "hi": {"rice": "धान", "wheat": "गेहूँ", "maize": "मक्का", "vegetables": "सब्ज़ियाँ", "sugarcane": "गन्ना", "all crops": "सभी फसलें", "flowers": "फूल", "fruit crops": "फल वाली फसलें", "nursery": "नर्सरी", "any crop": "कोई भी फसल", "cotton": "कपास", "pulses": "दलहन", "ginger": "अदरक", "turmeric": "हल्दी", "strawberry": "स्ट्रॉबेरी", "banana": "केला"},
}

st.title(f"🌿 {get_label('natural_farming', lang)}")
st.markdown(get_label("natural_farming_intro", lang))
st.warning(
    get_label("precautions", lang) + ": " + (
        "'Natural' does not automatically mean safe. Follow all precautions for each practice. "
        "This module does not provide homemade pesticide formulations."
        if lang == "en" else
        "இயற்கை' என்பது தானாகவே பாதுகாப்பானது என்று அர்த்தமில்லை."
        if lang == "ta" else
        "'సహజం' అంటే స్వయంచాలకంగా సురక్షితమని కాదు."
        if lang == "te" else
        "'प्राकृतिक' का अर्थ स्वतः सुरक्षित नहीं है।"
    )
)
st.markdown("---")

practice_map: dict[str, str] = {}
for p in practices:
    pid = p.get("id", "")
    name = p.get("name", {}).get(lang) or p.get("name", {}).get("en", pid)
    icon = PRACTICE_ICONS.get(pid, "🌿")
    practice_map[f"{icon} {name}"] = pid

selected_label = st.selectbox(get_label("select_practice", lang), list(practice_map.keys()))
selected_id = practice_map.get(selected_label, "")

current = next((p for p in practices if p.get("id") == selected_id), None)

if current:
    name_lang = current.get("name", {}).get(lang) or current.get("name", {}).get("en", "")
    st.markdown(f"## {PRACTICE_ICONS.get(selected_id, '🌿')} {name_lang}")
    st.markdown("---")
    st.markdown(f"**{get_label(current.get('category', ''), lang) or current.get('category','').replace('_',' ').title()}**")
    st.markdown(localize_content(current.get("description", ""), lang))

    col1, col2 = st.columns(2)
    with col1:
        for sec, label_key in [("preparation","preparation"),("how_to","preparation"),
                                ("methods","preparation"),("examples","preparation")]:
            items = current.get(sec, [])
            if items:
                st.markdown(f"### {get_label(label_key, lang)}")
                for item in items:
                    st.markdown(f"- {localize_content(item, lang)}")
        if "application" in current:
            st.markdown(f"### {get_label('application', lang)}")
            st.markdown(localize_content(current["application"], lang))

    with col2:
        if "benefits" in current:
            st.markdown(f"### {get_label('benefits', lang)}")
            for b in current["benefits"]:
                st.success(f"✅ {localize_content(b, lang)}")
        if "precautions" in current:
            st.markdown(f"### {get_label('precautions', lang)}")
            for p in current["precautions"]:
                st.warning(f"⚠️ {localize_content(p, lang)}")

    if "suitable_crops" in current:
        crop_names = SUITABLE_CROP_NAMES.get(lang, {})
        st.markdown(f"**{get_label('suitable_for', lang)}**: " + ", ".join(crop_names.get(c, c) for c in current["suitable_crops"]))

st.markdown("---")
st.subheader(get_label("ask_natural_farming", lang))
nf_question = st.text_area(
    f"{get_label('ask_question', lang)} ({st.session_state.language})",
    placeholder=get_label("nf_question_placeholder", lang),
    height=80,
)

if st.button(get_label("get_guidance", lang), key="nf_ask"):
    if not nf_question.strip():
        st.warning(get_label("enter_question", lang))
    else:
        with st.spinner(get_label("loading", lang)):
            result = ask(f"natural farming {nf_question}", lang_code=lang,
                         profile=st.session_state.profile)
        if result.is_demo:
            st.info(get_label("demo_mode_notice", lang))
        st.markdown(result.answer)
        if result.sources:
            with st.expander(get_label("sources", lang)):
                for s in result.sources:
                    st.markdown(f"- {s}")
        if result.confidence:
            st.caption(result.confidence)

st.markdown("---")
st.caption("Source: NITI Aayog Natural Farming Toolkit, ICAR, state agriculture department resources.")
