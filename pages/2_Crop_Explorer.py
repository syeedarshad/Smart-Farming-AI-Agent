"""Location-personalised crop explorer using only records in the local datasets."""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.config import APP_TITLE, DATA_DIR
from src.language_service import get_crop_description, get_label, localize_crop_term
from src.shared_utils import inject_css, init_session_state, render_sidebar

st.set_page_config(page_title=f"{get_label('crop_explorer','en')} — {APP_TITLE}", page_icon="🌱", layout="wide")
init_session_state()
inject_css()
lang = render_sidebar("crop_explorer")
WORDS = {
    "en": {"location":"Choose your farm location to see crops supported for your state.", "setup":"Set up farm location", "limited":"Detailed district-level crop information is unavailable for this location. Showing only crops supported by the general state knowledge base.", "no_data":"No crop records in the knowledge base match this state. No crop list has been generated.", "count":"supported crops", "season":"Season", "water":"Water need", "soil":"Suitable soil", "soil_na":"Not specified", "region":"Region", "indicative":"Indicative state-level information", "details":"Crop details", "yield":"Typical yield", "view":"View roadmap", "footer":"Indicative information from the local crop dataset. Consult your local KVK or agriculture department for district and field-specific recommendations."},
    "ta": {"location":"உங்கள் மாநிலத்திற்கான பயிர்களைப் பார்க்க பண்ணை இருப்பிடத்தைத் தேர்ந்தெடுக்கவும்.", "setup":"பண்ணை இருப்பிடத்தை அமைக்கவும்", "limited":"இந்த இடத்திற்கான மாவட்ட அளவிலான விரிவான தகவல் இல்லை. மாநில பொது அறிவுத் தளத்தால் ஆதரிக்கப்படும் பயிர்கள் மட்டுமே காட்டப்படுகின்றன.", "no_data":"இந்த மாநிலத்திற்கான பயிர் பதிவுகள் அறிவுத் தளத்தில் இல்லை. பட்டியல் உருவாக்கப்படவில்லை.", "count":"ஆதரிக்கப்படும் பயிர்கள்", "season":"பருவம்", "water":"நீர் தேவை", "soil":"பொருத்தமான மண்", "soil_na":"குறிப்பிடப்படவில்லை", "region":"பகுதி", "indicative":"மாநில அளவிலான வழிகாட்டுத் தகவல்", "details":"பயிர் விவரங்கள்", "yield":"வழக்கமான மகசூல்", "view":"வழிகாட்டியைப் பார்க்கவும்", "footer":"உள்ளூர் KVK அல்லது வேளாண் துறையுடன் மாவட்ட மற்றும் வயல் சார்ந்த பரிந்துரைகளை உறுதிப்படுத்தவும்."},
    "te": {"location":"మీ రాష్ట్రానికి మద్దతు ఉన్న పంటలను చూడటానికి వ్యవసాయ స్థలాన్ని ఎంచుకోండి.", "setup":"వ్యవసాయ స్థలాన్ని సెటప్ చేయండి", "limited":"ఈ ప్రాంతానికి జిల్లా స్థాయి వివరాలు అందుబాటులో లేవు. రాష్ట్ర సాధారణ జ్ఞాన భాండాగారం మద్దతు ఉన్న పంటలే చూపబడుతున్నాయి.", "no_data":"ఈ రాష్ట్రానికి పంట రికార్డులు లేవు. జాబితా రూపొందించలేదు.", "count":"మద్దతు ఉన్న పంటలు", "season":"సీజన్", "water":"నీటి అవసరం", "soil":"అనుకూల నేల", "soil_na":"పేర్కొనలేదు", "region":"ప్రాంతం", "indicative":"రాష్ట్ర స్థాయి సూచనాత్మక సమాచారం", "details":"పంట వివరాలు", "yield":"సాధారణ దిగుబడి", "view":"మార్గదర్శిని చూడండి", "footer":"జిల్లా మరియు పొలం ప్రత్యేక సూచనల కోసం స్థానిక KVK లేదా వ్యవసాయ శాఖతో నిర్ధారించండి."},
    "hi": {"location":"अपने राज्य में समर्थित फसलें देखने के लिए खेत का स्थान चुनें।", "setup":"खेत का स्थान सेट करें", "limited":"इस स्थान के लिए जिला स्तर की विस्तृत जानकारी उपलब्ध नहीं है। केवल सामान्य राज्य ज्ञान आधार की समर्थित फसलें दिखाई गई हैं।", "no_data":"इस राज्य के लिए ज्ञान आधार में फसल रिकॉर्ड नहीं हैं। सूची नहीं बनाई गई है।", "count":"समर्थित फसलें", "season":"मौसम", "water":"पानी की जरूरत", "soil":"उपयुक्त मिट्टी", "soil_na":"निर्दिष्ट नहीं", "region":"क्षेत्र", "indicative":"राज्य स्तर की सांकेतिक जानकारी", "details":"फसल विवरण", "yield":"सामान्य उपज", "view":"मार्गदर्शिका देखें", "footer":"जिला और खेत संबंधी सलाह के लिए स्थानीय KVK या कृषि विभाग से पुष्टि करें।"},
}
W = WORDS.get(lang, WORDS["en"])
W.update({
    "district_supported": {
        "en": "This district is listed in the detailed state dataset. Crop suitability remains indicative; confirm field-level decisions with your local KVK.",
        "ta": "இந்த மாவட்டம் மாநிலத்தின் விரிவான தரவுத் தொகுப்பில் உள்ளது. பயிர் பொருத்தம் வழிகாட்டுதலுக்கானது மட்டுமே; வயல் சார்ந்த முடிவுகளை உள்ளூர் KVK-யுடன் உறுதிப்படுத்தவும்.",
        "te": "ఈ జిల్లా రాష్ట్ర వివరమైన డేటాలో ఉంది. పంట అనుకూలత సూచనాత్మకమే; పొలానికి సంబంధించిన నిర్ణయాలను స్థానిక KVKతో నిర్ధారించండి.",
        "hi": "यह जिला राज्य के विस्तृत डेटा में सूचीबद्ध है। फसल उपयुक्तता सांकेतिक है; खेत-स्तर के निर्णय स्थानीय KVK से सत्यापित करें.",
    }[lang],
    "district_missing": {
        "en": "State-level crop information is available, but this district has no detailed crop records in the current dataset.",
        "ta": "மாநில அளவிலான பயிர் தகவல் உள்ளது; இந்த மாவட்டத்திற்கான விரிவான பதிவுகள் தற்போதைய தரவுத் தொகுப்பில் இல்லை.",
        "te": "రాష్ట్ర స్థాయి పంట సమాచారం ఉంది; ఈ జిల్లాకు సంబంధించిన వివరమైన రికార్డులు ప్రస్తుత డేటాలో లేవు.",
        "hi": "राज्य स्तर की फसल जानकारी उपलब्ध है, लेकिन वर्तमान डेटा में इस जिले के विस्तृत रिकॉर्ड नहीं हैं।",
    }[lang],
    "data_missing": {
        "en": "Crop data is unavailable. Please check the crop knowledge dataset.",
        "ta": "பயிர் தரவு கிடைக்கவில்லை. பயிர் அறிவுத் தரவுத் தொகுப்பைச் சரிபார்க்கவும்.",
        "te": "పంట సమాచారం అందుబాటులో లేదు. పంట జ్ఞాన డేటాను తనిఖీ చేయండి.",
        "hi": "फसल डेटा उपलब्ध नहीं है। कृपया फसल ज्ञान डेटा की जाँच करें।",
    }[lang],
})

