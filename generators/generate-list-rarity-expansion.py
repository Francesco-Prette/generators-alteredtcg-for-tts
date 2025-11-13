import os
import re
import json
from collections import defaultdict

# === CONFIGURATION ===
MAIN_FOLDER = r"C:\Users\BlackKey\repos\databases"  # 👈 folder with all the input JSON files
OUTPUT_FOLDER = r"C:\Users\BlackKey\repos\generators-alteredtcg-for-tts\generated-cards\full-list"  # 👈 output folder for the rarity files

# Regex to find the English image URL
URL_PATTERN = re.compile(
    r'https://altered-prod-eu\.s3\.amazonaws\.com/Art/[A-Za-z0-9_/-]+/JPG/en_US/[a-f0-9]+\.jpg'
)

RARITY_TO_FILENAME = {
    "COMMON": "commons.json",
    "RARE": "rare.json",
    "UNIQUE": "unique.json",
}

CARDTYPE_TO_FILENAME = {
    "HERO": "heroes.json",
    "TOKEN CHARACTER": "tokens.json",
}

# =========================
#   HELPER FUNCTIONS
# =========================
def extract_face_url(text):
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None

def get_field(data, path, default=None):
    """Helper to safely get nested dict fields."""
    cur = data
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur

def get_rarity(data):
    return get_field(data, ["rarity", "name"], "").strip().upper()

def get_card_name(data):
    return data.get("name", "").strip()

def get_faction(data):
    return get_field(data, ["mainFaction", "name"], "Unknown").strip()

def get_expansion(data):
    return get_field(data, ["cardSet", "name"], "Unknown").strip()

def get_card_id(data):
    return data.get("id", "")

def get_card_type(data):
    return get_field(data, ["cardType", "name"], "").strip()

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)

def save_expansion_files(expansion, data_dict):
    """Write the rarity and card type files for a single expansion."""
    expansion_folder = os.path.join(OUTPUT_FOLDER, sanitize_filename(expansion))
    os.makedirs(expansion_folder, exist_ok=True)

    # Rarity files
    for rarity, cards in data_dict["rarities"].items():
        filename = RARITY_TO_FILENAME[rarity]
        out_file = os.path.join(expansion_folder, filename)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)
        print(f"✅ {expansion}/{filename} ({len(cards)} cards)")

    # Hero & Token files
    for ctype, cards in data_dict["types"].items():
        filename = CARDTYPE_TO_FILENAME[ctype]
        out_file = os.path.join(expansion_folder, filename)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)
        print(f"✅ {expansion}/{filename} ({len(cards)} cards)")


# =========================
#   MAIN SCRIPT
# =========================
def main():
    total_cards = 0
    skipped_no_url = 0
    skipped_no_rarity = 0

    current_expansion = None
    expansion_data = {"rarities": defaultdict(list), "types": defaultdict(list)}

    # Sort files so expansions are processed in order
    for root, _, files in os.walk(MAIN_FOLDER):
        for filename in sorted(files):
            if not filename.lower().endswith(".json"):
                continue

            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    continue

                face_url = extract_face_url(text)
                if not face_url:
                    skipped_no_url += 1
                    continue

                rarity = get_rarity(data)
                cardtype = get_card_type(data).upper()
                expansion = get_expansion(data)

                # If we detect a new expansion, save the old one first
                if current_expansion and expansion != current_expansion:
                    save_expansion_files(current_expansion, expansion_data)
                    expansion_data = {"rarities": defaultdict(list), "types": defaultdict(list)}

                current_expansion = expansion

                card_info = {
                    "rarity": rarity.title(),
                    "name": get_card_name(data),
                    "faction": get_faction(data),
                    "id": get_card_id(data),
                    "cardtype": cardtype.title(),
                    "faceurl": face_url,
                    "expansion": expansion,
                }

                # Separate hero & token cards
                if cardtype in CARDTYPE_TO_FILENAME:
                    expansion_data["types"][cardtype].append(card_info)
                elif rarity in RARITY_TO_FILENAME:
                    expansion_data["rarities"][rarity].append(card_info)
                else:
                    skipped_no_rarity += 1
                    continue

                total_cards += 1

            except Exception as e:
                print(f"[WARN] Error parsing {file_path}: {e}")

    # Save the last expansion after the loop
    if current_expansion:
        save_expansion_files(current_expansion, expansion_data)

    print("\n====== SUMMARY ======")
    print(f"✅ Total cards exported: {total_cards}")
    print(f"🚫 Skipped (no URL): {skipped_no_url}")
    print(f"🚫 Skipped (no/invalid rarity): {skipped_no_rarity}")
    print(f"📂 Output root: {os.path.abspath(OUTPUT_FOLDER)}")


if __name__ == "__main__":
    main()
