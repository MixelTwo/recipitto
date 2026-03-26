import re
import unicodedata
from typing import cast

from transliterate import translit  # pyright: ignore[reportUnknownVariableType]


def normalize_for_search(text: str):
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = cast(str, translit(text, "ru", reversed=True))
    text = re.sub(r"[^\w\s]", "", text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text
