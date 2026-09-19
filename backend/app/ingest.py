import re
from datetime import datetime
from typing import Optional, Dict

PATTERN = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$")
LETTER_SLOT_CONFUSIONS = {'0':'O', '1':'I', '8':'B', '5':'S', '2':'Z', '6':'G'}
DIGIT_SLOT_CONFUSIONS  = {'O':'0', 'I':'1', 'B':'8', 'S':'5', 'Z':'2', 'G':'6'}

def repair_plate(plate: str) -> tuple[Optional[str], bool]:
    """Attempts to repair a plate. Returns (repaired_plate or None if unrecoverable, was_repaired)."""
    if PATTERN.match(plate):
        return plate, False
        
    # It didn't match. We can try all combinations of 1-character fixes using the confusion maps
    # and see if any results in a valid plate. But simpler: apply fixes slot-by-slot according to format?
    # Format: 2 letters, 1-2 digits, 1-3 letters, 4 digits.
    # The prompt says: apply in a slot-aware way (a digit slot only becomes another digit, a letter slot only becomes another letter).
    # Since the structure is fixed except for the variable length parts, we can just try all single-char substitutions
    # and if exactly one valid plate comes out, we use it. If multiple, we can't be sure, but we can just pick the first.
    
    # Actually, let's just try single substitutions using BOTH maps, and see if it passes PATTERN.
    possible_fixes = []
    plate_list = list(plate)
    for i, char in enumerate(plate_list):
        if char in LETTER_SLOT_CONFUSIONS:
            temp = list(plate_list)
            temp[i] = LETTER_SLOT_CONFUSIONS[char]
            cand = "".join(temp)
            if PATTERN.match(cand):
                possible_fixes.append(cand)
        if char in DIGIT_SLOT_CONFUSIONS:
            temp = list(plate_list)
            temp[i] = DIGIT_SLOT_CONFUSIONS[char]
            cand = "".join(temp)
            if PATTERN.match(cand):
                possible_fixes.append(cand)
                
    if possible_fixes:
        # If we found at least one valid fix, return the first one.
        return possible_fixes[0], True
        
    return None, False

def should_dedup(event1: Dict, event2: Dict) -> bool:
    """Returns True if event2 is a duplicate of event1 (same plate, same node, within 5 seconds)."""
    if event1["plate_normalized"] != event2["plate_normalized"]:
        return False
    if event1["node_id"] != event2["node_id"]:
        return False
        
    t1 = datetime.fromisoformat(event1["timestamp"])
    t2 = datetime.fromisoformat(event2["timestamp"])
    diff = abs((t2 - t1).total_seconds())
    return diff <= 5.0
