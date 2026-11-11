"""
pages/3_Crop_Roadmap.py
Step-by-step crop lifecycle roadmap — full i18n.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
from src.config import APP_TITLE, DATA_DIR
from src.language_service import get_label
from src.content_localization import localize_content
from src.shared_utils import APP_LOGO_DATA_URI, inject_css, init_session_state, render_sidebar
from src.farming_advisor import ask

st.set_page_config(page_title=f"{get_label('crop_roadmap','en')} — {APP_TITLE}", page_icon=APP_LOGO_DATA_URI, layout="wide")
init_session_state()
inject_css()
lang = render_sidebar("crop_roadmap")

@st.cache_data
def _load_roadmaps():
    path = DATA_DIR / "crop_roadmaps.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def _load_crops():
    path = DATA_DIR / "crops.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)

roadmaps = _load_roadmaps()
crops_list = _load_crops()

ROADMAP_CROP_IDS = [k for k in roadmaps.keys() if not k.startswith("_")]

# Build display name → crop_id map using the selected language name
crop_name_map: dict[str, str] = {}
for crop in crops_list:
    cid = crop.get("id", "")
    if cid in ROADMAP_CROP_IDS:
        name_lang = crop.get("name", {}).get(lang) or crop.get("name", {}).get("en", cid)
        name_en = crop.get("name", {}).get("en", cid)
        display = name_lang if name_lang != name_en else name_en
        crop_name_map[display] = cid

# Also add any roadmap crops not in the crop catalogue
for cid in ROADMAP_CROP_IDS:
    if cid not in crop_name_map.values():
        crop_name_map[cid.replace("_", " ").title()] = cid

STAGE_ICONS = {1:"🔨",2:"🧪",3:"🌱",4:"🌾",5:"💧",6:"🌿",7:"🌿",8:"🔍",9:"🌿",10:"🚜",11:"📦",12:"💰"}

ROADMAP_COPY = {
    "en": {
        "stage": "Stage", "seasons": "Seasons", "duration": "Duration / Timing",
        "no_stages": "No stages found for this crop.",
        "stage_names": ["Land Preparation", "Soil Testing and Field Arrangement", "Seed Selection and Preparation", "Sowing / Transplantation", "Irrigation Management", "Nutrient Management", "Weed Management", "Pest and Disease Monitoring", "Natural Farming Practices", "Harvesting", "Drying and Storage", "Market Guidance"],
    },
    "ta": {
        "stage": "நிலை", "seasons": "பருவங்கள்", "duration": "கால அளவு / நேரம்",
        "no_stages": "இந்தப் பயிருக்கான நிலைகள் இல்லை.",
        "stage_names": ["நிலம் தயாரித்தல்", "மண் பரிசோதனை மற்றும் வயல் அமைப்பு", "விதைத் தேர்வு மற்றும் தயாரிப்பு", "விதைத்தல் / நடவு", "நீர்ப்பாசன மேலாண்மை", "ஊட்டச்சத்து மேலாண்மை", "களை மேலாண்மை", "பூச்சி மற்றும் நோய் கண்காணிப்பு", "இயற்கை விவசாய முறைகள்", "அறுவடை", "உலர்த்துதல் மற்றும் சேமிப்பு", "சந்தை வழிகாட்டுதல்"],
    },
    "te": {
        "stage": "దశ", "seasons": "సాగు కాలాలు", "duration": "వ్యవధి / సమయం",
        "no_stages": "ఈ పంటకు దశలు కనుగొనబడలేదు.",
        "stage_names": ["భూమి తయారీ", "మట్టి పరీక్ష మరియు పొలం ఏర్పాటు", "విత్తనాల ఎంపిక మరియు తయారీ", "విత్తడం / నాటడం", "నీటిపారుదల నిర్వహణ", "పోషకాల నిర్వహణ", "కలుపు మొక్కల నిర్వహణ", "తెగుళ్లు మరియు వ్యాధుల పర్యవేక్షణ", "సహజ వ్యవసాయ పద్ధతులు", "కోత", "ఎండబెట్టడం మరియు నిల్వ", "మార్కెట్ మార్గదర్శకం"],
    },
    "hi": {
        "stage": "चरण", "seasons": "मौसम", "duration": "अवधि / समय",
        "no_stages": "इस फसल के लिए कोई चरण नहीं मिले।",
        "stage_names": ["खेत की तैयारी", "मिट्टी की जाँच और खेत की व्यवस्था", "बीज चयन और तैयारी", "बुवाई / रोपाई", "सिंचाई प्रबंधन", "पोषक तत्व प्रबंधन", "खरपतवार प्रबंधन", "कीट और रोग निगरानी", "प्राकृतिक खेती के तरीके", "कटाई", "सुखाना और भंडारण", "बाजार मार्गदर्शन"],
    },
}
roadmap_copy = ROADMAP_COPY.get(lang, ROADMAP_COPY["en"])

st.title(f"📋 {get_label('crop_roadmap', lang)}")
st.markdown(get_label("crop_roadmap_intro", lang))
st.markdown("---")

# Pre-select from profile
profile = st.session_state.profile
profile_crop_id = profile.get("crop_id", "")
display_options = sorted(crop_name_map.keys())
default_display = next(
    (d for d, cid in crop_name_map.items() if cid == profile_crop_id),
    display_options[0] if display_options else None,
)
default_idx = display_options.index(default_display) if default_display in display_options else 0

selected_display = st.selectbox(get_label("select_crop", lang), display_options, index=default_idx)
selected_crop_id = crop_name_map.get(selected_display, "")

if not selected_crop_id or selected_crop_id not in roadmaps:
    st.info(get_label("no_roadmap_available", lang))
    st.stop()

roadmap = roadmaps[selected_crop_id]
crop_name = selected_display
seasons = roadmap.get("seasons", "")

st.subheader(f"🌾 {crop_name}")
st.markdown(f"**{roadmap_copy['seasons']}**: {localize_content(seasons, lang)}")
st.markdown("---")

stages = roadmap.get("stages", [])
if not stages:
    st.warning(roadmap_copy["no_stages"])
    st.stop()

stage_names = [
    f"{roadmap_copy['stage']} {s['stage']}: "
    f"{roadmap_copy['stage_names'][s['stage'] - 1] if 1 <= s['stage'] <= len(roadmap_copy['stage_names']) else s['name']}"
    for s in stages
]
selected_stage_label = st.radio(
    get_label("select_lifecycle_stage", lang),
    stage_names,
    horizontal=True,
)
selected_stage_num = stages[stage_names.index(selected_stage_label)]["stage"]
current_stage = next((s for s in stages if s["stage"] == selected_stage_num), stages[0])

icon = STAGE_ICONS.get(current_stage["stage"], "📌")
localized_stage_name = (
    roadmap_copy["stage_names"][current_stage["stage"] - 1]
    if 1 <= current_stage["stage"] <= len(roadmap_copy["stage_names"])
    else current_stage["name"]
)
st.markdown(f"## {icon} {roadmap_copy['stage']} {current_stage['stage']}: {localized_stage_name}")
st.markdown(f"**{roadmap_copy['duration']}**: {localize_content(current_stage.get('duration', ''), lang)}")
st.markdown("---")

col_tasks, col_warnings = st.columns([2, 1])

with col_tasks:
    st.markdown(f"### {get_label('tasks', lang)}")
    for task in current_stage.get("tasks", []):
        st.markdown(f"- {localize_content(task, lang)}")

with col_warnings:
    warnings = current_stage.get("warnings", [])
    if warnings:
        st.markdown(f"### {get_label('warnings', lang)}")
        for w in warnings:
            if "SAFETY" in w.upper() or "ELECTRICAL" in w.upper() or "ELECTROCUTE" in w.upper():
                st.error(f"🔴 {localize_content(w, lang)}")
            else:
                st.warning(f"⚠️ {localize_content(w, lang)}")

st.markdown("---")
with st.expander(get_label("view_all_stages", lang)):
    for s in stages:
        stage_name = roadmap_copy["stage_names"][s["stage"] - 1] if 1 <= s["stage"] <= len(roadmap_copy["stage_names"]) else s["name"]
        st.markdown(f"**{roadmap_copy['stage']} {s['stage']}: {stage_name}** — {localize_content(s.get('duration', ''), lang)}")

st.markdown("---")
st.subheader(f"💬 {get_label('ask_about_stage', lang)}: {localized_stage_name}")
st.markdown(f"{get_label('ask_question', lang)} ({st.session_state.language})")

q_key = f"roadmap_q_{selected_crop_id}_{selected_stage_num}"
question = st.text_area(
    f"{crop_name} — {localized_stage_name}",
    key=q_key,
    height=80,
)

if st.button(get_label("get_guidance", lang), key=f"btn_{selected_crop_id}_{selected_stage_num}"):
    if not question.strip():
        st.warning(get_label("enter_question", lang))
    else:
        with st.spinner(get_label("loading", lang)):
            profile_ctx = dict(profile)
            profile_ctx["crop_id"] = selected_crop_id
            result = ask(
                f"{crop_name} {current_stage['name']}: {question}",
                lang_code=lang,
                profile=profile_ctx,
            )
        if result.is_demo:
            st.info(get_label("demo_mode_notice", lang))
        st.markdown("### 📖")
        st.markdown(result.answer)
        if result.confidence:
            st.caption(result.confidence)
        if result.sources:
            with st.expander(get_label("sources", lang)):
                for s in result.sources:
                    st.markdown(f"- {s}")
