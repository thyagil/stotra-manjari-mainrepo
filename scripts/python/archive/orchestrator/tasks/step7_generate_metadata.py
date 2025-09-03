# orchestrator/tasks/step7_generate_metadata.py
import csv, json
from pathlib import Path

def run(args, resolver):
    """
    Step 7: Generate metadata.json for project, volumes, and chapters.
    """
    project_id = args.project_id
    volume = args.volume if args.project_type == "volume" else None
    csv_file = resolver.resolve("metadata", volume=volume) / f"{volume}.csv"
    root_path = resolver.project_root / project_id / "volumes" / volume
    root_path.mkdir(parents=True, exist_ok=True)

    chapters = []
    with open(csv_file, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue
            chap_num = int(row[1].strip())
            title = row[2].strip()
            chapter_id = f"chapter{chap_num:02d}"

            chapter_dir = root_path / "chapters" / chapter_id
            chapter_dir.mkdir(parents=True, exist_ok=True)

            metadata = {
                "id": chapter_id,
                "volumeId": volume,
                "title": title,
                "index": chap_num,
                "verses": None,
                "state": 2,
                "description": row[3] if len(row) > 3 else title
            }
            with open(chapter_dir / "metadata.json", "w", encoding="utf-8") as out:
                json.dump(metadata, out, ensure_ascii=False, indent=2)
            chapters.append(metadata)

    volume_metadata = {
        "id": volume,
        "title": f"Volume {int(volume.replace('volume','')):02d}",
        "index": int(volume.replace("volume","")),
        "chapters": len(chapters),
        "state": 2,
        "images": {"cover": f"images/{volume}.png"},
        "chaptersList": sorted(chapters, key=lambda c: c["index"])
    }
    with open(root_path / "metadata.json", "w", encoding="utf-8") as vf:
        json.dump(volume_metadata, vf, ensure_ascii=False, indent=2)
    print(f"📘 Metadata generated for {volume}")
