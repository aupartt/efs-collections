from typing import TypedDict


class Colors:
    class List:
        primary = [255, 75, 75, 255]
        secondary = [255, 165, 75, 255]
        tertiary = [255, 75, 165, 255]

    class Str:
        primary = "#FF4B4B"
        secondary = "#FFA54B"
        tertiary = "#FF4BA5"
        lightred = "#ff9898"
        red = "#FF4B4B"
        darkred = "#d23939"


class CollectType(TypedDict):
    fr: str
    en: str
    short: str


class SessionState(TypedDict):
    limit: int | None
    selected_collection: int | None
    selected_event: int | None
    collect_types: dict[str, CollectType]


ST_SESSION_STATE: SessionState = {
    "limit": None,
    "selected_collection": None,
    "selected_event": None,
    "collect_types": {
        "blood": {"fr": "sang", "en": "blood", "short": "st"},
        "plasma": {"fr": "plasma", "en": "plasma", "short": "pla"},
        "platelet": {"fr": "plaquette", "en": "platelet", "short": "cpa"},
    },
}
