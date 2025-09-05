#!/usr/bin/env python3
import os, re, shutil, sys
from pathlib import Path
from path_builder import PathBuilder

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config"


def safe_copytree(src: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = src / item.name
        d = dest / item.name
        if s.is_dir():
            safe_copytree(s, d)
        else:
            try:
                shutil.copy2(s, d)
            except OSError as e:
                if e.errno == 22:  # Invalid argument = flags issue
                    print(f"⚠️ Skipping metadata for {s}")
                    shutil.copy(s, d)   # copy file only, no attrs
                else:
                    raise


def sync_assets(root, project_code: str, volume_code: str, volume_name: str, langs,
                sync_content=True, sync_audio=True, sync_durations=True, sync_meanings=True,
                backupsync=False):

    # Load path builder from JSON
    json_config = f"{CONFIG_PATH}/{project_code}_paths.json"
    pb = PathBuilder(json_config, volume_code=volume_code, volume_name=volume_name)

    project_root = Path(root) / project_code
    chapters_root = project_root / f"volumes/volume{volume_code}" / "chapters"
    chapters_root.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Syncing {project_code} Volume {volume_code} into assets...")

    # === Backup ===
    if backupsync:
        backup_dir = project_root / "backup" / f"volume{volume_code}"
        if backup_dir.exists():
            reply = input(f"⚠️ Backup exists at {backup_dir}. Overwrite? (y/N): ").strip().lower()
            if reply != "y":
                print("❌ Backup cancelled.")
                sys.exit(0)
            shutil.rmtree(backup_dir)

        backup_dir.mkdir(parents=True, exist_ok=True)
        for name, src in {
            "content": pb.staging_content.parent,
            "audio": pb.staging_audio,
            "durations": pb.staging_durations,
            "meanings": pb.staging_meanings.parent
        }.items():
            dest = backup_dir / name
            safe_copytree(src, dest)
            print(f"📦 Backed up {name} → {dest}")

    # === Copy per language ===
    for lang in langs:
        if lang == "sa_bt":
            print("⚠️ sa_bt is not allowed.")
            continue

        pb.lang = "sa_bt" if lang == "sa" else lang
        content_dir = pb.staging_content
        pb.lang = lang   # reset back for dest path consistency

        for file in sorted(content_dir.glob("RAM_Kanda *_Sarga *.txt")):
            try:
                chapter_num = int(file.stem.split("Sarga")[1].strip())
            except Exception:
                print(f"⚠️ Could not parse chapter number from {file.name}")
                continue

            chapter_dir = chapters_root / f"chapter{chapter_num:02d}"
            (chapter_dir / "lang" / lang).mkdir(parents=True, exist_ok=True)

            print(f"📖 Processing Chapter {chapter_num:02d} ({lang})")

            # === VERSES ===
            if sync_content:
                shutil.copy2(file, chapter_dir / "lang" / lang / "verses.txt")

            # === MEANINGS ===
            if sync_meanings:
                meanings_file = pb.staging_meanings / f"RAM_Kanda {int(volume_code)}_Sarga {chapter_num}.txt"
                if meanings_file.exists():
                    shutil.copy2(meanings_file, chapter_dir / "lang" / lang / "meanings.txt")
                else:
                    print(f"⚠️ No meanings found for Chapter {chapter_num:02d}")

            # === DURATIONS ===
            if sync_durations:
                dur_file = f"{chapter_num:03d}"
                matches = [f for f in pb.staging_durations.glob("*.csv") if re.search(rf"(?:^|\D){dur_file}(?:\D|$)", f.stem)]
                if matches:
                    shutil.copy2(matches[0], chapter_dir / "durations.csv")
                else:
                    print(f"⚠️ No durations found for Chapter {chapter_num:02d}")

            # === AUDIO ===
            if sync_audio:
                audio_file = f"{chapter_num:03d}"
                matches = [f for f in pb.staging_audio.glob("*.m4a") if re.search(rf"(?:^|\D){audio_file}(?:\D|$)", f.stem)]
                if matches:
                    shutil.copy2(matches[0], chapter_dir / "audio.m4a")
                else:
                    print(f"⚠️ No audio found for Chapter {chapter_num:02d}")

    print(f"✅ Sync complete! Files placed under {chapters_root}")


if __name__ == "__main__":
    root = "/Volumes/web/stotra-manjari-assets/projects/"
    project_code = "ramayanam_sriramghanapatigal"
    volume_code, volume_name = "05", "Sundara Kandam"
    langs = ["be", "ka", "ma", "gu", "en", "te", "sa", "ta"]

    sync_assets(root, project_code, volume_code, volume_name, langs,
                sync_content=True, sync_audio=False, sync_durations=False, sync_meanings=False,
                backupsync=False)
