"""
escalation.py — Tier 3 human escalation (the "support-level" of "multilevel").

When retrieval confidence is low (query out of scope) we do NOT let the model
guess. We return a localised message pointing the farmer to a human expert:
their local APCNF/RySS CRP, the Kisan Call Centre, or the nearest KVK.

This mirrors Digital Green's Farmer.Chat human-in-the-loop safety design.
"""

from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CONTACTS

_ESCALATION = {
    "te": (
        "క్షమించండి, ఈ ప్రశ్నకు నాకు ఖచ్చితమైన సమాచారం లేదు. తప్పు సలహా ఇవ్వడం కంటే "
        "దయచేసి మీ గ్రామ/మండల RySS సహజ వ్యవసాయ సహాయకుడిని (CRP) అడగండి, లేదా "
        "కిసాన్ కాల్ సెంటర్ {kcc}కు ఫోన్ చేయండి ({hours})."
    ),
    "hi": (
        "माफ़ कीजिए, इस सवाल की पक्की जानकारी मेरे पास नहीं है। ग़लत सलाह देने के बजाय "
        "कृपया अपने गाँव/मंडल के RySS प्राकृतिक खेती सहायक (CRP) से पूछें, या "
        "किसान कॉल सेंटर {kcc} पर फ़ोन करें ({hours})।"
    ),
    "en": (
        "I'm not fully sure about this one, and I won't guess. Please ask your village/mandal "
        "RySS Community Resource Person (CRP), or call the Kisan Call Centre at {kcc} ({hours})."
    ),
}


def escalation_message(language_code: str) -> str:
    template = _ESCALATION.get(language_code, _ESCALATION["en"])
    return template.format(kcc=CONTACTS["kisan_call_centre"], hours=CONTACTS["kcc_hours"])


def should_escalate(retrieval: dict) -> bool:
    """Escalate when retrieval was not confident (no good matching context)."""
    return not retrieval.get("confident", False)
