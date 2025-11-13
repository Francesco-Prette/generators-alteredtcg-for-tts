import os
import json
import random
from pathlib import Path

# ==========================
# CONFIGURATION
# ==========================
EXPANSION_FOLDER = r"C:\Users\BlackKey\repos\generators-alteredtcg-for-tts\generated-cards\full-list\Trial by Frost"
OUTPUT_FOLDER = r"C:\Users\BlackKey\repos\generators-alteredtcg-for-tts\generated-cards\boosters"
BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2126321478353027369/C6ACE60B566C3C650B1865C2C6FF7C23712E3C61/"

PACK_SIZE = {
    "hero": 1,
    "common": 8,
    "rare": 3,
    "token": 1
}
UNIQUE_CHANCE = 1 / 8  # 1 in 8 chance to replace a rare

# ==========================
# HELPERS
# ==========================
def load_cards(file_name):
    file_path = os.path.join(EXPANSION_FOLDER, file_name)
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_random(cards, n):
    return random.sample(cards, min(len(cards), n)) if cards else []

# ==========================
# MAIN BOOSTER CREATION
# ==========================
def create_pack(deck_num_start, hero_cards, common_cards, rare_cards, unique_cards, token_cards):
    # pick cards for this booster
    hero_pick = pick_random(hero_cards, PACK_SIZE["hero"])
    common_pick = pick_random(common_cards, PACK_SIZE["common"])

    # handle rare/unique chance
    rare_pick = pick_random(rare_cards, PACK_SIZE["rare"])
    if unique_cards and random.random() < UNIQUE_CHANCE:
        # replace a random rare with a unique card
        idx_to_replace = random.randrange(len(rare_pick)) if rare_pick else 0
        unique_card = pick_random(unique_cards, 1)
        if unique_card:
            if rare_pick:
                rare_pick[idx_to_replace] = unique_card[0]
            else:
                rare_pick.append(unique_card[0])

    token_pick = pick_random(token_cards, PACK_SIZE["token"])

    # combine all cards for deck
    all_cards = hero_pick + common_pick + rare_pick + token_pick
    random.shuffle(all_cards)

    deck_ids = []
    contained_objects = []
    custom_deck = {}

    for idx, card in enumerate(all_cards):
        deck_num = deck_num_start + idx
        card_id = deck_num * 100

        # Register in DeckIDs
        deck_ids.append(card_id)

        # Register in CustomDeck
        custom_deck[str(deck_num)] = {
            "FaceURL": card["faceurl"],
            "BackURL": BACK_URL,
            "NumWidth": 1,
            "NumHeight": 1,
            "BackIsHidden": True,
            "UniqueBack": False,
            "Type": 0
        }

        # Register contained object
        contained_objects.append({
            "GUID": f"{deck_num:06x}"[-6:],
            "Name": "CardCustom",
            "Transform": {
                "posX": 16.79,
                "posY": 1.47,
                "posZ": 10.13,
                "rotX": 0.017,
                "rotY": 180.0,
                "rotZ": 0.079,
                "scaleX": 1.0,
                "scaleY": 1.0,
                "scaleZ": 1.0
            },
            "Nickname": card["name"],
            "Description": f"{card['rarity']} - {card['cardtype']}",
            "GMNotes": "",
            "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
            "ColorDiffuse": {"r": 0.713235259, "g": 0.713235259, "b": 0.713235259},
            "LayoutGroupSortIndex": 0,
            "Value": 0,
            "Locked": False,
            "Grid": True,
            "Snap": True,
            "IgnoreFoW": False,
            "MeasureMovement": False,
            "DragSelectable": True,
            "Autoraise": True,
            "Sticky": True,
            "Tooltip": True,
            "GridProjection": False,
            "HideWhenFaceDown": True,
            "Hands": True,
            "CardID": card_id,
            "SidewaysCard": False,
            "CustomDeck": {
                str(deck_num): custom_deck[str(deck_num)]
            },
            "LuaScript": "",
            "LuaScriptState": "",
            "XmlUI": ""
        })

    deck_object = {
        "GUID": "699f2d",
        "Name": "Deck",
        "Transform": {
            "posX": 16.79,
            "posY": 1.49,
            "posZ": 10.13,
            "rotX": 0.017,
            "rotY": 180.0,
            "rotZ": 0.079,
            "scaleX": 1.0,
            "scaleY": 1.0,
            "scaleZ": 1.0
        },
        "Nickname": "Booster Pack",
        "Description": "",
        "GMNotes": "",
        "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
        "ColorDiffuse": {"r": 0.713235259, "g": 0.713235259, "b": 0.713235259},
        "LayoutGroupSortIndex": 0,
        "Value": 0,
        "Locked": False,
        "Grid": True,
        "Snap": True,
        "IgnoreFoW": False,
        "MeasureMovement": False,
        "DragSelectable": True,
        "Autoraise": True,
        "Sticky": True,
        "Tooltip": True,
        "GridProjection": False,
        "HideWhenFaceDown": True,
        "Hands": False,
        "SidewaysCard": False,
        "DeckIDs": deck_ids,
        "CustomDeck": custom_deck,
        "LuaScript": "",
        "LuaScriptState": "",
        "XmlUI": "",
        "ContainedObjects": contained_objects
    }

    save_object = {
        "SaveName": "",
        "Date": "",
        "VersionNumber": "",
        "GameMode": "",
        "GameType": "",
        "GameComplexity": "",
        "Tags": [],
        "Gravity": 0.5,
        "PlayArea": 0.5,
        "Table": "",
        "Sky": "",
        "Note": "",
        "TabStates": {},
        "LuaScript": "",
        "LuaScriptState": "",
        "XmlUI": "",
        "ObjectStates": [deck_object]
    }

    return save_object

# ==========================
# ENTRY POINT
# ==========================
def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    hero_cards = load_cards("heroes.json")
    common_cards = load_cards("commons.json")
    rare_cards = load_cards("rare.json")
    unique_cards = load_cards("unique.json")
    token_cards = load_cards("token.json")

    num_packs = int(input("How many booster packs to generate? "))

    deck_num_start = 11110
    for pack_index in range(num_packs):
        booster_data = create_pack(
            deck_num_start + pack_index * 1000,  # unique base per pack
            hero_cards,
            common_cards,
            rare_cards,
            unique_cards,
            token_cards
        )

        output_file = Path(OUTPUT_FOLDER) / f"booster_pack_{pack_index+1}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(booster_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Generated: {output_file}")

    print(f"\n✨ Finished generating {num_packs} packs in:\n📂 {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()
