"""
pages/8_Market_Guidance.py
Approximate market price guidance module.
IMPORTANT: All prices shown are illustrative approximate ranges, NOT real-time mandi prices.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.config import APP_TITLE
from src.language_service import get_label
from src.shared_utils import inject_css, init_session_state, render_sidebar
from src.market_service import (
    get_all_commodities,
    format_price_table,
    get_disclaimer,
    get_external_links,
    localize_market_unit,
)

st.set_page_config(page_title=f"Market Guidance — {APP_TITLE}", page_icon="💰", layout="wide")

inject_css()
init_session_state()
lang = render_sidebar("market")

# ── Title ──────────────────────────────────────────────────────────────────────
st.title(f"💰 {get_label('market_guidance', lang)}")

# ── PROMINENT DISCLAIMER ───────────────────────────────────────────────────────
st.error(get_disclaimer(lang))
st.markdown("---")

# ── Live market links ──────────────────────────────────────────────────────────
st.subheader(get_label("live_price_check", lang))
st.markdown(
    {
        "en": "For **real-time** mandi prices, use these official government portals:",
        "ta": "**நேரடி** மண்டி விலைகளுக்கு, இந்த அதிகாரப்பூர்வ அரசு தளங்களை பயன்படுத்தவும்:",
        "te": "**నేరుగా** మండి ధరలకు, ఈ అధికారిక ప్రభుత్వ పోర்టల్‌లను వినియోగించండి:",
        "hi": "**वास्तविक समय** मंडी कीमतों के लिए, इन आधिकारिक सरकारी पोर्टलों का उपयोग करें:",
    }.get(lang, "For **real-time** mandi prices, use these official government portals:")
)
links = get_external_links(lang)
cols = st.columns(len(links))
for i, (name, url) in enumerate(links.items()):
    with cols[i]:
        st.link_button(f"🔗 {name}", url)

st.markdown("---")

# ── Illustrative price data ────────────────────────────────────────────────────
st.subheader(get_label("illustrative_prices", lang))
st.markdown(
    {
        "en": "The data below shows **approximate historical price ranges** for reference only. "
              "Prices are ₹ per quintal unless stated otherwise.",
        "ta": "கீழே உள்ள தரவு **தோராயமான வரலாற்று விலை வரம்புகளை** மட்டும் காட்டுகிறது. "
              "விலைகள் ₹/குவிண்டால் (தனியாக குறிப்பிடப்படாவிட்டால்).",
        "te": "దిగువ డేటా **సుమారు చారిత్రక ధర శ్రేణులను** మాత్రమే సూచనగా చూపుతుంది. "
              "ధరలు ₹/క్వింటాల్ (ప్రత్యేకంగా పేర్కొనకపోతే).",
        "hi": "नीचे दिया गया डेटा केवल संदर्भ के लिए **अनुमानित ऐतिहासिक मूल्य श्रेणियाँ** दिखाता है। "
              "कीमतें ₹ प्रति क्विंटल हैं (जब तक अन्यथा न बताया जाए)।",
    }.get(lang, "The data below shows **approximate historical price ranges** for reference only. "
                "Prices are ₹ per quintal unless stated otherwise.")
)

commodities = get_all_commodities()
if not commodities:
    st.error(
        {
            "en": "Market price data not available. Please check data/market_prices.json.",
            "ta": "சந்தை விலை தரவு கிடைக்கவில்லை. data/market_prices.json சரிபார்க்கவும்.",
            "te": "మార్కెట్ ధర డేటా అందుబాటులో లేదు. data/market_prices.json తనిఖీ చేయండి.",
            "hi": "बाजार मूल्य डेटा उपलब्ध नहीं है। data/market_prices.json जांचें।",
        }.get(lang, "Market price data not available.")
    )
    st.stop()

# ── Commodity selector ────────────────────────────────────────────────────────
commodity_map = {}
for c in commodities:
    name_lang = c.get("commodity_name", {}).get(lang) or c.get("commodity_name", {}).get("en", "")
    commodity_map[name_lang] = c

show_all_label = get_label("show_all", lang)
selected_commodity_name = st.selectbox(
    get_label("select_commodity", lang),
    [show_all_label] + list(commodity_map.keys()),
)

if selected_commodity_name == show_all_label:
    display_list = list(commodity_map.values())
else:
    c = commodity_map.get(selected_commodity_name)
    display_list = [c] if c else []

# ── Metric labels ─────────────────────────────────────────────────────────────
_metric_min = {
    "en": "Typical min (across regions)",
    "ta": "வழக்கமான குறைந்தபட்சம் (பிராந்தியங்களில்)",
    "te": "సాధారణ కనిష్ఠం (ప్రాంతాల్లో)",
    "hi": "सामान्य न्यूनतम (क्षेत्रों में)",
}.get(lang, "Typical min (across regions)")

_metric_modal = {
    "en": "Typical modal (across regions)",
    "ta": "வழக்கமான மோடல் விலை (பிராந்தியங்களில்)",
    "te": "సాధారణ మోడల్ (ప్రాంతాల్లో)",
    "hi": "सामान्य मोडल (क्षेत्रों में)",
}.get(lang, "Typical modal (across regions)")

_metric_max = {
    "en": "Typical max (across regions)",
    "ta": "வழக்கமான அதிகபட்சம் (பிராந்தியங்களில்)",
    "te": "సాధారణ గరిష్ఠం (ప్రాంతాల్లో)",
    "hi": "सामान्य अधिकतम (क्षेत्रों में)",
}.get(lang, "Typical max (across regions)")

_caption = {
    "en": "⚠️ Approximate illustrative range only. Check current prices at AGMARKNET or e-NAM before selling.",
    "ta": "⚠️ தோராயமான விலை வரம்பு மட்டும். விற்பனைக்கு முன் AGMARKNET அல்லது e-NAM இல் நடப்பு விலைகளை சரிபார்க்கவும்.",
    "te": "⚠️ సుమారు సూచించే శ్రేణి మాత్రమే. విక్రయించే ముందు AGMARKNET లేదా e-NAM లో ప్రస్తుత ధరలు తనిఖీ చేయండి.",
    "hi": "⚠️ केवल अनुमानित उदाहरणात्मक श्रेणी। बेचने से पहले AGMARKNET या e-NAM पर मौजूदा कीमतें जांचें।",
}.get(lang, "⚠️ Approximate illustrative range only. Check current prices at AGMARKNET or e-NAM before selling.")

for commodity in display_list:
    name = commodity.get("commodity_name", {}).get(lang) or commodity.get("commodity_name", {}).get("en", "")
    unit = localize_market_unit(commodity.get("unit", "₹/quintal"), lang)
    markets = commodity.get("markets", [])

    with st.expander(f"**{name}** — {unit}", expanded=(len(display_list) == 1)):
        st.markdown(format_price_table(commodity, lang))

        if markets:
            all_min = [m.get("min", 0) for m in markets if m.get("min")]
            all_max = [m.get("max", 0) for m in markets if m.get("max")]
            all_modal = [m.get("modal", 0) for m in markets if m.get("modal")]
            if all_modal:
                col_a, col_b, col_c = st.columns(3)
                col_a.metric(_metric_min, f"₹{min(all_min)}")
                col_b.metric(_metric_modal, f"₹{round(sum(all_modal)/len(all_modal))}")
                col_c.metric(_metric_max, f"₹{max(all_max)}")

        st.caption(_caption)

# ── Price literacy tips ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader(get_label("tips_better_prices", lang))

_tips = {
    "en": [
        "**Grade your produce** before taking it to market — graded produce fetches 10–20% higher price.",
        "**Check AGMARKNET or e-NAM** daily in the week before planned sale to identify the best mandi.",
        "**Join a Farmer Producer Organisation (FPO)** — collective selling reduces transport costs and improves bargaining power.",
        "**Do not sell under distress** immediately after harvest if you have storage. Wait for price recovery when possible.",
        "**Understand MSP**: Check the Government of India's Minimum Support Price for your crop. NAFED, FCI and cooperative procurement happens at or above MSP in many states.",
        "**Consider agri-processing**: During price gluts, value addition (drying, grinding, packaging) may improve net realisation.",
        "**PM-KISAN and PMFBY**: Register for PM-KISAN direct income support and PM Fasal Bima Yojana crop insurance if not already enrolled.",
    ],
    "ta": [
        "**உங்கள் விளைபொருளை தரப்படுத்துங்கள்** — தரப்படுத்தப்பட்ட விளைபொருள் 10–20% அதிக விலை பெறும்.",
        "**AGMARKNET அல்லது e-NAM சரிபார்க்கவும்** — திட்டமிட்ட விற்பனைக்கு ஒரு வாரம் முன்பு சிறந்த மண்டியை கண்டுபிடிக்கவும்.",
        "**விவசாயி உற்பத்தியாளர் நிறுவனத்தில் (FPO) சேருங்கள்** — கூட்டு விற்பனை போக்குவரத்து செலவை குறைக்கும்.",
        "**நெருக்கடியில் விற்காதீர்கள்** — சேமிப்பு வசதி இருந்தால் விலை ஏறும் வரை காத்திருங்கள்.",
        "**MSP புரிந்துகொள்ளுங்கள்**: உங்கள் பயிருக்கான குறைந்தபட்ச ஆதார விலையை அரசு அறிவிக்கிறது.",
        "**விவசாய பதப்படுத்துதல்**: விலை வீழ்ச்சியில் உலர்த்துதல், அரைத்தல், பேக்கேஜிங் மதிப்பை அதிகரிக்கலாம்.",
        "**PM-KISAN மற்றும் PMFBY**: PM-KISAN நேரடி வருமான ஆதரவு மற்றும் பயிர் காப்பீட்டுக்கு பதிவு செய்யுங்கள்.",
    ],
    "te": [
        "**మీ ఉత్పత్తిని గ్రేడ్ చేయండి** — గ్రేడ్ చేసిన ఉత్పత్తి 10–20% అధిక ధర పొందుతుంది.",
        "**AGMARKNET లేదా e-NAM తనిఖీ చేయండి** — అమ్మకానికి ముందు వారంలో ప్రతిరోజు తనిఖీ చేసి మంచి మండి గుర్తించండి.",
        "**రైతు ఉత్పత్తిదారుల సంస్థ (FPO) లో చేరండి** — సామూహిక విక్రయం రవాణా ఖర్చులు తగ్గిస్తుంది.",
        "**ఒత్తిడిలో అమ్మకండి** — నిల్వ సదుపాయం ఉంటే ధర పుంజుకున్న తర్వాత అమ్మండి.",
        "**MSP అర్థం చేసుకోండి**: మీ పంటకు కేంద్ర ప్రభుత్వం ప్రకటించిన కనీస మద్దతు ధర తనిఖీ చేయండి.",
        "**వ్యవసాయ ప్రాసెసింగ్ పరిశీలించండి**: ధర పతనంలో ఆరబెట్టడం, పేకేజింగ్ నికర ఆదాయం మెరుగుపరుస్తుంది.",
        "**PM-KISAN మరియు PMFBY**: PM-KISAN ప్రత్యక్ష ఆదాయ మద్దతు మరియు పంట బీమాకు నమోదు చేయండి.",
    ],
    "hi": [
        "**अपनी उपज को ग्रेड करें** — ग्रेडेड उपज 10–20% अधिक कीमत पाती है।",
        "**AGMARKNET या e-NAM देखें** — बिक्री से एक हफ्ते पहले रोज़ देखकर सबसे अच्छी मंडी चुनें।",
        "**किसान उत्पादक संगठन (FPO) में जुड़ें** — सामूहिक बिक्री परिवहन लागत कम करती है और मोल-भाव क्षमता बढ़ाती है।",
        "**संकट में न बेचें** — यदि भंडारण है तो कीमत सुधरने का इंतजार करें।",
        "**MSP समझें**: अपनी फसल के लिए सरकार का न्यूनतम समर्थन मूल्य जाँचें। NAFED, FCI और सहकारी खरीद MSP पर या उससे ऊपर होती है।",
        "**कृषि-प्रसंस्करण सोचें**: कीमत गिरने पर सुखाने, पीसने, पैकेजिंग से शुद्ध आय बढ़ सकती है।",
        "**PM-KISAN और PMFBY**: PM-KISAN प्रत्यक्ष आय सहायता और फसल बीमा के लिए नामांकन करें।",
    ],
}
for tip in _tips.get(lang, _tips["en"]):
    st.markdown(f"- {tip}")

# ── MSP note ─────────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander(get_label("about_msp", lang)):
    _msp_text = {
        "en": """
