"""
pages/7_Weather_and_Safety.py
Weather hazards and farmer safety — full i18n.
Safety information always takes priority.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
from src.config import APP_TITLE, DATA_DIR
from src.language_service import get_label
from src.content_localization import localize_content, safety_label
from src.shared_utils import inject_css, init_session_state, render_sidebar
from src.farming_advisor import ask

st.set_page_config(page_title=f"{get_label('weather_safety','en')} — {APP_TITLE}", page_icon="⛈️", layout="wide")
init_session_state()
inject_css()
lang = render_sidebar("weather_safety")

@st.cache_data
def _load_safety():
    path = DATA_DIR / "farmer_safety.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

safety_data = _load_safety()

st.title(f"⛈️ {get_label('weather_safety', lang)}")
st.error(get_label("emergency_notice", lang))
st.markdown("---")
st.info(get_label("live_weather_notice", lang))

with st.sidebar:
    st.markdown("---")
    st.markdown(f"**{get_label('emergency_contacts', lang)}**")
    st.markdown(
        f"🚨 **112** {safety_label('emergency', lang)}  \n"
        f"🚑 **108** {safety_label('ambulance', lang)}  \n"
        f"🔥 **101** {safety_label('fire', lang)}  \n"
        f"⚡ **1912** {safety_label('electricity', lang)}  \n"
        f"🌊 **1078** {safety_label('ndma', lang)}  \n"
        f"☠️ **1800-11-6666** {safety_label('poison', lang)}"
    )

hazards = safety_data.get("weather_hazards", [])
practices = safety_data.get("safety_practices", [])

HAZARD_ICONS = {
    "cyclone":"🌀","strong_winds":"💨","heavy_rain":"🌧️",
    "flooding":"🌊","lightning":"⚡","heatwave":"🌡️","drought":"🌵",
}
PRIORITY_COLOUR = {"CRITICAL":"error","HIGH":"warning","MEDIUM":"info"}

tab_weather, tab_elec, tab_pest, tab_gen, tab_ask = st.tabs([
    get_label("weather_hazards_tab", lang),
    get_label("electrical_safety_tab", lang),
    get_label("pesticide_safety_tab", lang),
    get_label("general_health_tab", lang),
    get_label("ask_safety_tab", lang),
])

with tab_weather:
    hazard_labels = {
        h.get("name", {}).get(lang) or h.get("name", {}).get("en", h.get("id", "")): h
        for h in hazards
    }
    sel_hazard = st.selectbox(get_label("select_hazard", lang), list(hazard_labels.keys()))
    hazard = hazard_labels.get(sel_hazard, {})

    if hazard:
        hid = hazard.get("id", "")
        icon = HAZARD_ICONS.get(hid, "⛈️")
        priority = hazard.get("priority", "MEDIUM")
        colour_fn = getattr(st, PRIORITY_COLOUR.get(priority, "info"))
        colour_fn(
            f"{icon} **{get_label('safety_warning', lang)} — "
            f"{safety_label('priority', lang)}: "
            f"{safety_label(priority.lower(), lang)}**"
        )

        for section, label, emoji in [
            ("before","before","📋"),("during","during","🚨"),("after","after","✅"),
            ("practices","practices","📌"),
            ("farmer_health","farmer_health","🏥"),("crop_protection","crop_protection","🌾"),
        ]:
            items = hazard.get(section, [])
            if items:
                st.markdown(f"### {emoji} {safety_label(label, lang)}")
                for item in items:
                    display_item = localize_content(item, lang)
                    if "NEVER" in item or "DO NOT" in item:
                        st.error(f"🔴 {display_item}")
                    elif "SAFETY" in item or "WARNING" in item or "CALL" in item:
                        st.warning(f"⚠️ {display_item}")
                    else:
                        st.markdown(f"- {display_item}")
        contacts = localize_content(hazard.get("emergency_contacts", ""), lang)
        if contacts:
            st.info(f"📞 **{get_label('emergency_contacts', lang)}**: {contacts}")

with tab_elec:
    elec = next((p for p in practices if p.get("id") == "electrical_safety"), None)
    if elec:
        name = elec.get("name", {}).get(lang) or elec.get("name", {}).get("en", "Electrical Safety")
        st.markdown(f"## ⚡ {name}")
        st.error(
            f"🔴 **{safety_label('priority', lang)}: "
            f"{safety_label('critical', lang)}** — {get_label('safety_warning', lang)}"
        )
        for rule in elec.get("rules", []):
            display_rule = localize_content(rule, lang)
            if any(kw in rule for kw in ("NEVER","ALWAYS","MANDATORY","CRITICAL")):
                st.error(f"🔴 {display_rule}")
            else:
                st.markdown(f"- {display_rule}")

with tab_pest:
    ps = next((p for p in practices if p.get("id") == "pesticide_safety"), None)
    if ps:
        name = ps.get("name", {}).get(lang) or ps.get("name", {}).get("en", "Pesticide Safety")
        st.markdown(f"## 💊 {name}")
        st.error(
            f"🔴 **{safety_label('priority', lang)}: "
            f"{safety_label('critical', lang)}** — {get_label('safety_warning', lang)}"
        )
        for rule in ps.get("rules", []):
            display_rule = localize_content(rule, lang)
            if any(kw in rule.upper() for kw in ("NEVER","ALWAYS","PPE","WEAR","HOSPITAL","POISON")):
                st.error(f"🔴 {display_rule}")
            elif any(kw in rule for kw in ("READ","LABEL","STORE")):
                st.warning(f"⚠️ {display_rule}")
            else:
                st.markdown(f"- {display_rule}")
        st.info(
            f"☎️ {safety_label('poison_control', lang)}: **1800-11-6666** "
            f"({safety_label('poison_control_detail', lang)})"
        )

with tab_gen:
    gen = next((p for p in practices if p.get("id") == "general_health"), None)
    if gen:
        name = gen.get("name", {}).get(lang) or gen.get("name", {}).get("en", "General Health")
        st.markdown(f"## 🌡️ {name}")
        for rule in gen.get("rules", []):
            display_rule = localize_content(rule, lang)
            if "HEAT STROKE" in rule.upper() or "URGENT" in rule.upper():
                st.error(f"🔴 {display_rule}")
            else:
                st.markdown(f"- {display_rule}")

with tab_ask:
    st.subheader(get_label("ask_safety_tab", lang))
    safety_q = st.text_area(
        get_label("ask_safety_question", lang),
        placeholder=get_label("safety_question_placeholder", lang),
        height=80,
    )
    if st.button(get_label("get_safety_guidance", lang), key="safety_ask"):
        if not safety_q.strip():
            st.warning(get_label("enter_question", lang))
        else:
            with st.spinner(get_label("loading", lang)):
                result = ask(safety_q, lang_code=lang, profile=st.session_state.profile)
            if result.is_demo:
                st.info(get_label("demo_mode_notice", lang))
            st.markdown(result.answer)
            if result.sources:
                with st.expander(get_label("sources", lang)):
                    for s in result.sources:
                        st.markdown(f"- {s}")

st.markdown("---")
with st.expander(get_label("official_resources", lang)):
    st.markdown(
        f"| {safety_label('resource', lang)} | {safety_label('link', lang)} |\n"
        f"|---|---|\n"
        f"| IMD {safety_label('resource_weather', lang)} | [mausam.imd.gov.in](https://mausam.imd.gov.in) |\n"
        f"| IMD {safety_label('resource_agromet', lang)} | [imdagrimet.gov.in](https://imdagrimet.gov.in) |\n"
        f"| NDMA {safety_label('resource_safety', lang)} | [ndma.gov.in](https://ndma.gov.in) |\n"
        f"| NDMA SACHET {safety_label('resource_dos_donts', lang)} | [sachet.ndma.gov.in](https://sachet.ndma.gov.in/DosDont) |\n"
        "| PM Fasal Bima Yojana | [pmfby.gov.in](https://pmfby.gov.in) |"
    )

st.caption(safety_label("source_caption", lang))
