"""
pages/4_AI_Farming_Assistant.py
Main AI farming chat interface — full i18n.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.config import APP_TITLE, LLM_PROVIDER
from src.language_service import get_label
from src.shared_utils import inject_css, init_session_state, render_sidebar
from src.farming_advisor import ask

st.set_page_config(page_title=f"{get_label('ai_assistant','en')} — {APP_TITLE}", page_icon="🤖", layout="wide")
init_session_state()
inject_css()
lang = render_sidebar("ai_assistant")

if LLM_PROVIDER == "ibm_granite":
    st.info(get_label("ibm_granite_mode", lang))
else:
    st.info(get_label("demo_mode_banner", lang))

st.title(f"🤖 {get_label('ai_assistant', lang)}")
st.markdown(get_label("ai_intro", lang))
st.markdown("---")

# ── Suggested questions ────────────────────────────────────────────────────────
with st.expander(get_label("suggested_questions", lang)):
    suggestions = {
        "en": [
            "When should I sow paddy in Tamil Nadu?",
            "What crops are suitable for black cotton soil in Maharashtra Kharif?",
            "How do I make compost at home?",
            "My tomato leaves are turning yellow — what could be wrong?",
            "What is the approximate price of onion in Nashik?",
            "Is it safe to work in the field during a thunderstorm?",
            "How do I install an RCCB for my water pump?",
            "What is the MSP for wheat in 2023-24?",
            "How should I manage pests in cotton organically?",
            "What are the steps to harvest and store groundnut?",
        ],
        "ta": [
            "தமிழ்நாட்டில் நெல் எப்போது விதைக்க வேண்டும்?",
            "மண் பரிசோதனை எப்படி செய்வது?",
            "தக்காளியில் பூச்சி தாக்குதல் எப்படி கட்டுப்படுத்துவது?",
            "மழை பெய்யும்போது பயிர்களுக்கு மருந்து தெளிக்கலாமா?",
            "மண்புழு உரம் எப்படி செய்வது?",
            "மகாராஷ்டிராவின் காரீஃப் பருவத்தில் கரிசல் மண்ணுக்கு ஏற்ற பயிர்கள் எவை?",
            "நாஷிக்கில் வெங்காயத்தின் தோராயமான விலை என்ன?",
            "இடி மின்னலின்போது வயலில் வேலை செய்வது பாதுகாப்பானதா?",
            "நீர்ப்பம்புக்கு RCCB-ஐ எப்படிப் பொருத்துவது?",
            "2023–24-இல் கோதுமைக்கான MSP என்ன?",
            "பருத்தியில் பூச்சிகளை இயற்கை முறையில் எப்படிக் கட்டுப்படுத்துவது?",
            "நிலக்கடலையை அறுவடை செய்து சேமிப்பது எப்படி?",
        ],
        "te": [
            "ఆంధ్రప్రదేశ్‌లో వేరుశనగను ఎప్పుడు విత్తాలి?",
            "నేల పరీక్ష ఎలా చేయాలి?",
            "పత్తిలో తెల్ల ఈగను ఎలా నివారించాలి?",
            "వర్మీకంపోస్ట్ ఎలా తయారు చేయాలి?",
            "మహారాష్ట్ర ఖరీఫ్‌లో నల్లరేగడి నేలకు ఏ పంటలు అనుకూలం?",
            "నాసిక్‌లో ఉల్లి ధర సుమారుగా ఎంత ఉంటుంది?",
            "ఉరుములతో కూడిన వర్షంలో పొలంలో పనిచేయడం సురక్షితమేనా?",
            "నీటి పంపుకు RCCBని ఎలా అమర్చాలి?",
            "2023–24లో గోధుమకు MSP ఎంత?",
            "పత్తిలో చీడపీడలను సేంద్రియంగా ఎలా నిర్వహించాలి?",
            "వేరుశనగను కోసి నిల్వ చేయడం ఎలా?",
        ],
        "hi": [
            "गेहूं की सिंचाई कब करें?",
            "सोयाबीन में कीट नियंत्रण कैसे करें?",
            "मिट्टी परीक्षण कैसे करवाएं?",
            "वर्मीकम्पोस्ट कैसे बनाएं?",
            "महाराष्ट्र में खरीफ के दौरान काली मिट्टी के लिए कौन-सी फसलें उपयुक्त हैं?",
            "नाशिक में प्याज का अनुमानित भाव क्या है?",
            "गरज-चमक के दौरान खेत में काम करना सुरक्षित है?",
            "पानी के पंप में RCCB कैसे लगाएँ?",
            "2023–24 में गेहूँ का MSP क्या था?",
            "कपास में कीटों का जैविक प्रबंधन कैसे करें?",
            "मूंगफली की कटाई और भंडारण कैसे करें?",
        ],
    }
    lang_suggestions = suggestions.get(lang, suggestions["en"])
    cols = st.columns(2)
    for i, sug in enumerate(lang_suggestions):
        if cols[i % 2].button(sug, key=f"sug_{i}"):
            st.session_state["prefill_question"] = sug

st.markdown("---")

# ── Chat history ───────────────────────────────────────────────────────────────
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(chat["question"])
    with st.chat_message("assistant"):
        if chat.get("is_demo"):
            st.caption(get_label("demo_mode_notice", lang))
            if chat.get("provider_diagnostic"):
                st.caption(f"IBM connection detail: {chat['provider_diagnostic']}")
        elif chat.get("provider_error"):
            st.warning(get_label("granite_response_unavailable", lang))
            if chat.get("provider_diagnostic"):
                st.caption(f"IBM connection detail: {chat['provider_diagnostic']}")
        elif LLM_PROVIDER == "ibm_granite":
            st.success(get_label("granite_response_verified", lang))
        st.markdown(chat["answer"])
        if chat.get("has_safety"):
            st.error(get_label("safety_content_notice", lang))
        if chat.get("sources"):
            with st.expander(get_label("sources", lang)):
                for s in chat["sources"]:
                    st.markdown(f"- {s}")
        if chat.get("confidence"):
            st.caption(chat["confidence"])

# ── Clear chat in sidebar (added after sidebar rendered) ──────────────────────
with st.sidebar:
    st.markdown("---")
    if st.button(get_label("clear_chat", lang)):
        st.session_state.chat_history = []
        st.rerun()

# ── Input ──────────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_question", "")
question = st.chat_input(get_label("ask_question", lang))

if question is None and prefill:
    question = prefill

if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(get_label("retrieving", lang)):
            result = ask(
                question=question,
                lang_code=lang,
                profile=st.session_state.profile,
            )
        if result.is_demo:
            st.caption(get_label("demo_mode_notice", lang))
            if result.provider_diagnostic:
                st.caption(f"IBM connection detail: {result.provider_diagnostic}")
        elif result.provider_error:
            st.warning(get_label("granite_response_unavailable", lang))
            if result.provider_diagnostic:
                st.caption(f"IBM connection detail: {result.provider_diagnostic}")
        elif LLM_PROVIDER == "ibm_granite":
            st.success(get_label("granite_response_verified", lang))
        if result.has_safety_content:
            st.error(get_label("safety_content_notice", lang))
        st.markdown(result.answer)
        if result.confidence:
            st.caption(result.confidence)
        if result.sources:
            with st.expander(get_label("sources", lang)):
                for s in result.sources:
                    st.markdown(f"- {s}")

    st.session_state.chat_history.append({
        "question": question,
        "answer": result.answer,
        "sources": result.sources,
        "confidence": result.confidence,
        "is_demo": result.is_demo,
        "provider_error": result.provider_error,
        "provider_diagnostic": result.provider_diagnostic,
        "has_safety": result.has_safety_content,
    })

st.markdown("---")
st.caption(get_label("ai_disclaimer", lang))
