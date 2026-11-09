"""Smart Farming AI landing page and location-personalised dashboard."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from src.config import APP_TITLE, DATA_DIR, LLM_PROVIDER
from src.language_service import LANGUAGE_CODES, get_label, localize_crop_term
from src.shared_utils import inject_css, init_session_state, render_sidebar

st.set_page_config(page_title=APP_TITLE, page_icon="🌾", layout="wide", initial_sidebar_state="expanded")
init_session_state()
inject_css()
lang = render_sidebar("home")

WELCOME = {
    "en": ("Smarter Farming, Better Harvests.", "Welcome to Smart Farming AI. Your intelligent farming companion helps you make better agricultural decisions, understand your crops and protect your harvest.", "Choose your language", "Continue", "Your farming companion", "Plan crops, learn natural farming, manage pests, prepare for weather risks and explore market guidance.", "Where farming knowledge meets your field"),
    "ta": ("சிறந்த விவசாயம், சிறந்த அறுவடை.", "Smart Farming AI-க்கு உங்களை வரவேற்கிறோம். சிறந்த விவசாய முடிவுகளை எடுக்கவும், உங்கள் பயிர்களைப் புரிந்துகொள்ளவும், அறுவடையைப் பாதுகாக்கவும் உங்கள் அறிவார்ந்த விவசாயத் துணை உதவுகிறது.", "உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்", "தொடரவும்", "உங்கள் விவசாயத் துணை", "பயிர் திட்டமிடல், இயற்கை விவசாயம், பூச்சி மேலாண்மை, வானிலை பாதுகாப்பு மற்றும் சந்தை வழிகாட்டுதலைப் பெறுங்கள்.", "உங்கள் வயலுக்கான விவசாய அறிவு"),
    "te": ("తెలివైన వ్యవసాయం, మెరుగైన పంటలు.", "స్మార్ట్ ఫార్మింగ్ AIకి స్వాగతం. మెరుగైన వ్యవసాయ నిర్ణయాలు తీసుకోవడానికి, మీ పంటలను అర్థం చేసుకోవడానికి, దిగుబడిని కాపాడుకోవడానికి మీ తెలివైన వ్యవసాయ సహచరుడు సహాయపడుతుంది.", "మీ భాషను ఎంచుకోండి", "కొనసాగించండి", "మీ వ్యవసాయ సహచరుడు", "పంట ప్రణాళిక, సహజ వ్యవసాయం, పురుగు నిర్వహణ, వాతావరణ భద్రత మరియు మార్కెట్ మార్గదర్శకత పొందండి.", "మీ పొలానికి వ్యవసాయ జ్ఞానం"),
    "hi": ("बेहतर खेती, बेहतर फसल।", "स्मार्ट फार्मिंग AI में आपका स्वागत है। आपका बुद्धिमान कृषि साथी बेहतर निर्णय लेने, फसलों को समझने और उपज की रक्षा करने में मदद करता है।", "अपनी भाषा चुनें", "जारी रखें", "आपका कृषि साथी", "फसल योजना, प्राकृतिक खेती, कीट प्रबंधन, मौसम सुरक्षा और बाजार मार्गदर्शन प्राप्त करें।", "आपके खेत के लिए कृषि ज्ञान"),
}
FEATURES = {
    "en": [("🌾", "Crop planning", "Explore crops that match your region."), ("🌿", "Natural farming", "Build soil health with practical guidance."), ("🛡️", "Pest & weather safety", "Prepare for common farm risks."), ("🧺", "Market guidance", "Find useful harvest and market information.")],
    "ta": [("🌾", "பயிர் திட்டமிடல்", "உங்கள் பகுதிக்குப் பொருத்தமான பயிர்களை அறியுங்கள்."), ("🌿", "இயற்கை விவசாயம்", "நடைமுறை வழிகாட்டுதலுடன் மண் வளத்தை மேம்படுத்துங்கள்."), ("🛡️", "பூச்சி மற்றும் வானிலை பாதுகாப்பு", "பொதுவான பண்ணை அபாயங்களுக்குத் தயாராகுங்கள்."), ("🧺", "சந்தை வழிகாட்டுதல்", "அறுவடை மற்றும் சந்தைத் தகவல்களைப் பெறுங்கள்.")],
    "te": [("🌾", "పంట ప్రణాళిక", "మీ ప్రాంతానికి సరిపోయే పంటలను తెలుసుకోండి."), ("🌿", "సహజ వ్యవసాయం", "ఆచరణాత్మక సూచనలతో నేల ఆరోగ్యాన్ని మెరుగుపరచండి."), ("🛡️", "పురుగు మరియు వాతావరణ భద్రత", "సాధారణ వ్యవసాయ ప్రమాదాలకు సిద్ధంగా ఉండండి."), ("🧺", "మార్కెట్ మార్గదర్శకం", "దిగుబడి మరియు మార్కెట్ సమాచారం తెలుసుకోండి.")],
    "hi": [("🌾", "फसल योजना", "अपने क्षेत्र के अनुकूल फसलों को जानें।"), ("🌿", "प्राकृतिक खेती", "व्यावहारिक मार्गदर्शन से मिट्टी की सेहत सुधारें।"), ("🛡️", "कीट और मौसम सुरक्षा", "सामान्य कृषि जोखिमों के लिए तैयार रहें।"), ("🧺", "बाजार मार्गदर्शन", "फसल और बाजार की उपयोगी जानकारी पाएँ।")],
}
DASH = {
    "en": {"welcome":"Welcome, Farmer!", "location":"Farm location", "supported":"Supported crops", "discovery":"Common crops for your location", "tools":"Your farming tools", "open":"Open", "roadmap":"View crop roadmap", "district":"District not specified", "no_records":"No crop records for this state are available in the current knowledge base. We have not generated a crop list.", "limited":"Detailed district-level crop data is unavailable for this location. The crops below are supported by the general state knowledge base; please confirm local suitability with your KVK or agriculture office.", "detailed":"Seasonal crop patterns use state-level data. The dataset does not map crops to individual districts; confirm local suitability with your KVK or agriculture office.", "modules":[("🤖", "Farming assistant", "Ask a question about your farm.", "pages/4_AI_Farming_Assistant.py"),("🌿", "Natural farming", "Explore compost, mulching and soil health.", "pages/5_Natural_Farming.py"),("🛡️", "Weather & safety", "Review practical safety guidance.", "pages/7_Weather_and_Safety.py"),("🧺", "Market guidance", "Explore illustrative market information.", "pages/8_Market_Guidance.py")]},
    "ta": {"welcome":"விவசாயி அவர்களே, வரவேற்கிறோம்!", "location":"பண்ணை அமைவிடம்", "supported":"ஆதரிக்கப்படும் பயிர்கள்", "discovery":"உங்கள் பகுதியில் பொதுவாகப் பயிரிடப்படும் பயிர்கள்", "tools":"விவசாய கருவிகள்", "open":"திறக்கவும்", "roadmap":"பயிர் வழிகாட்டியைப் பார்க்கவும்", "district":"மாவட்டம் குறிப்பிடப்படவில்லை", "no_records":"இந்த மாநிலத்திற்கான பயிர் பதிவுகள் அறிவுத் தளத்தில் இல்லை. பயிர் பட்டியல் உருவாக்கப்படவில்லை.", "limited":"இந்த இடத்திற்கான மாவட்ட அளவிலான விரிவான தரவு இல்லை. கீழே உள்ள பயிர்கள் மாநில பொது அறிவுத் தளத்திலிருந்து வந்தவை; உள்ளூர் KVK அல்லது வேளாண் அலுவலகத்துடன் உறுதிப்படுத்தவும்.", "detailed":"பருவகால பயிர் முறைகள் மாநில அளவிலான தரவை அடிப்படையாகக் கொண்டவை. தனிப்பட்ட மாவட்டப் பயிர் பதிவுகள் இல்லை; உள்ளூர் KVK அல்லது வேளாண் அலுவலகத்தில் உறுதிப்படுத்தவும்.", "modules":[("🤖", "விவசாய உதவியாளர்", "உங்கள் பண்ணை குறித்து கேளுங்கள்.", "pages/4_AI_Farming_Assistant.py"),("🌿", "இயற்கை விவசாயம்", "உரம், மூடாக்கு மற்றும் மண் வளத்தை அறியுங்கள்.", "pages/5_Natural_Farming.py"),("🛡️", "வானிலை மற்றும் பாதுகாப்பு", "பாதுகாப்பு வழிகாட்டுதலைப் பாருங்கள்.", "pages/7_Weather_and_Safety.py"),("🧺", "சந்தை வழிகாட்டுதல்", "சந்தைத் தகவல்களைப் பாருங்கள்.", "pages/8_Market_Guidance.py")]},
    "te": {"welcome":"రైతుకు స్వాగతం!", "location":"వ్యవసాయ స్థలం", "supported":"మద్దతు ఉన్న పంటలు", "discovery":"మీ ప్రాంతంలో సాధారణంగా పండించే పంటలు", "tools":"వ్యవసాయ సాధనాలు", "open":"తెరవండి", "roadmap":"పంట మార్గదర్శిని చూడండి", "district":"జిల్లా పేర్కొనలేదు", "no_records":"ఈ రాష్ట్రానికి సంబంధించిన పంట రికార్డులు జ్ఞాన భాండాగారంలో లేవు. పంటల జాబితా రూపొందించలేదు.", "limited":"ఈ ప్రాంతానికి జిల్లా స్థాయి వివరమైన సమాచారం లేదు. దిగువ పంటలు రాష్ట్ర సాధారణ జ్ఞాన భాండాగారం నుంచి వచ్చాయి; స్థానిక KVK లేదా వ్యవసాయ కార్యాలయంలో నిర్ధారించండి.", "detailed":"సీజన్ వారీ పంట నమూనాలు రాష్ట్ర స్థాయి సమాచారంపై ఆధారపడతాయి. వ్యక్తిగత జిల్లాల పంట రికార్డులు లేవు; స్థానిక KVK లేదా వ్యవసాయ కార్యాలయంలో నిర్ధారించండి.", "modules":[("🤖", "వ్యవసాయ సహాయకుడు", "మీ పొలం గురించి అడగండి.", "pages/4_AI_Farming_Assistant.py"),("🌿", "సహజ వ్యవసాయం", "కంపోస్ట్, మల్చింగ్ మరియు నేల ఆరోగ్యం తెలుసుకోండి.", "pages/5_Natural_Farming.py"),("🛡️", "వాతావరణం మరియు భద్రత", "భద్రతా సూచనలు చూడండి.", "pages/7_Weather_and_Safety.py"),("🧺", "మార్కెట్ మార్గదర్శకం", "మార్కెట్ సమాచారాన్ని చూడండి.", "pages/8_Market_Guidance.py")]},
    "hi": {"welcome":"किसान का स्वागत है!", "location":"खेत का स्थान", "supported":"समर्थित फसलें", "discovery":"आपके क्षेत्र में आम तौर पर उगाई जाने वाली फसलें", "tools":"खेती के साधन", "open":"खोलें", "roadmap":"फसल मार्गदर्शिका देखें", "district":"जिला निर्दिष्ट नहीं", "no_records":"इस राज्य के लिए ज्ञान आधार में फसल रिकॉर्ड नहीं हैं। कोई फसल सूची नहीं बनाई गई है।", "limited":"इस स्थान के लिए जिला स्तर का विस्तृत डेटा उपलब्ध नहीं है। नीचे की फसलें सामान्य राज्य ज्ञान आधार से समर्थित हैं; स्थानीय KVK या कृषि कार्यालय से पुष्टि करें।", "detailed":"मौसमी फसल पैटर्न राज्य स्तर के डेटा पर आधारित हैं। अलग-अलग जिलों के फसल रिकॉर्ड उपलब्ध नहीं हैं; स्थानीय KVK या कृषि कार्यालय से पुष्टि करें.", "modules":[("🤖", "कृषि सहायक", "अपने खेत के बारे में पूछें।", "pages/4_AI_Farming_Assistant.py"),("🌿", "प्राकृतिक खेती", "खाद, मल्चिंग और मिट्टी की सेहत जानें।", "pages/5_Natural_Farming.py"),("🛡️", "मौसम और सुरक्षा", "सुरक्षा मार्गदर्शन देखें।", "pages/7_Weather_and_Safety.py"),("🧺", "बाजार मार्गदर्शन", "बाजार की उपयोगी जानकारी देखें।", "pages/8_Market_Guidance.py")]},
}
HOME_LABELS = {
    "en": {"language":"Language", "season":"Season", "water":"Water", "soil":"Soil", "season_na":"Season information unavailable", "soil_na":"See local advice", "set_location":"Set up your farm location"},
    "ta": {"language":"மொழி", "season":"பருவம்", "water":"நீர் தேவை", "soil":"மண்", "season_na":"பருவத் தகவல் இல்லை", "soil_na":"உள்ளூர் ஆலோசனையைப் பெறவும்", "set_location":"பண்ணை இருப்பிடத்தை அமைக்கவும்"},
    "te": {"language":"భాష", "season":"సీజన్", "water":"నీటి అవసరం", "soil":"నేల", "season_na":"సీజన్ సమాచారం లేదు", "soil_na":"స్థానిక సలహా పొందండి", "set_location":"వ్యవసాయ స్థలాన్ని సెటప్ చేయండి"},
    "hi": {"language":"भाषा", "season":"मौसम", "water":"पानी की जरूरत", "soil":"मिट्टी", "season_na":"मौसम की जानकारी उपलब्ध नहीं", "soil_na":"स्थानीय सलाह लें", "set_location":"अपने खेत का स्थान सेट करें"},
}

def crop_data_for(state):
    try:
        with open(DATA_DIR / "crops.json", encoding="utf-8") as f:
            crops = json.load(f)
        with open(DATA_DIR / "state_crop_mapping.json", encoding="utf-8") as f:
            mapping = json.load(f)
    except (OSError, json.JSONDecodeError):
        return [], {}
    state_info = mapping.get(state, {})
    # Use the location's seasonal crop records first. These lists are more
    # specific to local planting patterns than the broad catalogue's states.
    seasonal_ids = list(dict.fromkeys(
        state_info.get("kharif_crops", []) + state_info.get("rabi_crops", [])
    ))
    aliases = {"tur": "pigeon_pea"}
    common_ids = {aliases.get(crop_id, crop_id) for crop_id in seasonal_ids}
    matches = [c for c in crops if c.get("id") in common_ids]

    # Some locations have only a general suitability list, so use that before
    # falling back to the catalogue's broad major-state tags.
    if not matches:
        suitable = {aliases.get(crop_id, crop_id) for crop_id in state_info.get("suitable_crops", [])}
        matches = [
            c for c in crops
            if (c.get("id") in suitable if suitable else state in c.get("major_states", []))
        ]
    return matches, state_info

# The sidebar is the single language selector across every page.
profile = st.session_state.farmer_profile

# First visit: a short welcome screen, then location setup.
if not profile.get("state") and not st.session_state.onboarding_started:
    tagline, intro, _, continue_label, *_ = WELCOME.get(lang, WELCOME["en"])
    st.markdown(
        f"""<div class="sf-hero">
        <span class="sf-mark">🌾</span>
        <span class="sf-hero-title">{get_label("app_title", lang)}</span>
        <span class="sf-hero-tagline">{tagline}</span>
        <p class="sf-hero-intro">{intro}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button(continue_label, type="primary", use_container_width=True):
        st.session_state.onboarding_started = True
        st.session_state.onboarding_language_selected = True
        st.switch_page("pages/1_Farmer_Profile.py")
    st.stop()

