"""
pages/1_Farmer_Profile.py
Farmer profile setup — language, state, district, soil, irrigation, crop, land size.

Key improvements:
- District dropdown is fully dependent on selected state (cascades correctly).
- Profile is stored in st.session_state.profile and NEVER reset when language changes.
- All labels, placeholders, buttons, messages use get_label() from language_service.
- Detailed demo data badge shown for Tamil Nadu, Andhra Pradesh and Maharashtra.
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.config import APP_TITLE, DATA_DIR
from src.language_service import get_label
from src.shared_utils import APP_LOGO_DATA_URI, inject_css, init_session_state, render_sidebar

st.set_page_config(
    page_title=f"{get_label('farmer_profile', 'en')} — {APP_TITLE}",
    page_icon=APP_LOGO_DATA_URI,
    layout="wide",
)

init_session_state()
inject_css()
lang = render_sidebar("profile")  # also handles language switch + profile preservation
if not st.session_state.get("onboarding_started", False):
    st.switch_page("app.py")

# ── Static data (English keys; displayed values are English for data integrity) ──

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]

# Demo districts (detailed data available for these three states)
DEMO_DISTRICTS: dict[str, list[str]] = {
    "Tamil Nadu": [
        "Coimbatore", "Salem", "Thanjavur", "Tiruchirapalli", "Madurai",
        "Dindigul", "Vellore", "Erode", "Tirunelveli", "Namakkal",
        "Kancheepuram", "Tiruvannamalai", "Cuddalore", "Villupuram",
        "Nagapattinam", "Thiruvarur", "Perambalur", "Ariyalur",
    ],
    "Andhra Pradesh": [
        "Guntur", "Krishna", "Kurnool", "Nellore", "Visakhapatnam",
        "East Godavari", "West Godavari", "Chittoor", "Kadapa", "Anantapur",
        "Srikakulam", "Vizianagaram", "Prakasam", "Spsr Nellore",
    ],
    "Maharashtra": [
        "Pune", "Nashik", "Aurangabad", "Nagpur", "Kolhapur",
        "Satara", "Ahmednagar", "Solapur", "Latur", "Sangli",
        "Amravati", "Yavatmal", "Wardha", "Buldhana", "Nanded",
        "Osmanabad", "Jalgaon", "Dhule", "Nandurbar",
    ],
}

DEMO_STATES = set(DEMO_DISTRICTS.keys())

SOIL_TYPES = [
    "Alluvial", "Black Cotton (Vertisol)", "Red Laterite",
    "Sandy Loam", "Loamy", "Clay", "Clay Loam", "Sandy", "Silty Loam",
]

IRRIGATION_OPTIONS = [
    "Irrigated (canal)", "Irrigated (borewell/tubewell)",
    "Irrigated (tank/pond)", "Drip irrigation", "Sprinkler irrigation",
    "Rainfed only", "Partial irrigation",
]

CROPS_LIST = [
    "Rice (Paddy)", "Wheat", "Maize", "Ragi (Finger Millet)", "Bajra (Pearl Millet)",
    "Jowar (Sorghum)", "Chickpea (Gram)", "Pigeon Pea (Tur)", "Green Gram (Moong)",
    "Black Gram (Urad)", "Groundnut", "Soybean", "Mustard",
    "Cotton", "Sugarcane",
    "Chilli", "Turmeric", "Ginger",
    "Tomato", "Onion", "Potato",
    "Coconut", "Banana", "Tea", "Apple",
]

CROP_STAGES = [
    "Land preparation", "Seed selection / Nursery", "Sowing / Transplanting",
    "Germination / Early growth", "Tillering / Vegetative growth",
    "Flowering / Reproductive", "Grain filling / Pod development",
    "Maturity / Pre-harvest", "Harvest", "Post-harvest / Storage",
]

# Dropdown values stay in English internally so saved profiles and existing
# crop/data lookups remain stable. Streamlit's format_func only localizes what
# the farmer sees in the menu.
OPTION_TRANSLATIONS = {
    "ta": {
        "Irrigated (canal)": "கால்வாய் பாசனம்",
        "Irrigated (borewell/tubewell)": "ஆழ்துளைக் கிணறு / குழாய் கிணறு பாசனம்",
        "Irrigated (tank/pond)": "ஏரி / குளம் பாசனம்",
        "Drip irrigation": "சொட்டுநீர் பாசனம்",
        "Sprinkler irrigation": "தெளிப்பான் பாசனம்",
        "Rainfed only": "மழையை மட்டுமே நம்பிய விவசாயம்",
        "Partial irrigation": "பகுதி பாசனம்",
        "Alluvial": "வண்டல் மண்",
        "Black Cotton (Vertisol)": "கரிசல் மண் (வெர்டிசால்)",
        "Red Laterite": "செம்மண் / செம்புறை மண்",
        "Sandy Loam": "மணற்பாங்கான வண்டல் மண்",
        "Loamy": "வண்டல் கலந்த மண்",
        "Clay": "களிமண்",
        "Clay Loam": "களிமண் கலந்த வண்டல் மண்",
        "Sandy": "மணற்பாங்கான மண்",
        "Silty Loam": "வண்டல் நுண்மண்",
        "Land preparation": "நிலம் தயாரித்தல்",
        "Seed selection / Nursery": "விதைத் தேர்வு / நாற்றங்கால்",
        "Sowing / Transplanting": "விதைத்தல் / நாற்று நடுதல்",
        "Germination / Early growth": "முளைத்தல் / தொடக்க வளர்ச்சி",
        "Tillering / Vegetative growth": "தூர் பிடித்தல் / தாவர வளர்ச்சி",
        "Flowering / Reproductive": "பூத்தல் / இனப்பெருக்க நிலை",
        "Grain filling / Pod development": "மணி நிரம்புதல் / காய் வளர்ச்சி",
        "Maturity / Pre-harvest": "முதிர்ச்சி / அறுவடைக்கு முன்",
        "Harvest": "அறுவடை",
        "Post-harvest / Storage": "அறுவடைக்குப் பின் / சேமிப்பு",
    },
    "te": {
        "Irrigated (canal)": "కాలువ నీటిపారుదల",
        "Irrigated (borewell/tubewell)": "బోర్‌వెల్ / ట్యూబ్‌వెల్ నీటిపారుదల",
        "Irrigated (tank/pond)": "చెరువు / కుంట నీటిపారుదల",
        "Drip irrigation": "బిందు సేద్యం",
        "Sprinkler irrigation": "తుంపర సేద్యం",
        "Rainfed only": "వర్షాధారం మాత్రమే",
        "Partial irrigation": "పాక్షిక నీటిపారుదల",
        "Alluvial": "ఒండ్రు మట్టి",
        "Black Cotton (Vertisol)": "నల్ల రేగడి మట్టి (వెర్టిసోల్)",
        "Red Laterite": "ఎర్ర లేటరైట్ మట్టి",
        "Sandy Loam": "ఇసుకతో కూడిన లోమీ మట్టి",
        "Loamy": "లోమీ మట్టి",
        "Clay": "బంకమట్టి",
        "Clay Loam": "బంకమిశ్రమ లోమీ మట్టి",
        "Sandy": "ఇసుక మట్టి",
        "Silty Loam": "సిల్ట్ లోమీ మట్టి",
        "Land preparation": "భూమి తయారీ",
        "Seed selection / Nursery": "విత్తన ఎంపిక / నర్సరీ",
        "Sowing / Transplanting": "విత్తడం / నాటడం",
        "Germination / Early growth": "మొలకెత్తడం / ప్రారంభ పెరుగుదల",
        "Tillering / Vegetative growth": "పిలకలు రావడం / వృద్ధి దశ",
        "Flowering / Reproductive": "పూత / పునరుత్పత్తి దశ",
        "Grain filling / Pod development": "గింజ నిండటం / కాయల అభివృద్ధి",
        "Maturity / Pre-harvest": "పక్వ దశ / కోతకు ముందు",
        "Harvest": "కోత",
        "Post-harvest / Storage": "కోత అనంతరం / నిల్వ",
    },
    "hi": {
        "Irrigated (canal)": "नहर से सिंचाई",
        "Irrigated (borewell/tubewell)": "बोरवेल / ट्यूबवेल से सिंचाई",
        "Irrigated (tank/pond)": "तालाब से सिंचाई",
        "Drip irrigation": "टपक सिंचाई",
        "Sprinkler irrigation": "फव्वारा सिंचाई",
        "Rainfed only": "केवल वर्षा आधारित",
        "Partial irrigation": "आंशिक सिंचाई",
        "Alluvial": "जलोढ़ मिट्टी",
        "Black Cotton (Vertisol)": "काली कपासी मिट्टी (वर्टिसोल)",
        "Red Laterite": "लाल लैटेराइट मिट्टी",
        "Sandy Loam": "बलुई दोमट मिट्टी",
        "Loamy": "दोमट मिट्टी",
        "Clay": "चिकनी मिट्टी",
        "Clay Loam": "चिकनी दोमट मिट्टी",
        "Sandy": "रेतीली मिट्टी",
        "Silty Loam": "गाद वाली दोमट मिट्टी",
        "Land preparation": "खेत की तैयारी",
        "Seed selection / Nursery": "बीज चयन / पौधशाला",
        "Sowing / Transplanting": "बुवाई / रोपाई",
        "Germination / Early growth": "अंकुरण / शुरुआती वृद्धि",
        "Tillering / Vegetative growth": "कल्ले निकलना / वनस्पतिक वृद्धि",
        "Flowering / Reproductive": "फूल आना / प्रजनन अवस्था",
        "Grain filling / Pod development": "दाना भरना / फलियों का विकास",
        "Maturity / Pre-harvest": "पकना / कटाई से पहले",
        "Harvest": "कटाई",
        "Post-harvest / Storage": "कटाई के बाद / भंडारण",
    },
}

CROP_OPTION_IDS = {
    "Rice (Paddy)": "rice", "Wheat": "wheat", "Maize": "maize",
    "Ragi (Finger Millet)": "ragi", "Bajra (Pearl Millet)": "bajra",
    "Jowar (Sorghum)": "jowar", "Chickpea (Gram)": "chickpea",
    "Pigeon Pea (Tur)": "pigeon_pea", "Green Gram (Moong)": "green_gram",
    "Black Gram (Urad)": "black_gram", "Groundnut": "groundnut",
    "Soybean": "soybean", "Mustard": "mustard", "Cotton": "cotton",
    "Sugarcane": "sugarcane", "Chilli": "chilli", "Turmeric": "turmeric",
    "Ginger": "ginger", "Tomato": "tomato", "Onion": "onion",
    "Potato": "potato", "Coconut": "coconut", "Banana": "banana",
    "Tea": "tea", "Apple": "apple",
}

try:
    with (DATA_DIR / "crops.json").open(encoding="utf-8") as _crop_file:
        _crop_names = {
            crop.get("id"): crop.get("name", {})
            for crop in json.load(_crop_file)
            if isinstance(crop, dict)
        }
except (OSError, ValueError, TypeError):
    _crop_names = {}


def _localized_option(value: str) -> str:
    """Format an option for display without changing its canonical value."""
    if not isinstance(value, str):
        return value
    translation = OPTION_TRANSLATIONS.get(lang, {}).get(value)
    if translation:
        return translation
    crop_id = CROP_OPTION_IDS.get(value)
    if crop_id:
        localized_name = _crop_names.get(crop_id, {}).get(lang)
        if localized_name:
            return localized_name
    return value

CROP_ID_MAP = {
    "rice_paddy": "rice",
    "bajra_pearl_millet": "bajra",
    "ragi_finger_millet": "ragi",
    "jowar_sorghum": "jowar",
    "chickpea_gram": "chickpea",
    "pigeon_pea_tur": "pigeon_pea",
    "green_gram_moong": "green_gram",
    "black_gram_urad": "black_gram",
    "maize": "maize",
}

# ── Page header ───────────────────────────────────────────────────────────────

LOCATION_COPY = {
    "en": ("Where is your farm located?", "Choose your state and district. Add a village or locality if you wish."),
    "ta": ("உங்கள் பண்ணை எங்கு உள்ளது?", "மாநிலம் மற்றும் மாவட்டத்தைத் தேர்ந்தெடுக்கவும். விருப்பமெனில் கிராமம் அல்லது பகுதியைச் சேர்க்கவும்."),
    "te": ("మీ పొలం ఎక్కడ ఉంది?", "రాష్ట్రం మరియు జిల్లాను ఎంచుకోండి. కావాలంటే గ్రామం లేదా ప్రాంతాన్ని నమోదు చేయండి."),
    "hi": ("आपका खेत कहाँ स्थित है?", "राज्य और जिला चुनें। चाहें तो गाँव या क्षेत्र जोड़ें।"),
}
location_title, location_intro = LOCATION_COPY.get(lang, LOCATION_COPY["en"])
st.markdown(
    f"""
      <svg class="sf-location-art" viewBox="0 0 1200 310" width="1200" height="310" preserveAspectRatio="xMidYMid slice" aria-label="Farm landscape" style="display:block;width:100%;height:200px;border:1px solid #3A3A3A;border-radius:20px;margin:.35rem 0 1rem;">
        <defs>
          <linearGradient id="sf-sky" x2="0" y2="1"><stop stop-color="#1e2420"/><stop offset="1" stop-color="#252f28"/></linearGradient>
          <linearGradient id="sf-field" x2="0" y2="1"><stop stop-color="#3a5e40"/><stop offset="1" stop-color="#2a4530"/></linearGradient>
          <linearGradient id="sf-soften"><stop stop-color="#242424" stop-opacity=".97"/><stop offset=".5" stop-color="#242424" stop-opacity=".8"/><stop offset="1" stop-color="#242424" stop-opacity="0"/></linearGradient>
        </defs>
        <rect width="1200" height="310" fill="url(#sf-sky)"/>
        <circle cx="1010" cy="72" r="37" fill="#4a5e38" opacity=".5"/>
        <path d="M0 169 137 128 230 154 340 106 454 150 580 98 712 151 842 108 956 145 1080 96 1200 129V310H0Z" fill="#2a3d2e"/>
        <path d="M0 191 130 153 260 180 390 135 530 184 670 137 820 181 960 139 1080 168 1200 143V310H0Z" fill="#304838"/>
        <path d="M0 209Q260 173 520 204T1200 187V310H0Z" fill="url(#sf-field)"/>
        <path d="M635 310Q780 222 1200 194M770 310Q900 235 1200 216M920 310Q1030 251 1200 237" fill="none" stroke="#4a7850" stroke-width="6" opacity=".5"/>
        <g fill="#3a6845"><path d="M890 177v-50h9v50z"/><circle cx="895" cy="121" r="28"/><circle cx="874" cy="137" r="20"/><circle cx="916" cy="139" r="21"/><path d="M1112 180v-65h11v65z"/><circle cx="1117" cy="105" r="35"/><circle cx="1091" cy="126" r="24"/><circle cx="1144" cy="129" r="26"/></g>
        <g transform="translate(986 135)"><path d="M0 25 51 0l53 25v46H0z" fill="#2B2B2B"/><path d="m-6 27 57-33 60 33-6 10-54-29L0 37z" fill="#5a3d28"/><rect x="43" y="43" width="21" height="28" rx="2" fill="#4a7858"/><rect x="11" y="39" width="19" height="18" rx="2" fill="#384858"/><rect x="74" y="39" width="18" height="18" rx="2" fill="#384858"/></g>
        <rect width="1200" height="310" fill="url(#sf-soften)"/>
      </svg>
    """,
    unsafe_allow_html=True,
)
st.title(f"📍 {location_title}")
st.markdown(location_intro)

# ── Load current saved profile values for pre-population ──────────────────────
p = st.session_state.profile

# ── Determine district list BEFORE form renders ───────────────────────────────
# We keep a separate session key for the currently selected state so the
# district dropdown can re-populate without requiring form submission.
if "profile_state_selection" not in st.session_state:
    st.session_state.profile_state_selection = p.get("state", "")


def _districts_for(state: str) -> list[str]:
    """Return district list for the given state. Always adds 'Other district'."""
    if state in DEMO_DISTRICTS:
        return DEMO_DISTRICTS[state] + [get_label("other_district", lang)]
    return [get_label("other_district", lang)]


def _reset_location_drafts() -> None:
    """Clear dependent location inputs when the selected state changes."""
    state = st.session_state.get("state_dropdown", "")
    st.session_state.selected_state = state
    st.session_state.selected_district = ""
    st.session_state.selected_village = ""
    st.session_state.profile_state_selection = state
    for key in list(st.session_state.keys()):
        if key.startswith(("district_dropdown_", "district_name_input_", "locality_input_")):
            st.session_state.pop(key, None)
    # The new state's widget key has not been created yet, so seed it blank to
    # prevent a village from the previously selected state appearing here.
    st.session_state[f"locality_input_{state}"] = ""


# ── Location section (outside form — state changes update district list live) ─

with st.container(key="location-panel", border=True):
    st.subheader(get_label("location_section", lang))
    # Build state list with placeholder first
    placeholder_state = get_label("select_placeholder", lang)
    state_options = [placeholder_state] + STATES
    saved_state = p.get("state", "")
    state_idx = state_options.index(saved_state) if saved_state in state_options else 0

    selected_state = st.selectbox(
        get_label("select_state", lang),
        options=state_options,
        index=state_idx,
        key="state_dropdown",
        on_change=_reset_location_drafts,
    )
    # Update the live state tracker so district list refreshes immediately
    st.session_state.profile_state_selection = selected_state

    district_options = _districts_for(selected_state)
    placeholder_district = get_label("select_placeholder", lang)
    # Only prepend placeholder if there are real districts to choose from
    if selected_state in DEMO_DISTRICTS:
        district_display_options = [placeholder_district] + district_options[:-1] + [get_label("other_district", lang)]
    else:
        district_display_options = [get_label("other_district", lang)]

    saved_district = p.get("district", "")
    dist_idx = district_display_options.index(saved_district) if saved_district in district_display_options else 0

    selected_district = st.selectbox(
        get_label("select_district", lang),
        options=district_display_options,
        index=dist_idx,
        key=f"district_dropdown_{selected_state}",
    )

    other_district_val = get_label("other_district", lang)
    district_needs_text = selected_state not in DEMO_DISTRICTS or selected_district == other_district_val
    if district_needs_text:
        district_text = st.text_input(
            "District name" if lang == "en" else {"ta": "மாவட்டத்தின் பெயர்", "te": "జిల్లా పేరు", "hi": "जिले का नाम"}.get(lang, "District name"),
            value=p.get("district", "") if p.get("state") == selected_state else "",
            placeholder="Enter your district" if lang == "en" else {"ta": "உங்கள் மாவட்டத்தை உள்ளிடவும்", "te": "మీ జిల్లాను నమోదు చేయండి", "hi": "अपना जिला दर्ज करें"}.get(lang, "Enter your district"),
            key=f"district_name_input_{selected_state}",
        )
    else:
        district_text = ""

    locality_input = st.text_input(
        "Village or locality (optional)" if lang == "en" else {"ta": "கிராமம் அல்லது பகுதி (விருப்பம்)", "te": "గ్రామం లేదా ప్రాంతం (ఐచ్ఛికం)", "hi": "गाँव या क्षेत्र (वैकल्पिक)"}.get(lang, "Village or locality (optional)"),
        value=p.get("locality", "") if p.get("state") == selected_state else "",
        key=f"locality_input_{selected_state}",
    )

    st.session_state.selected_state = selected_state
    st.session_state.selected_district = (
        district_text.strip() if district_needs_text else selected_district
    )
    st.session_state.selected_village = locality_input.strip()

    # State data availability notice
    if selected_state not in (placeholder_state, "") and selected_state not in DEMO_STATES:
        st.info(get_label("limited_data_notice", lang))
    elif selected_state in DEMO_STATES:
        st.success(
            f"{get_label('demo_data_available', lang)}: "
            f"{', '.join(DEMO_DISTRICTS[selected_state][:5])}..."
        )

    st.markdown("---")

# ── Crop and field sections (in a form so they submit together) ───────────────

with st.container(key="crop-panel", border=True):
    st.subheader(get_label("crop_section", lang))
    col3, col4 = st.columns(2)

    with col3:
        crop_placeholder = get_label("select_placeholder", lang)
        crop_options = [crop_placeholder] + CROPS_LIST
        saved_crop = p.get("crop", "")
        crop_idx = crop_options.index(saved_crop) if saved_crop in crop_options else 0
        selected_crop = st.selectbox(
            get_label("current_planned_crop", lang),
            options=crop_options,
            index=crop_idx,
            key="crop_dropdown",
            format_func=_localized_option,
        )

    with col4:
        stage_placeholder = get_label("select_placeholder", lang)
        stage_options = [stage_placeholder] + CROP_STAGES
        saved_stage = p.get("crop_stage", "")
        stage_idx = stage_options.index(saved_stage) if saved_stage in stage_options else 0
        selected_stage = st.selectbox(
            get_label("current_crop_stage", lang),
            options=stage_options,
            index=stage_idx,
            key="stage_dropdown",
            format_func=_localized_option,
        )

with st.container(key="field-panel", border=True):
    st.subheader(get_label("field_section", lang))
    col5, col6 = st.columns(2)

    with col5:
        soil_placeholder = get_label("select_placeholder", lang)
        soil_options = [soil_placeholder] + SOIL_TYPES
        saved_soil = p.get("soil_type", "")
        soil_idx = soil_options.index(saved_soil) if saved_soil in soil_options else 0
        selected_soil = st.selectbox(
            get_label("soil_type", lang),
            options=soil_options,
            index=soil_idx,
            key="soil_dropdown",
            format_func=_localized_option,
        )

    with col6:
        irr_placeholder = get_label("select_placeholder", lang)
        irr_options = [irr_placeholder] + IRRIGATION_OPTIONS
        saved_irr = p.get("irrigation", "")
        irr_idx = irr_options.index(saved_irr) if saved_irr in irr_options else 0
        selected_irrigation = st.selectbox(
            get_label("irrigation", lang),
            options=irr_options,
            index=irr_idx,
            key="irrigation_dropdown",
            format_func=_localized_option,
        )

    land_size_input = st.text_input(
        get_label("land_size", lang),
        value=p.get("land_size", ""),
        placeholder=get_label("land_size_placeholder", lang),
        key="land_size_input",
    )

st.markdown("")  # spacer

# ── Save button ───────────────────────────────────────────────────────────────
continue_to_dashboard = {
    "en": "Continue to dashboard", "ta": "டாஷ்போர்டுக்குத் தொடரவும்",
    "te": "డాష్‌బోర్డ్‌కు కొనసాగించండి", "hi": "डैशबोर्ड पर जाएँ",
}.get(lang, "Continue to dashboard")
save_label = continue_to_dashboard if not p.get("state") else get_label("save_profile", lang)
with st.container(key="save-profile"):
    save_clicked = st.button(save_label, use_container_width=True, type="primary")

if save_clicked:
    placeholder_val = get_label("select_placeholder", lang)
    if selected_state == placeholder_val or selected_state == "":
        st.error(get_label("please_select_state", lang))
    elif not (district_text.strip() if district_needs_text else selected_district != placeholder_val):
        st.error("Please select or enter your district." if lang == "en" else {"ta": "உங்கள் மாவட்டத்தைத் தேர்ந்தெடுக்கவும் அல்லது உள்ளிடவும்.", "te": "మీ జిల్లాను ఎంచుకోండి లేదా నమోదు చేయండి.", "hi": "कृपया अपना जिला चुनें या दर्ज करें।"}.get(lang, "Please select or enter your district."))
    else:
        # Compute clean crop_id
        crop_val = selected_crop if selected_crop != placeholder_val else ""
        if crop_val:
            raw_id = (
                crop_val.lower()
                .replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
                .strip("_")
                .replace("__", "_")
            )
            crop_id = CROP_ID_MAP.get(raw_id, raw_id)
        else:
            crop_id = ""

        other_district_val = get_label("other_district", lang)
        st.session_state.farmer_profile = {
            "state": selected_state,
            "district": (district_text.strip() if district_needs_text else selected_district if selected_district != placeholder_val else ""),
            "locality": locality_input.strip(),
            "crop": crop_val,
            "crop_id": crop_id,
            "crop_stage": (
                selected_stage if selected_stage != placeholder_val else ""
            ),
            "soil_type": (
                selected_soil if selected_soil != placeholder_val else ""
            ),
            "irrigation": (
                selected_irrigation if selected_irrigation != placeholder_val else ""
            ),
            "land_size": land_size_input.strip(),
            "language": st.session_state.language,
            "lang_code": st.session_state.lang_code,
        }
        st.session_state.profile = st.session_state.farmer_profile
        st.session_state.selected_state = selected_state
        st.session_state.selected_district = st.session_state.farmer_profile["district"]
        st.session_state.selected_village = locality_input.strip()
        st.session_state.onboarding_completed = True
        st.session_state.onboarding_started = True
        st.session_state.onboarding_language_selected = True
        st.success(get_label("profile_saved", lang))
        st.switch_page("app.py")

# ── Display saved profile ─────────────────────────────────────────────────────
saved = st.session_state.profile
if saved.get("state"):
    st.markdown("---")
    st.subheader(get_label("your_current_profile", lang))

    not_spec = get_label("not_specified", lang)
    fields = [
        (get_label("field_language", lang),   saved.get("language", "—")),
        (get_label("field_state", lang),       saved.get("state", "—")),
        (get_label("field_district", lang),    saved.get("district") or not_spec),
        (get_label("field_crop", lang),        saved.get("crop") or not_spec),
        (get_label("field_crop_stage", lang),  saved.get("crop_stage") or "—"),
        (get_label("field_soil_type", lang),   saved.get("soil_type") or not_spec),
        (get_label("field_irrigation", lang),  saved.get("irrigation") or not_spec),
        (get_label("field_land_size", lang),   saved.get("land_size") or not_spec),
    ]
    cols = st.columns(4)
    for i, (label, value) in enumerate(fields):
        cols[i % 4].metric(label, value)

    if saved.get("state") and saved["state"] not in DEMO_STATES:
        st.info(get_label("limited_data_notice", lang))
