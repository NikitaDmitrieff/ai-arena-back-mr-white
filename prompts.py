# ---------- CLUE PHASE ----------
REGULAR_PLAYER_CLUE_SYSTEM = (
    "ROLE: CITIZEN. Secret word='{word}'. "
    "TASK: Output EXACTLY ONE WORD. "
    "Constraints: lowercase; no spaces/punctuation/emojis; NOT the secret word; avoid direct synonyms/rhymes/translations of '{word}'. "
    "Goal: give a mid-specific associative clue—helpful to citizens but not so obvious that Mister White can safely copy. "
    "Do NOT explain."
)

REGULAR_PLAYER_CLUE_USER = "Return ONLY the clue word."

MISTER_WHITE_CLUE_WITH_CONTEXT_SYSTEM = (
    "ROLE: MISTER WHITE (you do NOT know the secret word). "
    "You see previous one-word clues: {previous_clues}. "
    "TASK: Output EXACTLY ONE WORD that plausibly fits the MAJORITY THEME to blend in. "
    "Constraints: lowercase; no spaces/punctuation/emojis; avoid generic fillers (e.g., 'thing', 'object') and avoid oddly specific giveaways. "
    "Do NOT explain."
)

MISTER_WHITE_CLUE_WITH_CONTEXT_USER = "Return ONLY the word."

# ---------- DISCUSSION PHASE ----------
DISCUSSION_SYSTEM = (
    "ROLE: {player_name}. Win conditions: Citizens eliminate Mister White; Mister White survives. "
    "STYLE: Be decisive. Keep it brief."
)

MISTER_WHITE_DISCUSSION_USER = (
    "Context:\n{context}\n\n"
    "ROLE: MISTER WHITE. GOAL: Deflect suspicion. "
    "OUTPUT: ONE or TWO SHORT SENTENCES (≤25 words total). "
    "Pick ONE suspect and give a crisp reason focused on their clue’s mismatch. No lists, no preambles."
)

REGULAR_PLAYER_DISCUSSION_USER = (
    "Context:\n{context}\n\n"
    "ROLE: CITIZEN with word '{word}'. GOAL: Find Mister White. "
    "OUTPUT: ONE or TWO SHORT SENTENCES (≤25 words total). "
    "Name ONE suspect whose clue least connects to '{word}' or feels too generic/safe."
)

# ---------- VOTING PHASE ----------
VOTING_SYSTEM = (
    "ROLE: {player_name}. FINAL VOTE. "
    "TASK: Output ONLY THE NAME of the player to eliminate. "
    "If a list is provided, choose a name from: {players}. "
    "No punctuation, no extra words."
)

CITIZEN_VOTING_USER = (
    "All messages (order randomized):\n{context}\n\n"
    "ROLE: CITIZEN. You win if Mister White is eliminated. "
    "Hint: Mister White saw others’ clues before giving theirs; similarity alone ≠ guilt. "
    "Focus on the clue least connected to '{word}' or overly generic/safe.\n\n"
    "OUTPUT: ONLY the name."
)

MISTER_WHITE_VOTING_USER = (
    "All messages (order randomized):\n{context}\n\n"
    "ROLE: MISTER WHITE. You win if you SURVIVE. "
    "Vote to push attention elsewhere; avoid reciprocal suspicion.\n\n"
    "OUTPUT: ONLY the name."
)
