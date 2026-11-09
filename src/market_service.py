"""
src/market_service.py
Market price service.
Currently serves illustrative approximate prices from local JSON data.
Designed for future integration with AGMARKNET or e-NAM APIs.

IMPORTANT: All prices returned by this module are illustrative/approximate only.
They are NOT real-time mandi prices. Always direct users to verify at AGMARKNET
or their local mandi.
"""
import json
import logging
import re
from pathlib import Path
from typing import Optional

from src.config import DATA_DIR

logger = logging.getLogger(__name__)

_DISCLAIMER = {
    "en": "⚠️ **Price Disclaimer**: These are **approximate illustrative ranges** based on general historical patterns. They are **NOT real-time mandi prices**. Actual prices vary by mandi, variety, quality grade, moisture content and date. Always verify current prices at [AGMARKNET](https://agmarknet.nic.in), [e-NAM](https://enam.gov.in) or your local mandi.",
    "ta": "⚠️ **விலை மறுப்பு**: இவை பொதுவான வரலாற்றுப் போக்குகளை அடிப்படையாகக் கொண்ட **தோராயமான எடுத்துக்காட்டு வரம்புகள்** மட்டுமே; **நேரடி மண்டி விலைகள் அல்ல**. மண்டி, ரகம், தரம், ஈரப்பதம் மற்றும் தேதியைப் பொறுத்து விலைகள் மாறும். விற்பனைக்கு முன் [AGMARKNET](https://agmarknet.nic.in), [e-NAM](https://enam.gov.in) அல்லது உள்ளூர் மண்டியில் நடப்பு விலையைச் சரிபார்க்கவும்.",
    "te": "⚠️ **ధరల నిరాకరణ**: ఇవి సాధారణ చారిత్రక ధోరణుల ఆధారంగా ఇచ్చిన **సుమారు సూచనాత్మక ధరల శ్రేణులు** మాత్రమే; **ప్రస్తుత మండి ధరలు కావు**. మండి, రకం, నాణ్యత, తేమ, తేదీ ఆధారంగా ధర మారుతుంది. విక్రయానికి ముందు [AGMARKNET](https://agmarknet.nic.in), [e-NAM](https://enam.gov.in) లేదా స్థానిక మండిలో ప్రస్తుత ధరను నిర్ధారించండి.",
    "hi": "⚠️ **मूल्य अस्वीकरण**: ये सामान्य ऐतिहासिक रुझानों पर आधारित **अनुमानित सांकेतिक मूल्य-सीमाएँ** हैं; ये **मंडी के वास्तविक समय के भाव नहीं हैं**। मंडी, किस्म, गुणवत्ता, नमी और तारीख के अनुसार भाव बदलते हैं। बेचने से पहले [AGMARKNET](https://agmarknet.nic.in), [e-NAM](https://enam.gov.in) या स्थानीय मंडी में मौजूदा भाव जाँचें।",
}

_AGMARKNET_URL = "https://agmarknet.nic.in"
_ENAM_URL = "https://enam.gov.in"


def _load_market_data() -> Optional[dict]:
    """Load market prices JSON file."""
    path = DATA_DIR / "market_prices.json"
    if not path.exists():
        logger.warning("market_prices.json not found at %s", path)
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Error loading market_prices.json: %s", exc)
        return None


def get_all_commodities() -> list[dict]:
    """
    Return all commodities with their price data.
    Each item includes commodity_id, commodity_name, unit and markets list.
    """
    data = _load_market_data()
    if not data:
        return []
    return data.get("commodities", [])


def get_commodity_price(commodity_id: str) -> Optional[dict]:
    """
    Get price data for a specific commodity by its ID.
    Returns None if not found.
    """
    commodities = get_all_commodities()
    for item in commodities:
        if item.get("commodity_id") == commodity_id:
            return item
    return None


def get_commodity_ids() -> list[str]:
    """Return list of all available commodity IDs."""
    return [c.get("commodity_id", "") for c in get_all_commodities()]


def localize_market_unit(unit: str, lang_code: str = "en") -> str:
    translations = {
        "₹ per quintal": {"ta": "₹ / குவிண்டால்", "te": "₹ / క్వింటాల్", "hi": "₹ / क्विंटल"},
        "₹ per dozen": {"ta": "₹ / டஜன்", "te": "₹ / డజను", "hi": "₹ / दर्जन"},
        "₹ per tonne": {"ta": "₹ / டன்", "te": "₹ / టన్ను", "hi": "₹ / टन"},
        "₹/quintal": {"ta": "₹ / குவிண்டால்", "te": "₹ / క్వింటాల్", "hi": "₹ / क्विंटल"},
    }
    return translations.get(unit, {}).get(lang_code, unit)


