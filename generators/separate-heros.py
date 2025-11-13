import json
import os

# Root folder containing expansion subfolders
INPUT_FOLDER = r"C:\Users\BlackKey\repos\generators-alteredtcg-for-tts\generated-cards\full-list"

def main():
    # Loop through subfolders (each expansion)
    for expansion_name in os.listdir(INPUT_FOLDER):
        expansion_path = os.path.join(INPUT_FOLDER, expansion_name)
        if not os.path.isdir(expansion_path):
            continue  # skip files, only process folders

        # Find JSON file in the expansion folder
        source_file = None
        for filename in os.listdir(expansion_path):
            if filename.endswith(".json"):
                source_file = os.path.join(expansion_path, filename)
                break
        if not source_file:
            continue  # no JSON found in this folder

        # Load cards from the file
        with open(source_file, "r", encoding="utf-8") as f:
            cards = json.load(f)

        # Separate heroes and non-heroes
        heroes = [c for c in cards if c.get("cardtype") == "Hero"]
        others = [c for c in cards if c.get("cardtype") != "Hero"]

        # Build output file paths inside the same folder
        hero_file = os.path.join(expansion_path, "heroes.json")
        others_file = os.path.join(expansion_path, "non_heroes.json")

        # Save hero cards
        with open(hero_file, "w", encoding="utf-8") as f:
            json.dump(heroes, f, ensure_ascii=False, indent=2)

        # Save non-hero cards
        with open(others_file, "w", encoding="utf-8") as f:
            json.dump(others, f, ensure_ascii=False, indent=2)

        print(f"✅ {expansion_name}: {len(heroes)} heroes, {len(others)} non-heroes saved.")

    print("\n✨ All expansions processed successfully.")

if __name__ == "__main__":
    main()
