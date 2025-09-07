from typing import TypedDict


class Colors:
    class List:
        lightred = [255, 75, 75, 255]

    class Str:
        lightred = "#ff4b4b"


class CollectType(TypedDict):
    fr: str
    en: str
    short: str


class SessionState(TypedDict):
    limit: int | None
    selected_collection: list
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