# Returning to Home before saving a location resumes the profile setup.
D = DASH.get(lang, DASH["en"])
H = HOME_LABELS.get(lang, HOME_LABELS["en"])
if not profile.get("state"):
    st.switch_page("pages/1_Farmer_Profile.py")

st.markdown(f"# 🌾 {get_label('home', lang)}")
st.markdown(f"## {D['welcome']}")
st.markdown(f"{profile.get('district') or profile.get('locality') or ''} · {profile['state']}")
crops, state_info = crop_data_for(profile["state"])
metric1, metric2, metric3 = st.columns(3)
metric1.metric(H["language"], st.session_state.language)
metric2.metric(D["location"], f"{profile.get('district') or D['district']}, {profile['state']}")
metric3.metric(D["supported"], len(crops))

if profile["state"] in ("Tamil Nadu", "Andhra Pradesh", "Maharashtra"):
    st.success(D["detailed"])
else:
    st.info(D["limited"])

st.markdown(f"### 🌱 {D['discovery']}")
if crops:
    crop_aliases = {"tur": "pigeon_pea"}
    location_seasons = {}
    for season, key in (("Kharif", "kharif_crops"), ("Rabi", "rabi_crops")):
        for crop_id in state_info.get(key, []):
            normalized_id = crop_aliases.get(crop_id, crop_id)
            location_seasons.setdefault(normalized_id, []).append(season)

    location_label = (
        f"{profile['district']}, {profile['state']}"
        if profile.get("district") else profile["state"]
    )
    tiles = st.columns(3)
    for index, crop in enumerate(crops):
        name = crop.get("name", {}).get(lang) or crop.get("name", {}).get("en", crop.get("id", "Crop"))
        with tiles[index % 3]:
            with st.container(border=True):
                st.markdown(f"### 🌿 {name}")
                seasons = location_seasons.get(crop.get("id"), crop.get("seasons", []))
                season_text = ", ".join(localize_crop_term(item, lang) for item in seasons)
                water_text = localize_crop_term(crop.get('water_need', '—').replace('_', ' ').title(), lang)
                soil_text = ", ".join(localize_crop_term(item, lang) for item in crop.get('soil_types', [])[:3])
                st.caption(f"{season_text or H['season_na']} · {location_label}")
                st.write(f"{H['water']}: {water_text}  ·  {H['soil']}: {soil_text or H['soil_na']}")
                if st.button(D["roadmap"], key=f"roadmap_{crop.get('id')}"):
                    st.session_state.profile["crop_id"] = crop.get("id", "")
                    st.session_state.profile["crop"] = crop.get("name", {}).get("en", "")
                    st.switch_page("pages/3_Crop_Roadmap.py")
else:
    st.warning(D["no_records"])

st.markdown(f"### {D['tools']}")
modules = D["modules"]
cols = st.columns(4)
for col, (icon, title, description, page) in zip(cols, modules):
    with col:
        with st.container(border=True):
            st.markdown(f"### {icon} {title}")
            st.caption(description)
            st.page_link(page, label=D["open"], use_container_width=True)

if LLM_PROVIDER != "ibm_granite":
    st.caption(get_label("demo_mode_banner", lang))
