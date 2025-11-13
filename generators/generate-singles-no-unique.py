import os
import re
import json
from datetime import datetime

# === CONFIGURATION ===
MAIN_FOLDER = r"<<repo of the databases>>"  # 👈 folder with all the input JSON files
OUTPUT_FOLDER = r"<<folder until>>\generated-cards\singles"                # root output folder for generated TTS JSONs
BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2126321478353027369/C6ACE60B566C3C650B1865C2C6FF7C23712E3C61/"

# Regex to find the English image URL
URL_PATTERN = re.compile(
    r'https://altered-prod-eu\.s3\.amazonaws\.com/Art/[A-Za-z0-9_/-]+/JPG/en_US/[a-f0-9]+\.jpg'
)

# =========================
#   JSON TEMPLATE BUILDER
# =========================
def make_tts_card(face_url, card_name, rarity):
    """Return a Tabletop Simulator JSON card object with given face image URL, name, and rarity."""
    nickname = f"{card_name} ({rarity})" if rarity else card_name
    return {
        "SaveName": "",
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        "ObjectStates": [
            {
                "GUID": "cff041",
                "Name": "CardCustom",
                "Transform": {
                    "posX": 16.42998,
                    "posY": 1.47420466,
                    "posZ": 6.777185,
                    "rotX": 0.0168644264,
                    "rotY": 180.004868,
                    "rotZ": 0.07987778,
                    "scaleX": 1.0,
                    "scaleY": 1.0,
                    "scaleZ": 1.0,
                },
                "Nickname": nickname,
                "Description": "",
                "GMNotes": "",
                "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
                "ColorDiffuse": {
                    "r": 0.713235259,
                    "g": 0.713235259,
                    "b": 0.713235259,
                },
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
                "CardID": 1083500,
                "SidewaysCard": False,
                "CustomDeck": {
                    "10835": {
                        "FaceURL": face_url,
                        "BackURL": BACK_URL,
                        "NumWidth": 1,
                        "NumHeight": 1,
                        "BackIsHidden": True,
                        "UniqueBack": False,
                        "Type": 0,
                    }
                },
                "LuaScript": "",
                "LuaScriptState": "",
                "XmlUI": "",
            }
        ],
    }


# =========================
#   HELPER FUNCTIONS
# =========================

def is_unique_card(data):
    """Return True if card rarity is 'Unique'."""
    rarity = data.get("rarity")
    if isinstance(rarity, dict):
        name = rarity.get("name", "").strip().lower()
        ref = rarity.get("reference", "").strip().lower()
        if name == "unique" or ref == "unique":
            return True
    return False


def get_rarity(data):
    """Extract rarity name (e.g. 'Common', 'Rare')."""
    rarity = data.get("rarity")
    if isinstance(rarity, dict):
        return rarity.get("name", "").strip().title()
    return ""


def get_faction_name(data):
    """Extract main faction name."""
    faction = data.get("mainFaction")
    if isinstance(faction, dict):
        name = faction.get("name")
        if name:
            return name.strip().replace(" ", "_")
    return "Unknown"


def get_expansion_name(data):
    """Extract expansion / cardSet name."""
    card_set = data.get("cardSet")
    if isinstance(card_set, dict):
        name = card_set.get("name")
        if name:
            return name.strip().replace(" ", "_")
    return "Unknown_Set"


def get_card_name(data):
    """Extract card name."""
    return data.get("name", "Unnamed Card").strip()


def extract_face_url(text):
    """Extract first en_US image URL from the JSON text."""
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


def sanitize_filename(name):
    """Remove illegal characters for file names."""
    return re.sub(r'[<>:"/\\|?*]', "_", name)


# =========================
#   MAIN SCRIPT
# =========================
def main():
    total = 0
    skipped_unique = 0
    skipped_no_url = 0

    for root, _, files in os.walk(MAIN_FOLDER):
        for name in files:
            if not name.lower().endswith(".json"):
                continue

            file_path = os.path.join(root, name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = {}

                # Skip "Unique" cards
                if is_unique_card(data):
                    skipped_unique += 1
                    continue

                face_url = extract_face_url(text)
                if not face_url:
                    skipped_no_url += 1
                    continue

                faction_name = get_faction_name(data)
                expansion_name = get_expansion_name(data)
                card_name = get_card_name(data)
                rarity = get_rarity(data)
                safe_name = sanitize_filename(f"{card_name} ({rarity})" if rarity else card_name)

                # Create nested output folder: expansion/faction
                out_folder = os.path.join(OUTPUT_FOLDER, expansion_name, faction_name)
                os.makedirs(out_folder, exist_ok=True)

                # Create TTS JSON
                card_json = make_tts_card(face_url, card_name, rarity)

                out_path = os.path.join(out_folder, f"{safe_name}.json")
                with open(out_path, "w", encoding="utf-8") as out:
                    json.dump(card_json, out, indent=2, ensure_ascii=False)

                print(f"✅ {expansion_name}/{faction_name}: {card_name} ({rarity})")
                total += 1

            except Exception as e:
                print(f"[WARN] Failed to process {file_path}: {e}")

    print("\n====== SUMMARY ======")
    print(f"✅ Created: {total} JSON card files")
    print(f"🚫 Skipped Unique cards: {skipped_unique}")
    print(f"🚫 Skipped (no URL): {skipped_no_url}")
    print(f"Output root: {os.path.abspath(OUTPUT_FOLDER)}")


if __name__ == "__main__":
    main()
