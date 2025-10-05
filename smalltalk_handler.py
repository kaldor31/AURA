#created: 2025/10/05 20:39:31
#last-modified: 2025/10/05 20:51:20
#by kaldor31

import json
import random
from typing import Optional

# File with responses
DATA_FILE = "smalltalk_data.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    SMALLTALK_RESPONSES = json.load(f)

def detect_smalltalk(text: str) -> Optional[str]:
    """
    Checks whether the message is a domestic question.
    Returns a random response or None if not found.
    """
    text_lower = text.lower()
    for key, answers in SMALLTALK_RESPONSES.items():
        if key in text_lower:
            return random.choice(answers)
    return None