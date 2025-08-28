#!/usr/bin/env python3
import os, re, shutil, sys
from pathlib import Path
from projects.ramayanam_sriramghanapatigal import folders

def sync_assets(root, project_code: str, volume: int, langs=[],
                sync_content=True, sync_audio=True,
                sync_durations=True, sync_meanings=True,
                backupsync=False):

    # --- META (staging sources) ---
    SRC_AUDIO = Path(folders[volume].STAGING_FLDR_AUDIO)
    SRC_DURATIONS = Path(folders[volume].STAGING_FLDR_DURATIONS)
    SRC_CONTENT = Path(folders[volume].STAGING_FLDR_CONTENT)
    SRC_MEANINGS = Path(folders[volume].STAGING_FLDR_MEANINGS if hasattr(folders[volume], "FLDR_MEANINGS") else folders[volume].STAGING_FLDR_DURATIONS)

    # --- DESTINATION ROOT (assets) ---
    PROJECT_ROOT = Path(f"{root}{project_code}")
    TARGET_ROOT = PROJECT_ROOT / f"volumes/volume{volume:02d}"
    CHAPTERS = TARGET_ROOT / "chapters"
    CHAPTERS.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Syncing {project_code} (Volume {volume}) into assets...")

    # --- Step 1: Backup (if enabled) ---
    if backupsync:
        BACKUP_BASE = PROJECT_ROOT / "backup" / "volumes"
        BACKUP_DIR = BACKUP_BASE / f"volume{volume:02d}"

        folders_to_backup = {
            "content": Path(folders[volume].STAGING_FLDR_CONTENT).parent,  # 👈 all langs
            "audio": SRC_AUDIO,
            "durations": SRC_DURATIONS,
            "meanings": SRC_MEANINGS,
        }


        if BACKUP_DIR.exists():
            reply = input(f"⚠️ Backup already exists at {BACKUP_DIR}. Overwrite? (y/N): ").strip().lower()
            if reply != "y":
                print("❌ Backup cancelled by user.")
                sys.exit(0)
            else:
                print("⚠️ Overwriting existing backup...")

        # wipe old and create fresh
        if BACKUP_DIR.exists():
            shutil.rmtree(BACKUP_DIR)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        # copy each folder into backup
        for name, src in folders_to_backup.items():
            dest = BACKUP_DIR / name
            shutil.copytree(src, dest)
            print(f"📦 Backed up {name} → {dest}")

        print(f"✅ Backup complete at {BACKUP_DIR}")

    # --- Step 2: Transform sync (same as before) ---
    for lang in langs:
        # handle sa special-case
        if lang == "sa":
            folders[volume].lang = "sa_bt"
            SRC_CONTENT = Path(folders[volume].STAGING_FLDR_CONTENT)
            lang = "sa"
        elif lang == "sa_bt":
            print("This lang code is not allowed.")
            exit()
        else:
            folders[volume].lang = lang
            SRC_CONTENT = Path(folders[volume].STAGING_FLDR_CONTENT)

        SRC_MEANINGS = Path(folders[volume].STAGING_FLDR_MEANINGS if hasattr(folders[volume], "FLDR_MEANINGS") else folders[volume].STAGING_FLDR_DURATIONS)

        for file in sorted(SRC_CONTENT.glob("RAM_Kanda *_Sarga *.txt")):
            fname = file.name
            try:
                chapter_num = int(fname.split("Sarga")[1].split(".")[0].strip())
            except Exception:
                print(f"⚠️ Could not parse chapter number from {fname}")
                continue

            chapter_num_padded = f"{chapter_num:02d}"
            chapter_dir = CHAPTERS / f"chapter{chapter_num_padded}"
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

    print(f"✅ Sync complete! Files placed under {CHAPTERS}")


if __name__ == "__main__":
    root = "/Volumes/WORKBENCH/assets/stotra_manjari/projects/"
    project_code = "ramayanam_sriramghanapatigal"
    volume = 1
    langs = ["be", "ka", "ma", "gu", "en", "te", "sa", "ta"]

    # === Control flags ===
    sync_content = True
    sync_audio = False
    sync_durations = False
    sync_meanings = False
    backupsync = True   # 👈 toggle this

    sync_assets(root, project_code, volume, langs,
                sync_content, sync_audio, sync_durations, sync_meanings,
                backupsync)
