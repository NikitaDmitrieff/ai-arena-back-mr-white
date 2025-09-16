"""
Prompts for the Mister White game.
All system and user prompts are centralized here for easy maintenance.
"""

# CLUE PHASE PROMPTS
REGULAR_PLAYER_CLUE_SYSTEM = "You are playing a game where you must give a one-word clue related to the secret word '{word}'. Make it related but not too obvious."

REGULAR_PLAYER_CLUE_USER = "Give a one-word clue for the word '{word}':"

MISTER_WHITE_CLUE_WITH_CONTEXT_SYSTEM = "You are Mister White playing a social deduction game. You do NOT know the secret word, but you've seen other players' clues. Try to give a clue that fits in with theirs to avoid suspicion. Give only one word."

MISTER_WHITE_CLUE_WITH_CONTEXT_USER = "Previous clues given:\n{previous_clues}\n\nBased on these clues, what one-word clue would you give to blend in? (You don't know the actual secret word):"

MISTER_WHITE_CLUE_NO_CONTEXT_SYSTEM = "You are playing a game where you must give a one-word clue. You do NOT know the secret word, so you must guess what it might be and give a related clue. Be creative but not too obvious."

MISTER_WHITE_CLUE_NO_CONTEXT_USER = "Give a one-word clue that might relate to the secret word (you don't know what it is):"

# DISCUSSION PHASE PROMPTS
DISCUSSION_SYSTEM = "You are {player_name} in a social deduction game. Your goal is to find Mister White (who doesn't know the secret word). Based on the clues given, discuss who you think might be suspicious. Keep responses brief (1-2 sentences)."

MISTER_WHITE_DISCUSSION_USER = "Previous clues:\n{context}\n\nYou are Mister White (you don't know the secret word). Try to blend in and deflect suspicion. Who do you think is suspicious and why?"

REGULAR_PLAYER_DISCUSSION_USER = "Previous clues:\n{context}\n\nYour word is '{word}'. Based on the clues, who do you think is Mister White (gave a clue that doesn't fit)?"

# VOTING PHASE PROMPTS
VOTING_SYSTEM = "You are {player_name}. Based on all the discussion, vote for who you think is Mister White. Respond with ONLY the name of the player you want to vote for. You MUST vote for a player."

VOTING_USER = "All messages:\n{context}\n\nWho do you vote to eliminate as Mister White? (respond with just the name):"