def _localize_market_note(note: str, lang_code: str) -> str:
    if lang_code == "en" or not note:
        return note
    match = re.fullmatch(r"MSP reference ~₹(\d+)/quintal \(2023-24\)", note)
    if match:
        amount = match.group(1)
        templates = {
            "ta": f"2023–24 MSP குறிப்பு: குவிண்டாலுக்கு சுமார் ₹{amount}",
            "te": f"2023–24 MSP సూచన: క్వింటాల్‌కు సుమారు ₹{amount}",
            "hi": f"2023–24 MSP संदर्भ: लगभग ₹{amount} प्रति क्विंटल",
        }
        return templates.get(lang_code, note)
    return note


def format_price_table(commodity_data: dict, lang_code: str = "en") -> str:
    """
    Format a commodity's price data as a Markdown table string.
    """
    if not commodity_data:
        return {
            "ta": "விலைத் தரவு கிடைக்கவில்லை.",
            "te": "ధరల సమాచారం అందుబాటులో లేదు.",
            "hi": "मूल्य जानकारी उपलब्ध नहीं है।",
        }.get(lang_code, "No price data available.")

    name = commodity_data.get("commodity_name", {}).get(lang_code) or \
           commodity_data.get("commodity_name", {}).get("en", "Unknown")
    unit = commodity_data.get("unit", "₹/quintal")
    unit = localize_market_unit(unit, lang_code)

    headings = {
        "en": ("Region / Market", "Min Price", "Max Price", "Modal Price", "Notes"),
        "ta": ("பகுதி / சந்தை", "குறைந்த விலை", "அதிக விலை", "சராசரி விலை", "குறிப்புகள்"),
        "te": ("ప్రాంతం / మార్కెట్", "కనిష్ఠ ధర", "గరిష్ఠ ధర", "మోడల్ ధర", "గమనికలు"),
        "hi": ("क्षेत्र / मंडी", "न्यूनतम भाव", "अधिकतम भाव", "मॉडल भाव", "टिप्पणियाँ"),
    }.get(lang_code, ("Region / Market", "Min Price", "Max Price", "Modal Price", "Notes"))
    lines = [
        f"**{name}** — {unit}",
        "",
        "| " + " | ".join(headings) + " |",
        "|---|---|---|---|---|",
    ]

    common_notes = {
        "Common grade": {
            "ta": "பொதுத் தரம்", "te": "సాధారణ నాణ్యత", "hi": "सामान्य गुणवत्ता",
        },
        "Fair average quality": {
            "ta": "நியாயமான சராசரி தரம்", "te": "సగటు నాణ్యత ప్రమాణం", "hi": "उचित औसत गुणवत्ता",
        },
        "Major production zone": {
            "ta": "முக்கிய உற்பத்திப் பகுதி", "te": "ప్రధాన ఉత్పత్తి ప్రాంతం", "hi": "प्रमुख उत्पादन क्षेत्र",
        },
        "Mixed grade": {
            "ta": "கலப்புத் தரம்", "te": "మిశ్రమ నాణ్యత", "hi": "मिश्रित गुणवत्ता",
        },
        "Common grade paddy; MSP reference ~₹2183/quintal (2023-24)": {
            "ta": "பொதுத் தர நெல்; 2023–24 MSP குறிப்பு: குவிண்டாலுக்கு சுமார் ₹2183",
            "te": "సాధారణ వరి; 2023–24 MSP సూచన: క్వింటాల్‌కు సుమారు ₹2183",
            "hi": "सामान्य धान; 2023–24 MSP संदर्भ: लगभग ₹2183 प्रति क्विंटल",
        },
        "MSP reference ~₹2275/quintal (2023-24); procurement at MSP common": {
            "ta": "2023–24 MSP குறிப்பு: குவிண்டாலுக்கு சுமார் ₹2275; MSP-யில் கொள்முதல் வழக்கம்",
            "te": "2023–24 MSP సూచన: క్వింటాల్‌కు సుమారు ₹2275; MSP వద్ద కొనుగోలు సాధారణం",
            "hi": "2023–24 MSP संदर्भ: लगभग ₹2275 प्रति क्विंटल; MSP पर खरीद आम है",
        },
        "Fair and Remunerative Price (FRP) ~₹3150/tonne (2023-24); mills may pay above FRP": {
            "ta": "நியாயமான மற்றும் ஆதாய விலை (FRP): 2023–24-இல் டன்னுக்கு சுமார் ₹3150; ஆலைகள் அதிகம் வழங்கலாம்",
            "te": "న్యాయమైన మరియు లాభదాయక ధర (FRP): 2023–24లో టన్నుకు సుమారు ₹3150; మిల్లులు ఇంకా ఎక్కువ చెల్లించవచ్చు",
            "hi": "उचित एवं लाभकारी मूल्य (FRP): 2023–24 में लगभग ₹3150 प्रति टन; मिलें इससे अधिक दे सकती हैं",
        },
        "Medium staple; MSP Long: ~₹7020, Medium: ~₹6620 (2023-24)": {
            "ta": "நடுத்தர இழை; 2023–24 MSP குறிப்பு: நீள இழை சுமார் ₹7020, நடுத்தர இழை ₹6620",
            "te": "మధ్యస్థ పీచు; 2023–24 MSP సూచన: పొడవైన పీచు సుమారు ₹7020, మధ్యస్థం ₹6620",
            "hi": "मध्यम रेशा; 2023–24 MSP संदर्भ: लंबा रेशा लगभग ₹7020, मध्यम ₹6620",
        },
        "Common paddy": {"ta": "பொதுத் தர நெல்", "te": "సాధారణ వరి", "hi": "सामान्य धान"},
        "Common wheat": {"ta": "பொதுத் தர கோதுமை", "te": "సాధారణ గోధుమ", "hi": "सामान्य गेहूँ"},
        "Common yellow maize": {"ta": "பொதுத் தர மஞ்சள் மக்காச்சோளம்", "te": "సాధారణ పసుపు మొక్కజొన్న", "hi": "सामान्य पीला मक्का"},
        "Common grade yellow mustard": {"ta": "பொதுத் தர மஞ்சள் கடுகு", "te": "సాధారణ పసుపు ఆవాలు", "hi": "सामान्य पीली सरसों"},
        "PR varieties; procurement at MSP common": {"ta": "PR ரகங்கள்; MSP-யில் கொள்முதல் வழக்கம்", "te": "PR రకాలు; MSP వద్ద కొనుగోలు సాధారణం", "hi": "PR किस्में; MSP पर खरीद आम है"},
        "Samba/Ponni variety commands premium": {"ta": "சம்பா / பொன்னி ரகங்களுக்கு கூடுதல் விலை கிடைக்கும்", "te": "సాంబా / పొన్ని రకాలకు అధిక ధర లభిస్తుంది", "hi": "सांबा / पोन्नी किस्मों को प्रीमियम भाव मिलता है"},
        "Sangli is a major turmeric trading hub": {"ta": "சாங்லி முக்கிய மஞ்சள் வர்த்தக மையம்", "te": "సాంగ్లీ ప్రధాన పసుపు వాణిజ్య కేంద్రం", "hi": "सांगली प्रमुख हल्दी व्यापार केंद्र है"},
        "Major production zone": {"ta": "முக்கிய உற்பத்திப் பகுதி", "te": "ప్రధాన ఉత్పత్తి ప్రాంతం", "hi": "प्रमुख उत्पादन क्षेत्र"},
        "Consumption centre prices": {"ta": "நுகர்வு மைய விலைகள்", "te": "వినియోగ కేంద్రాల ధరలు", "hi": "उपभोग केंद्रों के भाव"},
        "Desi gram": {"ta": "தேசி கொண்டைக்கடலை", "te": "దేశీ శనగ", "hi": "देसी चना"},
        "Fair average quality": {"ta": "நியாயமான சராசரி தரம்", "te": "సగటు నాణ్యత ప్రమాణం", "hi": "उचित औसत गुणवत्ता"},
        "FRP applies; cooperative sugar factories": {"ta": "FRP பொருந்தும்; கூட்டுறவு சர்க்கரை ஆலைகள்", "te": "FRP వర్తిస్తుంది; సహకార చక్కెర కర్మాగారాలు", "hi": "FRP लागू; सहकारी चीनी मिलें"},
        "FRP applies; prices by sugar recovery percentage": {"ta": "FRP பொருந்தும்; சர்க்கரை மீட்பு சதவீதத்தைப் பொறுத்து விலை", "te": "FRP వర్తిస్తుంది; చక్కెర రికవరీ శాతాన్ని బట్టి ధర", "hi": "FRP लागू; चीनी रिकवरी प्रतिशत के अनुसार भाव"},
        "Byadgi variety commands premium for deep red colour": {"ta": "ஆழமான சிவப்பு நிறத்தால் பியாட்கி ரகத்திற்கு கூடுதல் விலை", "te": "గాఢ ఎరుపు రంగు వల్ల బ్యాడగి రకానికి అధిక ధర", "hi": "गहरे लाल रंग के कारण बयाडगी किस्म को प्रीमियम भाव"},
        "Jalgaon is major banana production zone": {"ta": "ஜல்கான் முக்கிய வாழை உற்பத்திப் பகுதி", "te": "జల్గావ్ ప్రధాన అరటి ఉత్పత్తి ప్రాంతం", "hi": "जलगाँव प्रमुख केला उत्पादक क्षेत्र है"},
        "Long staple; premium over medium staple": {"ta": "நீண்ட இழை; நடுத்தர இழையைவிட கூடுதல் விலை", "te": "పొడవైన పీచు; మధ్యస్థం కంటే అధిక ధర", "hi": "लंबा रेशा; मध्यम रेशे से अधिक भाव"},
        "Medium staple": {"ta": "நடுத்தர இழை", "te": "మధ్యస్థ పీచు", "hi": "मध्यम रेशा"},
        "Mixed grade": {"ta": "கலப்புத் தரம்", "te": "మిశ్రమ నాణ్యత", "hi": "मिश्रित गुणवत्ता"},
        "Shelled; MSP ref ~₹6783/quintal (2023-24)": {"ta": "தோல் நீக்கியது; 2023–24 MSP குறிப்பு: குவிண்டாலுக்கு சுமார் ₹6783", "te": "పొట్టు తీసినది; 2023–24 MSP సూచన: క్వింటాల్‌కు సుమారు ₹6783", "hi": "छिली हुई; 2023–24 MSP संदर्भ: लगभग ₹6783 प्रति क्विंटल"},
        "Unshelled pods; prices highly seasonal": {"ta": "தோல் நீக்காத காய்கள்; பருவத்தைப் பொறுத்து விலை மாறும்", "te": "పొట్టు తీయని కాయలు; సీజన్‌ను బట్టి ధర మారుతుంది", "hi": "बिना छिली फलियाँ; मौसम के अनुसार भाव बदलते हैं"},
        "Unshelled; quality premium for bold varieties": {"ta": "தோல் நீக்காதது; பெரிய விதை ரகங்களுக்கு கூடுதல் விலை", "te": "పొట్టు తీయనిది; పెద్ద గింజ రకాలకు అధిక ధర", "hi": "बिना छिली; बड़े दाने वाली किस्मों को प्रीमियम भाव"},
        "Rabi onion; varies significantly by season": {"ta": "ரபி வெங்காயம்; பருவத்தைப் பொறுத்து விலை மாறும்", "te": "రబీ ఉల్లి; సీజన్‌ను బట్టి ధర మారుతుంది", "hi": "रबी प्याज; मौसम के अनुसार भाव बदलता है"},
        "Prices are EXTREMELY volatile. Madanapalle is India's major tomato trading hub.": {"ta": "விலைகள் மிக அதிகமாக மாறக்கூடும். மதனப்பள்ளி முக்கிய தக்காளி வர்த்தக மையம்.", "te": "ధరలు అత్యంత మారుతాయి. మదనపల్లె ప్రధాన టమాటా వాణిజ్య కేంద్రం.", "hi": "भाव में बहुत उतार-चढ़ाव होता है। मदनपल्ले प्रमुख टमाटर व्यापार केंद्र है।"},
        "Prices are HIGHLY volatile—range is wide across seasons. Lasalgaon is Asia's largest onion market.": {"ta": "விலைகள் அதிகம் மாறுபடும்; பருவங்களுக்கிடையே வரம்பு பெரியது. லாசல்கான் ஆசியாவின் பெரிய வெங்காய சந்தை.", "te": "ధరలు చాలా మారుతాయి; సీజన్ల మధ్య తేడా ఎక్కువ. లాసల్‌గావ్ ఆసియాలో అతిపెద్ద ఉల్లి మార్కెట్.", "hi": "भाव में बहुत उतार-चढ़ाव और मौसम के अनुसार बड़ा अंतर होता है। लासलगाँव एशिया की सबसे बड़ी प्याज मंडी है।"},
        "Guntur is India's largest dry chilli market. Wide price range by variety (Teja, Byadgi, 334 etc.) and quality grade.": {"ta": "குண்டூர் இந்தியாவின் பெரிய உலர் மிளகாய் சந்தை. ரகம் (தேஜா, பியாட்கி, 334) மற்றும் தரத்தைப் பொறுத்து விலை மாறும்.", "te": "గుంటూరు భారతదేశపు అతిపెద్ద ఎండు మిర్చి మార్కెట్. రకం (తేజా, బ్యాడగి, 334), నాణ్యతను బట్టి ధర మారుతుంది.", "hi": "गुंटूर भारत की सबसे बड़ी सूखी मिर्च मंडी है। किस्म (तेजा, बयाडगी, 334) और गुणवत्ता के अनुसार भाव बदलता है।"},
        "Erode (Tamil Nadu) and Nizamabad are major turmeric markets. Wide quality variation.": {"ta": "ஈரோடு (தமிழ்நாடு), நிஜாமாபாத் முக்கிய மஞ்சள் சந்தைகள்; தரத்தால் விலை மாறுபடும்.", "te": "ఈరోడ్ (తమిళనాడు), నిజామాబాద్ ప్రధాన పసుపు మార్కెట్లు; నాణ్యతను బట్టి ధర మారుతుంది.", "hi": "इरोड (तमिलनाडु) और निज़ामाबाद प्रमुख हल्दी मंडियाँ हैं; गुणवत्ता के अनुसार भाव बदलता है।"},
        "Price per dozen; Robusta and Nendran varieties command premium": {"ta": "ஒரு டஜன் விலை; ரொபஸ்டா, நேந்திரன் ரகங்களுக்கு கூடுதல் விலை", "te": "డజను ధర; రోబస్టా, నేంద్రన్ రకాలకు అధిక ధర", "hi": "प्रति दर्जन भाव; रोबस्टा और नेन्द्रन किस्मों को प्रीमियम मिलता है"},
    }

    for market in commodity_data.get("markets", []):
        region = market.get("region", "")
        min_p = market.get("min", "—")
        max_p = market.get("max", "—")
        modal = market.get("modal", "—")
        note = market.get("grade_note", "")
        note = common_notes.get(note, {}).get(lang_code, note)
        note = _localize_market_note(note, lang_code)
        lines.append(f"| {region} | ₹{min_p} | ₹{max_p} | ₹{modal} | {note} |")

    return "\n".join(lines)