@st.cache_data
def load_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

crops = load_json("crops.json")
state_map = load_json("state_crop_mapping.json")
profile = st.session_state.profile
state = profile.get("state")

def get_state_crops(state_name):
    info = state_map.get(state_name, {})
    # The general crop catalogue is filtered to state records first. For states
    # with a mapping, also require membership in its supported crop list.
    mapped = set(info.get("suitable_crops", []))
    aliases = {"tur": "pigeon_pea", "chickpea": "chickpea", "rice": "rice"}
    mapped = {aliases.get(item, item) for item in mapped}
    return [crop for crop in crops if state_name in crop.get("major_states", []) and (not mapped or crop.get("id") in mapped)], info

st.title(f"🌱 {get_label('crop_explorer', lang)}")
st.markdown(get_label("crop_explorer_intro", lang))
if not crops:
    st.error(W["data_missing"])
    st.stop()
if not state:
    st.info(W["location"])
    if st.button(W["setup"], type="primary"):
        st.switch_page("pages/1_Farmer_Profile.py")
    st.stop()

available, location_info = get_state_crops(state)
st.markdown(f"### 📍 {state}{' · ' + profile['district'] if profile.get('district') else ''}")
if state in ("Tamil Nadu", "Andhra Pradesh", "Maharashtra"):
    district = profile.get("district", "")
    if district and district in location_info.get("demo_districts", []):
        st.success(W["district_supported"])
    else:
        st.info(W["district_missing"])
