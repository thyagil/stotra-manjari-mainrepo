import csv
import json
from pathlib import Path

def generate_chapter_metadata(csv_file, project_id, volume_id, output_root, overwrite=False):
    """
    Reads a CSV file describing chapters and generates:
    1. metadata.json for each chapter under:
         {output_root}/{project_id}/volumes/{volume_id}/chapters/chapterXX/
    2. metadata.json at the volume root listing all chapters.

    CSV format: volume,chapter,title,[description],[state]
    """

    csv_path = Path(csv_file)
    root_path = Path(output_root) / project_id / "volumes" / volume_id
    root_path.mkdir(parents=True, exist_ok=True)

    if not root_path.exists():
        raise FileNotFoundError(f"❌ Expected folder {root_path} does not exist")

    chapters = []

    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue  # skip invalid rows

            vol_num = int(row[0].strip())       # col1 volume
            chap_num = int(row[1].strip())      # col2 chapter
            title = row[2].strip()              # col3 title
            description = row[3].strip() if len(row) > 3 and row[3].strip() else title
            state = int(row[4].strip()) if len(row) > 4 and row[4].strip() else 2

            volume_id_from_csv = f"volume{vol_num:02d}"
            if volume_id_from_csv != volume_id:
                print(f"⚠️ Warning: CSV volume {volume_id_from_csv} does not match argument {volume_id}")

            chapter_id = f"chapter{chap_num:02d}"
            chapter_dir = root_path / "chapters" / chapter_id
            chapter_dir.mkdir(parents=True, exist_ok=True)

            if not chapter_dir.exists():
                raise FileNotFoundError(f"❌ Missing chapter directory: {chapter_dir}")

            # Chapter metadata
            metadata = {
                "id": chapter_id,
                "volumeId": volume_id,
                "title": title,
                "index": chap_num,
                "verses": None,
                "state": state,
                "description": description
            }

            out_file = chapter_dir / "metadata.json"
            if out_file.exists() and not overwrite:
                print(f"⚠️ Skipping existing {out_file}")
            else:
                with open(out_file, "w", encoding="utf-8") as out:
                    json.dump(metadata, out, ensure_ascii=False, indent=2)
                print(f"✅ Wrote {out_file}")

            # Collect for volume summary
            chapters.append({
                "index": chap_num,
                "id": chapter_id,
                "title": title,
                "verses": None,
                "state": state
            })

    # Volume metadata
    volume_num = int(volume_id.replace("volume", ""))

    volume_metadata = {
        "id": volume_id,
        "title": f"Volume {volume_num}",
        "index": volume_num,
        "chapters": len(chapters),
        "state": 2,
        "images": {
            "cover": f"images/vol{volume_num:02d}.png"
        },
        "chaptersList": sorted(chapters, key=lambda c: c["index"])
    }

    volume_file = root_path / "metadata.json"
    if volume_file.exists() and not overwrite:
        print(f"⚠️ Skipping existing {volume_file}")
    else:
        with open(volume_file, "w", encoding="utf-8") as vf:
            json.dump(volume_metadata, vf, ensure_ascii=False, indent=2)
        print(f"📘 Wrote {volume_file}")


if __name__ == "__main__":
    root = "/Volumes/web/stotra-manjari-assets/projects/"
    csv_file = f"{root}ramayanam_sriramghanapatigal/metadata/volume05.csv"
    project_id = "ramayanam_sriramghanapatigal"
    volume_id = "volume05"

    generate_chapter_metadata(csv_file, project_id, volume_id, root, overwrite=True)
