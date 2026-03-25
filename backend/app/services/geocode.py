import re
from typing import Optional, Tuple
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="news-intelligence-dashboard")

KNOWN_PREFIXES = [
    "in ", "near ", "from ", "at ", "outside ", "across ", "inside ",
]


def extract_location_candidate(text: str) -> Optional[str]:
    if not text:
        return None

    lowered = text.strip()
    for prefix in KNOWN_PREFIXES:
        idx = lowered.lower().find(prefix)
        if idx >= 0:
            candidate = lowered[idx + len(prefix):].split(",")[0].split(".")[0].strip()
            if len(candidate) > 2:
                return candidate

    match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", text)
    return match.group(1) if match else None


def geocode_location(location_name: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    if not location_name:
        return None, None
    try:
        result = geolocator.geocode(location_name, timeout=10)
        if result:
            return result.latitude, result.longitude
    except Exception:
        return None, None
    return None, None