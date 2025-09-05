# orchestrator/tasks/step9_sync_to_staging.py
import shutil
from pathlib import Path

def safe_copytree(src: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s, d = src / item.name, dest / item.name
        if s.is_dir():
            safe_copytree(s, d)
        else:
            shutil.copy2(s, d)

def run(args, resolver):
    """
    Step 9: Sync assets from working directories into staging structure.
    """
    project_id = args.project_id
    volume = args.volume if args.project_type == "volume" else None
    langs = args.langs

    project_root = resolver.project_root / project_id
    staging_root = resolver.staging_root / project_id

    print(f"🚀 Syncing {project_id} volume={volume} → staging")

    for lang in langs:
        content_src = resolver.resolve("content", volume=volume, lang=lang)
        content_dst = staging_root / "volumes" / volume / "lang" / lang
        safe_copytree(content_src, content_dst)

        audio_src = resolver.resolve("audio", volume=volume, audio_format=args.audio_format)
        audio_dst = staging_root / "volumes" / volume / "audio"
        safe_copytree(audio_src, audio_dst)

    print(f"✅ Sync complete → {staging_root}")
