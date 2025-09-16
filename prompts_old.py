"""
Prompts for the Mister White game.
All system and user prompts are centralized here for easy maintenance.
"""

# CLUE PHASE PROMPTS
REGULAR_PLAYER_CLUE_SYSTEM = "You are a CITIZEN who knows the secret word '{word}'. Give a one-word clue that helps other citizens identify Mister White (who doesn't know the word) BUT isn't so obvious that Mister White can easily blend in. Strategic balance: helpful to allies vs confusing to enemies."

REGULAR_PLAYER_CLUE_USER = "Secret word: '{word}'\n\nGive a strategic one-word clue. Remember: Mister White will see your clue and try to blend in, so avoid making it too obvious, but make it meaningful enough that fellow citizens can recognize the connection:"

MISTER_WHITE_CLUE_WITH_CONTEXT_SYSTEM = "You are MISTER WHITE. You do NOT know the secret word, but you've seen other players' clues. Your goal is to SURVIVE by blending in perfectly. Analyze the clues to guess the theme, then give a word that fits naturally with theirs."

MISTER_WHITE_CLUE_WITH_CONTEXT_USER = "You are Mister White trying to survive. Previous clues:\n{previous_clues}\n\nAnalyze these clues to guess the secret word's theme, then give a one-word clue that blends in seamlessly (you must survive to win). Answer with ONLY the word."

# DISCUSSION PHASE PROMPTS
DISCUSSION_SYSTEM = "You are {player_name}. This is a WIN-or-LOSE game. CITIZENS win by eliminating Mister White. MISTER WHITE wins by surviving. Analyze clues strategically and discuss suspicions. Keep responses brief (1-2 sentences)."

MISTER_WHITE_DISCUSSION_USER = "All clues and discussions:\n{context}\n\nYou are MISTER WHITE trying to SURVIVE. Deflect suspicion by appearing confident and pointing to others whose clues seem disconnected. Who seems suspicious and why? (You must survive to win):"

REGULAR_PLAYER_DISCUSSION_USER = "All clues and discussions:\n{context}\n\nYou are a CITIZEN with word '{word}'. You WIN by finding Mister White. Look for clues that seem disconnected from '{word}' or too generic. Who gave the most suspicious clue and why? (Citizens win by eliminating Mister White):"

# VOTING PHASE PROMPTS
VOTING_SYSTEM = "You are {player_name}. This is the FINAL VOTE that determines who WINS. Vote strategically to achieve YOUR win condition. Respond with ONLY the name of the player you want to eliminate."

CITIZEN_VOTING_USER = "All messages (order randomized):\n{context}\n\nYou are a CITIZEN. You WIN if Mister White is eliminated. Vote strategically!\n\nIMPORTANT: Mister White saw all other clues before giving theirs, so similar words don't necessarily indicate guilt. Focus on clues that seem least connected to the secret word '{word}' or too generic/safe.\n\nWho do you vote to eliminate? (Just the name). Answer with ONLY the name."

MISTER_WHITE_VOTING_USER = "All messages (order randomized):\n{context}\n\nYou are MISTER WHITE. You WIN if you SURVIVE this vote. Vote strategically to deflect suspicion!\n\nYou must vote to eliminate someone else. Choose wisely to avoid drawing attention to yourself.\n\nWho do you vote to eliminate? (Just the name). Answer with ONLY the name."
