"""
src/data_loader.py
Loads and validates all agricultural knowledge JSON files.
Returns them as flat lists of text chunks with metadata for the retrieval engine.
"""
import json
import logging
from pathlib import Path
from typing import Any

from src.config import DATA_DIR, RAG_CHUNK_SIZE

logger = logging.getLogger(__name__)


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_json(filename: str) -> Any:
    """Load a JSON file from the data directory."""
    path = DATA_DIR / filename
    if not path.exists():
        logger.warning("Data file not found: %s", path)
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _chunk_text(text: str, metadata: dict, chunk_size: int = RAG_CHUNK_SIZE) -> list[dict]:
    """Split long text into overlapping chunks keeping metadata."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    overlap = chunk_size // 4
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        chunks.append({"text": chunk_text, **metadata})
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


# ── individual loaders ────────────────────────────────────────────────────────

def load_crops() -> list[dict]:
    """Load crop catalogue as retrieval chunks."""
    data = _load_json("crops.json")
    if not data:
        return []
    chunks = []
    for crop in data:
        crop_id = crop.get("id", "unknown")
        name_en = crop.get("name", {}).get("en", crop_id)
        text_parts = [
            f"Crop: {name_en}",
            f"Category: {crop.get('category', '')}",
            f"Seasons: {', '.join(crop.get('seasons', []))}",
            f"Soil types: {', '.join(crop.get('soil_types', []))}",
            f"Water need: {crop.get('water_need', '')}",
            f"Major states: {', '.join(crop.get('major_states', []))}",
            f"Description: {crop.get('description', '')}",
            f"Typical yield: {crop.get('typical_yield_qtl_per_ha', '')} quintal/ha",
            f"Harvest duration: {crop.get('harvest_duration_days', '')} days",
        ]
        text = "\n".join(text_parts)
        meta = {
            "source": "crops.json",
            "topic": "crop_info",
            "crop_id": crop_id,
            "crop_name": name_en,
            "name_ta": crop.get("name", {}).get("ta", ""),
            "name_te": crop.get("name", {}).get("te", ""),
            "name_hi": crop.get("name", {}).get("hi", ""),
        }
        chunks.extend(_chunk_text(text, meta))
    return chunks


def load_state_crop_mapping() -> list[dict]:
    """Load state-crop mapping as retrieval chunks."""
    data = _load_json("state_crop_mapping.json")
    if not data:
        return []
    chunks = []
    for state, info in data.items():
        if state.startswith("_"):
            continue
        crops = info.get("suitable_crops", [])
        agro = info.get("agro_climate", "")
        text = (
            f"State: {state}\n"
            f"Suitable crops: {', '.join(crops)}\n"
            f"Agro-climate: {agro}\n"
            f"Kharif crops: {', '.join(info.get('kharif_crops', []))}\n"
            f"Rabi crops: {', '.join(info.get('rabi_crops', []))}\n"
            f"Major soil: {info.get('major_soil', '')}\n"
            f"Disclaimer: Indicative only. Consult local KVK or agriculture department."
        )
        meta = {
            "source": "state_crop_mapping.json",
            "topic": "state_crop_suitability",
            "state": state,
        }
        chunks.extend(_chunk_text(text, meta))
    return chunks


def load_crop_roadmaps() -> list[dict]:
    """Load crop lifecycle roadmaps as retrieval chunks (one chunk per stage)."""
    data = _load_json("crop_roadmaps.json")
    if not data:
        return []
    chunks = []
    for crop_id, roadmap in data.items():
        if crop_id.startswith("_"):
            continue
        crop_name = roadmap.get("crop_name", crop_id)
        seasons = roadmap.get("seasons", "")
        for stage in roadmap.get("stages", []):
            stage_num = stage.get("stage", "?")
            stage_name = stage.get("name", "")
            tasks = stage.get("tasks", [])
            warnings = stage.get("warnings", [])
            text_parts = [
                f"Crop: {crop_name}",
                f"Seasons: {seasons}",
                f"Stage {stage_num}: {stage_name}",
                f"Duration: {stage.get('duration', '')}",
                "Tasks:",
            ]
            for t in tasks:
                text_parts.append(f"  - {t}")
            if warnings:
                text_parts.append("Warnings:")
                for w in warnings:
                    text_parts.append(f"  ! {w}")
            text = "\n".join(text_parts)
            meta = {
                "source": "crop_roadmaps.json",
                "topic": "crop_lifecycle",
                "crop_id": crop_id,
                "crop_name": crop_name,
                "stage_number": stage_num,
                "stage_name": stage_name,
            }
            chunks.extend(_chunk_text(text, meta))
    return chunks


def load_natural_farming() -> list[dict]:
    """Load natural farming practices as retrieval chunks."""
    data = _load_json("natural_farming.json")
    if not data:
        return []
    chunks = []
    for practice in data.get("practices", []):
        pid = practice.get("id", "unknown")
        name = practice.get("name", {}).get("en", pid)
        text_parts = [
            f"Natural Farming Practice: {name}",
            f"Category: {practice.get('category', '')}",
            f"Description: {practice.get('description', '')}",
        ]
        if "preparation" in practice:
            text_parts.append("Preparation:")
            for p in practice["preparation"]:
                text_parts.append(f"  - {p}")
        if "application" in practice:
            text_parts.append(f"Application: {practice['application']}")
        if "benefits" in practice:
            text_parts.append("Benefits:")
            for b in practice["benefits"]:
                text_parts.append(f"  + {b}")
        if "precautions" in practice:
            text_parts.append("Precautions:")
            for p in practice["precautions"]:
                text_parts.append(f"  ! {p}")
        text = "\n".join(text_parts)
        meta = {
            "source": "natural_farming.json",
            "topic": "natural_farming",
            "practice_id": pid,
            "practice_name": name,
        }
        chunks.extend(_chunk_text(text, meta))
    return chunks


def load_pest_management() -> list[dict]:
    """Load pest and disease management as retrieval chunks."""
    data = _load_json("pest_management.json")
    if not data:
        return []
    chunks = []

    # General IPM principles as a single chunk
    principles = data.get("general_ipm_principles", [])
    if principles:
        text = "General IPM (Integrated Pest Management) Principles:\n" + "\n".join(
            f"  - {p}" for p in principles
        )
        chunks.extend(_chunk_text(text, {
            "source": "pest_management.json",
            "topic": "ipm_principles",
            "crop_id": "general",
        }))

    for crop_entry in data.get("crops", []):
        crop_id = crop_entry.get("crop_id", "unknown")
        crop_name = crop_entry.get("crop_name", crop_id)
        for pd in crop_entry.get("pests_diseases", []):
            pd_name = pd.get("name", "")
            pd_type = pd.get("type", "")
            symptoms = pd.get("symptoms", [])
            ipm = pd.get("ipm_approach", [])
            text_parts = [
                f"Crop: {crop_name}",
                f"Pest/Disease: {pd_name} ({pd_type})",
                f"Symptoms:",
            ]
            for s in symptoms:
                text_parts.append(f"  - {s}")
            text_parts.append(f"Favorable conditions: {pd.get('favorable_conditions', '')}")
            text_parts.append("IPM approach:")
            for i in ipm:
                text_parts.append(f"  - {i}")
            text_parts.append(f"When to seek expert help: {pd.get('when_to_seek_expert', '')}")
            text_parts.append(f"Chemical guidance note: {pd.get('chemical_guidance_note', '')}")
            text = "\n".join(text_parts)
            meta = {
                "source": "pest_management.json",
                "topic": "pest_disease",
                "crop_id": crop_id,
                "crop_name": crop_name,
                "pest_name": pd_name,
            }
            chunks.extend(_chunk_text(text, meta))
    return chunks


def load_farmer_safety() -> list[dict]:
    """Load farmer safety information as retrieval chunks."""
    data = _load_json("farmer_safety.json")
    if not data:
        return []
    chunks = []

    for hazard in data.get("weather_hazards", []):
        hid = hazard.get("id", "unknown")
        name = hazard.get("name", {}).get("en", hid)
        text_parts = [
            f"SAFETY: {name}",
            f"Priority: {hazard.get('priority', '')}",
        ]
        for section, label in [("before", "Before the event"), ("during", "During the event"), ("after", "After the event"), ("practices", "Recommended practices"), ("farmer_health", "Farmer health"), ("crop_protection", "Crop protection")]:
            items = hazard.get(section, [])
            if items:
                text_parts.append(f"{label}:")
                for item in items:
                    text_parts.append(f"  - {item}")
        text = "\n".join(text_parts)
        meta = {
            "source": "farmer_safety.json",
            "topic": "safety",
            "safety_id": hid,
            "safety_name": name,
            "priority": hazard.get("priority", ""),
        }
        chunks.extend(_chunk_text(text, meta))

    for practice in data.get("safety_practices", []):
        pid = practice.get("id", "unknown")
        name = practice.get("name", {}).get("en", pid)
        rules = practice.get("rules", [])
        text_parts = [
            f"SAFETY PRACTICE: {name}",
            f"Priority: {practice.get('priority', '')}",
            "Rules and Guidelines:",
        ]
        for r in rules:
            text_parts.append(f"  - {r}")
        text = "\n".join(text_parts)
        meta = {
            "source": "farmer_safety.json",
            "topic": "safety",
            "safety_id": pid,
            "safety_name": name,
            "priority": practice.get("priority", ""),
        }
        chunks.extend(_chunk_text(text, meta))
    return chunks


# ── master loader ─────────────────────────────────────────────────────────────

def load_all_chunks() -> list[dict]:
    """
    Load all knowledge base files and return a flat list of chunks.
    Each chunk is a dict with 'text' and metadata fields.
    """
    loaders = [
        load_crops,
        load_state_crop_mapping,
        load_crop_roadmaps,
        load_natural_farming,
        load_pest_management,
        load_farmer_safety,
    ]
    all_chunks: list[dict] = []
    for loader in loaders:
        try:
            result = loader()
            all_chunks.extend(result)
            logger.debug("%s loaded %d chunks", loader.__name__, len(result))
        except Exception as exc:
            logger.error("Error loading from %s: %s", loader.__name__, exc)

    logger.info("Total knowledge chunks loaded: %d", len(all_chunks))
    return all_chunks


def get_data_summary() -> dict:
    """Return a summary of loaded data for debugging/display."""
    summary = {}
    for name, loader in [
        ("crops", load_crops),
        ("state_mapping", load_state_crop_mapping),
        ("roadmaps", load_crop_roadmaps),
        ("natural_farming", load_natural_farming),
        ("pest_management", load_pest_management),
        ("safety", load_farmer_safety),
    ]:
        try:
            chunks = loader()
            summary[name] = len(chunks)
        except Exception:
            summary[name] = 0
    return summary
