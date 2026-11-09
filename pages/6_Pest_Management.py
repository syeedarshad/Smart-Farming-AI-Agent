"""
pages/6_Pest_Management.py
Pest and disease guidance — full i18n.
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

st.set_page_config(page_title=f"{get_label('pest_management','en')} — {APP_TITLE}", page_icon="🐛", layout="wide")
init_session_state()
inject_css()
lang = render_sidebar("pest_management")

@st.cache_data
def _load_pest_data():
    path = DATA_DIR / "pest_management.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

pest_data = _load_pest_data()

st.title(f"🐛 {get_label('pest_management', lang)}")
st.markdown(get_label("pest_intro", lang))
st.warning(
    "⚠️ " + (
        "Always correctly identify the pest or disease before taking any action. "
        "Consult your local agricultural officer for registered pesticide recommendations."
        if lang == "en" else
        "எந்த நடவடிக்கையும் எடுப்பதற்கு முன் பூச்சி அல்லது நோயைச் சரியாக அடையாளம் காணவும். "
        "பதிவு செய்யப்பட்ட பூச்சிக்கொல்லி பரிந்துரைகளுக்கு உங்கள் உள்ளூர் வேளாண் அலுவலரை அணுகவும்."
        if lang == "ta" else
        "ఏ చర్య తీసుకునే ముందు చీడ లేదా వ్యాధిని సరిగ్గా గుర్తించండి. "
        "నమోదిత పురుగుమందుల సిఫార్సుల కోసం స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి."
        if lang == "te" else
        "कोई कार्रवाई करने से पहले कीट या रोग की सही पहचान करें। "
        "पंजीकृत कीटनाशक की सिफारिश के लिए स्थानीय कृषि अधिकारी से सलाह लें।"
    )
)
st.markdown("---")

mode = st.radio(
    get_label("pest_intro", lang),
    [get_label("browse_by_crop", lang), get_label("ask_by_symptoms", lang)],
    horizontal=True,
)

if mode == get_label("browse_by_crop", lang):
    crops_in_db = pest_data.get("crops", [])
    crop_map = {c["crop_name"]: c for c in crops_in_db}
    sel_crop_name = st.selectbox(get_label("select_crop_label", lang), list(crop_map.keys()))
    crop_entry = crop_map.get(sel_crop_name, {})
    pds = crop_entry.get("pests_diseases", [])

    if not pds:
        st.info(f"{safety_label('no_data', lang)} {get_label('ask_by_symptoms', lang)}")
    else:
        pd_labels = {pd["name"]: pd for pd in pds}
        sel_pd = st.selectbox(get_label("select_pest", lang), list(pd_labels.keys()))
        pd_info = pd_labels.get(sel_pd, {})

        if pd_info:
            pd_type = pd_info.get("type", "")
            type_icon = "🐛" if pd_type == "pest" else "🦠"
            st.markdown(f"## {type_icon} {sel_pd}")
            st.markdown(f"**{safety_label('type', lang)}**: {localize_content(pd_type.title(), lang)}")
            st.markdown("---")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"### {get_label('symptoms_label', lang)}")
                for s in pd_info.get("symptoms", []):
                    st.markdown(f"- {localize_content(s, lang)}")
                st.markdown(
                    f"**{safety_label('favorable_conditions', lang)}**: "
                    f"{localize_content(pd_info.get('favorable_conditions', ''), lang)}"
                )

            with c2:
                st.markdown(f"### {get_label('ipm_approach', lang)}")
                for step in pd_info.get("ipm_approach", []):
                    if "register" in step.lower() or "consult" in step.lower():
                        st.info(f"ℹ️ {localize_content(step, lang)}")
                    else:
                        st.markdown(f"- {localize_content(step, lang)}")

            st.markdown(f"### {get_label('seek_expert', lang)}")
            st.error(f"🏥 {localize_content(pd_info.get('when_to_seek_expert', ''), lang)}")
            st.warning(
                f"⚠️ {localize_content(pd_info.get('chemical_guidance_note', ''), lang)} "
                f"{localize_content('Follow label instructions, PPE, REI and PHI.', lang)}"
            )

else:
    st.subheader(get_label("describe_problem", lang))
    p = st.session_state.profile
    ca, cb = st.columns(2)
    with ca:
        crop_name = st.text_input(get_label("crop_name_label", lang), value=p.get("crop", ""))
        crop_stage = st.text_input(
            get_label("crop_stage_label", lang),
            value=p.get("crop_stage", ""),
            placeholder=get_label("crop_stage_placeholder", lang),
        )
    with cb:
        loc = st.text_input(
            get_label("location_label", lang),
            value=f"{p.get('state','')} {p.get('district','')}".strip(),
        )

    symptoms = st.text_area(
        get_label("describe_symptoms", lang),
        placeholder=get_label("symptoms_placeholder", lang),
        height=100,
    )

    if st.button(get_label("get_ipm_guidance", lang), key="pest_ask"):
        if not crop_name.strip():
            st.warning(get_label("crop_name_label", lang) + " " + get_label("enter_question", lang))
        elif not symptoms.strip():
            st.warning(get_label("describe_symptoms", lang) + " " + get_label("enter_question", lang))
        else:
            query = (f"Crop: {crop_name}. Location: {loc}. "
                     f"Crop stage: {crop_stage}. Symptoms: {symptoms}. "
                     f"What pest or disease and IPM management?")
            with st.spinner(get_label("loading", lang)):
                result = ask(question=query, lang_code=lang, profile=p)
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
with st.expander(safety_label("general_ipm", lang)):
    for p in pest_data.get("general_ipm_principles", []):
        st.markdown(f"- {localize_content(p, lang)}")

st.markdown("---")
st.error(get_label("ppe_reminder", lang))
