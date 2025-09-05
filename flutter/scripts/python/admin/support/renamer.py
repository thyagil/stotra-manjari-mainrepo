#!/usr/bin/env python3
import re
from pathlib import Path

# === CONFIG ===
CHAPTER_REGEX = r"Sarga\s+(\d{1,3})"   # capture 1–3 digit number (adjust if needed)
EXT = ".txt"


def rename(input_dir):
    for f in sorted(input_dir.glob(f"*{EXT}")):
        match = re.search(CHAPTER_REGEX, f.stem)
        if not match:
            print(f"⚠️ Skipping (no chapter number found): {f.name}")
            continue

        chap_num = int(match.group(1))
        new_name = f"chapter{chap_num:03d}{EXT}"
        new_path = f.with_name(new_name)

        if new_path.exists():
            print(f"⚠️ Skipping (already exists): {new_path.name}")
            continue

        print(f"🔄 {f.name} → {new_name}")
        f.rename(new_path)

    print("✅ Renaming complete.")

def main():
    langs = ["sa_bt", "be", "ka", "gu", "te", "ma", "en"]
    input_dir_root = "/Volumes/WORKBENCH/assets/projects/sgp_srimad_ramayanam/content/volume01/"
    for lang in langs:
        input_dir = Path(input_dir_root) / lang
        if not input_dir.exists():
            print(f"❌ Directory not found: {input_dir}")
            return
        else:
            rename(input_dir)


if __name__ == "__main__":
    main()