The **Minimum Support Price (MSP)** is the price at which the Government of India commits to
purchase certain crops from farmers, if market prices fall below MSP.

Key points:
- MSP is announced for about 23 crops by the Cabinet Committee on Economic Affairs (CCEA) each year.
- MSP does **not** guarantee that open market prices will be at or above MSP — they can be higher or lower.
- Procurement at MSP happens through state agencies, NAFED, FCI and other government bodies.
- Not all crops have MSP; not all farmers can access procurement in all areas.
- Check the latest MSP: [desagri.gov.in](https://desagri.gov.in) or DAC&FW website.

**MSP is not shown in this application** because it changes every year —
always verify the current year's MSP from official government sources.
""",
        "ta": """
**குறைந்தபட்ச ஆதார விலை (MSP)** என்பது சந்தை விலை MSP-ஐ விட குறைந்தால் அரசு விவசாயிகளிடம் பயிர்களை வாங்கும் விலை.

முக்கிய குறிப்புகள்:
- ஒவ்வொரு ஆண்டும் CCEA சுமார் 23 பயிர்களுக்கு MSP அறிவிக்கும்.
- MSP சந்தை விலை அதற்கு மேலே இருக்கும் என்று உத்தரவாதம் அளிக்காது.
- கொள்முதல் NAFED, FCI மற்றும் மாநில அமைப்புகள் மூலம் நடைபெறும்.
- **MSP இந்த பயன்பாட்டில் காட்டப்படவில்லை** — அதிகாரப்பூர்வ அரசு ஆதாரங்களிலிருந்து ஒவ்வொரு ஆண்டும் சரிபார்க்கவும்.
""",
        "te": """
**కనీస మద్దతు ధర (MSP)** అంటే మార్కెట్ ధరలు MSP కంటే తక్కువగా పడిపోతే ప్రభుత్వం రైతుల నుండి పంటలు కొనే ధర.

ముఖ్యమైన అంశాలు:
- ప్రతి సంవత్సరం CCEA సుమారు 23 పంటలకు MSP ప్రకటిస్తుంది.
- MSP బహిరంగ మార్కెట్ ధరలు MSP కంటే ఎక్కువగా ఉంటాయని హామీ ఇవ్వదు.
- కొనుగోలు NAFED, FCI మరియు రాష్ట్ర సంస్థల ద్వారా జరుగుతుంది.
- **MSP ఈ అప్లికేషన్‌లో చూపబడలేదు** — ప్రతి సంవత్సరం అధికారిక ప్రభుత్వ మూలాల నుండి ధృవీకరించండి.
""",
        "hi": """
**न्यूनतम समर्थन मूल्य (MSP)** वह मूल्य है जिस पर भारत सरकार किसानों से फसल खरीदने की प्रतिबद्धता करती है, यदि बाजार मूल्य MSP से नीचे गिर जाए।

मुख्य बिंदु:
- CCEA प्रत्येक वर्ष लगभग 23 फसलों के लिए MSP घोषित करती है।
- MSP यह गारंटी नहीं देता कि खुले बाजार की कीमतें MSP पर या उससे ऊपर होंगी।
- खरीद NAFED, FCI और राज्य एजेंसियों के माध्यम से होती है।
- **MSP इस एप्लिकेशन में नहीं दिखाया गया** — आधिकारिक सरकारी स्रोतों से हर साल सत्यापित करें।
""",
    }
    st.markdown(_msp_text.get(lang, _msp_text["en"]))

# ── Future integration note ────────────────────────────────────────────────────
st.markdown("---")
st.info(get_label("future_integration", lang))

# ── Sources caption ────────────────────────────────────────────────────────────
_sources_text = {
    "en": "Market information sources: AGMARKNET, e-NAM, DAC&FW annual agricultural statistics. Reference period: 2023–2024 general calibration. Prices are NOT real-time.",
    "ta": "சந்தை தகவல் ஆதாரங்கள்: AGMARKNET, e-NAM, DAC&FW ஆண்டு வேளாண் புள்ளிவிவரங்கள். குறிப்பு காலம்: 2023–2024. விலைகள் நேரடி அல்ல.",
    "te": "మార్కెట్ సమాచార మూలాలు: AGMARKNET, e-NAM, DAC&FW వార్షిక వ్యవసాయ గణాంకాలు. సూచన కాలం: 2023–2024. ధరలు నేరుగా కాదు.",
    "hi": "बाजार सूचना स्रोत: AGMARKNET, e-NAM, DAC&FW वार्षिक कृषि सांख्यिकी। संदर्भ अवधि: 2023–2024। कीमतें रियल-टाइम नहीं हैं।",
}
st.caption(_sources_text.get(lang, _sources_text["en"]))
