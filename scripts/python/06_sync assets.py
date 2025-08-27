#!/usr/bin/env python3
import os, re, shutil, sys
from pathlib import Path
from projects.ramayanam_sriramghanapatigal import folders

# === CONFIGURATION ===
def sync_assets(root, project_code: str, volume: int, langs=[],
                sync_content=True, sync_audio=True,
                sync_durations=True, sync_meanings=True):
    # --- META ---
    SRC_AUDIO = Path(folders[volume].FLDR_AUDIO_FINAL)
    SRC_DURATIONS = Path(folders[volume].FLDR_DURATIONS)

    # --- DESTINATION ROOT ---
    TARGET = Path(f"{root}{project_code}/volumes/volume{volume:02d}/chapters")
    TARGET.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Syncing {project_code} (Volume {volume}) into assets...")

    # --- Iterate over languages ---
    for lang in langs:
        # handle sa special-case
        if lang == "sa":
            folders[volume].lang = "sa_bt"
            SRC_CONTENT = Path(folders[volume].FLDR_CONTENT_FINAL)
            lang = "sa"
        else:
            folders[volume].lang = lang
            SRC_CONTENT = Path(folders[volume].FLDR_CONTENT_FINAL)

        SRC_MEANINGS = Path(folders[volume].FLDR_MEANINGS if hasattr(folders[volume], "FLDR_MEANINGS") else folders[volume].FLDR_DURATIONS)

        for file in sorted(SRC_CONTENT.glob("RAM_Kanda *_Sarga *.txt")):
            fname = file.name
            try:
                chapter_num = int(fname.split("Sarga")[1].split(".")[0].strip())
            except Exception:
                print(f"⚠️ Could not parse chapter number from {fname}")
                continue

            chapter_num_padded = f"{chapter_num:02d}"
            chapter_dir = TARGET / f"chapter{chapter_num_padded}"
            (chapter_dir / "lang" / lang).mkdir(parents=True, exist_ok=True)

            print(f"📖 Processing Chapter {chapter_num_padded} ({lang})")

            # === VERSES ===
            if sync_content:
                shutil.copy2(file, chapter_dir / "lang" / lang / "verses.txt")

            # === MEANINGS ===
            if sync_meanings:
                meanings_file = SRC_MEANINGS / f"RAM_Kanda {volume}_Sarga {chapter_num}.txt"
                if meanings_file.exists():
                    shutil.copy2(meanings_file, chapter_dir / "lang" / lang / "meanings.txt")
                else:
                    print(f"⚠️ No meanings found for Chapter {chapter_num_padded}")

            # === DURATIONS ===
            if sync_durations:
                dur_file = f"{chapter_num:03d}"
                pattern = re.compile(rf"(?:^|\D){dur_file}(?:\D|$)")
                matches = [f for f in SRC_DURATIONS.glob("*.csv") if pattern.search(f.stem)]

                if matches:
                    out_dur = chapter_dir / "durations.csv"
                    if not out_dur.exists() or matches[0].stat().st_mtime > out_dur.stat().st_mtime:
                        print("⏱️ Copying durations...")
                        shutil.copy2(matches[0], out_dur)
                else:
                    print(f"⚠️ No durations found for Chapter {chapter_num_padded}")

            # === AUDIO ===
            if sync_audio:
                audio_file = f"{chapter_num:03d}"
                pattern = re.compile(rf"(?:^|\D){audio_file}(?:\D|$)")
                matches = [f for f in SRC_AUDIO.glob("*.m4a") if pattern.search(f.stem)]

                if matches:
                    out_audio = chapter_dir / "audio.m4a"
                    if not out_audio.exists() or matches[0].stat().st_mtime > out_audio.stat().st_mtime:
                        print("🎵 Copying audio...")
                        shutil.copy2(matches[0], out_audio)
                else:
                    print(f"⚠️ No audio found for Chapter {chapter_num_padded}")

    print(f"✅ Sync complete! Files placed under {TARGET}")


if __name__ == "__main__":
    #root = "/Volumes/web/stotra_manjari/projects/"
    root = "/Users/thyagil/Amrutham/amrutham_assets/projects/"
    project_code = "ramayanam_sriramghanapatigal"
    volume = 5
    langs = ["be", "ka", "ma", "gu", "en", "te", "sa", "ta"]
    #langs = ["sa_bt"]
    # 🔹 Example calls:
    # sync only content
    sync_content = True
    sync_audio = False
    sync_durations = False
    sync_meanings = False

    sync_assets(root, project_code, volume, langs, sync_content, sync_audio, sync_durations, sync_meanings)