else:
    st.info(W["limited"])

if not available:
    st.warning(W["no_data"])
    st.stop()

CATEGORIES = sorted({crop.get("category", "other") for crop in available})
category_labels = {localize_crop_term(category, lang): category for category in CATEGORIES}
season_labels = {localize_crop_term(season, lang): season for season in ("Kharif", "Rabi", "Zaid", "Perennial")}
water_labels = {localize_crop_term(water.replace("_", " ").title(), lang): water for water in ("low", "medium", "high", "very_high")}
col1, col2, col3 = st.columns(3)
with col1:
    cat_options = [get_label("all_categories", lang)] + list(category_labels)
    sel_cat = st.selectbox(get_label("filter_category", lang), cat_options)
with col2:
    season_options = [get_label("all_seasons", lang)] + list(season_labels)
    sel_season = st.selectbox(get_label("filter_season", lang), season_options)
with col3:
    water_options = [get_label("all_water_needs", lang)] + list(water_labels)
    sel_water = st.selectbox(get_label("filter_water", lang), water_options)

filtered = available
if sel_cat != get_label("all_categories", lang):
    filtered = [c for c in filtered if c.get("category") == category_labels.get(sel_cat)]
if sel_season != get_label("all_seasons", lang):
    filtered = [c for c in filtered if season_labels.get(sel_season) in c.get("seasons", [])]
if sel_water != get_label("all_water_needs", lang):
    filtered = [c for c in filtered if c.get("water_need") == water_labels.get(sel_water)]
st.markdown(f"**{len(filtered)} {W['count']}** · {state}")

CATEGORY_ICON = {"cereal":"🌾", "millet":"🌿", "pulse":"🫘", "oilseed":"🌻", "fibre":"🧵", "commercial":"🌱", "spice_vegetable":"🌶️", "spice":"🪴", "vegetable":"🥦", "fruit":"🍌", "plantation":"🌴"}
for start in range(0, len(filtered), 2):
    cols = st.columns(2)
    for col, crop in zip(cols, filtered[start:start + 2]):
        with col:
            with st.container(border=True):
                crop_names = crop.get("name", {})
                name = crop_names.get(lang) or crop_names.get("en", crop.get("id", "Crop"))
                st.markdown(f"### {CATEGORY_ICON.get(crop.get('category'), '🌱')} {name}")
                a, b = st.columns(2)
                a.markdown(f"**{W['season']}**")
                a.write(", ".join(localize_crop_term(item, lang) for item in crop.get("seasons", [])) or W["soil_na"])
                b.markdown(f"**{W['water']}**")
                b.write(localize_crop_term(crop.get("water_need", "Not specified").replace("_", " ").title(), lang))
                st.markdown(f"**{W['soil']}**")
                st.write(", ".join(localize_crop_term(item, lang) for item in crop.get("soil_types", [])) or W["soil_na"])
                st.caption(f"{W['region']}: {state} · {W['indicative']}")
                with st.expander(W["details"]):
                    st.write(get_crop_description(crop, lang))
                    st.caption(f"{W['yield']}: {crop.get('typical_yield_qtl_per_ha', '—')} qtl/ha · {crop.get('harvest_duration_days', '—')} days")
                if st.button(W["view"], key=f"crop_roadmap_{crop.get('id')}", type="primary"):
                    st.session_state.profile["crop_id"] = crop.get("id", "")
                    st.session_state.profile["crop"] = crop_names.get("en", name)
                    st.switch_page("pages/3_Crop_Roadmap.py")

st.caption(W["footer"])