def get_disclaimer(lang_code: str = "en") -> str:
    """Return the standard market price disclaimer."""
    return _DISCLAIMER.get(lang_code, _DISCLAIMER["en"])


def get_external_links(lang_code: str = "en") -> dict[str, str]:
    """Return official market information portal URLs."""
    labels = {
        "en": ("AGMARKNET (Live mandi prices)", "e-NAM (National Agriculture Market)"),
        "ta": ("AGMARKNET (நடப்பு மண்டி விலைகள்)", "e-NAM (தேசிய வேளாண் சந்தை)"),
        "te": ("AGMARKNET (ప్రస్తుత మండి ధరలు)", "e-NAM (జాతీయ వ్యవసాయ మార్కెట్)"),
        "hi": ("AGMARKNET (मंडी के मौजूदा भाव)", "e-NAM (राष्ट्रीय कृषि बाज़ार)"),
    }.get(lang_code, ("AGMARKNET (Live mandi prices)", "e-NAM (National Agriculture Market)"))
    return {labels[0]: _AGMARKNET_URL, labels[1]: _ENAM_URL}


# ── Future integration slot ───────────────────────────────────────────────────
# When AGMARKNET or e-NAM API credentials are available, replace the
# _load_market_data() function with an API call and update get_all_commodities()
# to use real-time data. The rest of the module interface remains unchanged.
#
# Example future implementation:
#
# def _fetch_agmarknet_prices(commodity: str, state: str, api_key: str) -> list[dict]:
#     """Fetch live prices from AGMARKNET API (not yet implemented)."""
#     raise NotImplementedError("AGMARKNET API integration pending credentials")
