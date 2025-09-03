import csv
import plistlib
from pathlib import Path
from admin.config.utils import get_project_path


def build_volume_plist(csv_file: Path, volume_id: str, volume_name: str,
                       volume_subtitle: str, output_file: Path,
                       thumbnail: str = "thumbnail.png", default_state: int = 2):
    """
    Create a volume plist from a CSV.
    """
    chapters = []
    with open(csv_file, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue

            try:
                chap_num = int(row[1].strip())
                title = row[2].strip()
                subtitle = row[3].strip() if len(row) > 3 and row[3].strip() else ""
                state = int(row[4].strip()) if len(row) > 4 and row[4].strip() else default_state
            except Exception as e:
                print(f"❌ Error while processing row: {row}")
                raise

            chapters.append({
                "id": f"chapter{chap_num:03d}",
                "index": chap_num,
                "title": f"Sarga {chap_num}",
                "subtitle": title,
                "state": state
            })

    volume_meta = {
        "id": volume_id,
        "name": volume_name,
        "subtitle": volume_subtitle,
        "state": default_state,
        "images": {"thumbnail": thumbnail},
        "chapters": sorted(chapters, key=lambda c: c["index"])
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "wb") as f:
        plistlib.dump(volume_meta, f)

    print(f"📘 Wrote {output_file} with {len(chapters)} chapters.")


def csvs_to_volume_plists(project_id: str, default_state: int = 2):
    """
    For a given project, read its project.plist and generate all volume plists
    from the CSV files listed under volumes.
    """
    project_dir = get_project_path(project_id)
    project_plist = project_dir / f"project.plist"

    if not project_plist.exists():
        raise FileNotFoundError(f"❌ Project plist not found: {project_plist}")

    with open(project_plist, "rb") as f:
        project_meta = plistlib.load(f)

    volumes = project_meta.get("volumes", [])
    if not volumes:
        print(f"⚠️ No volumes defined in {project_plist}")
        return

    for vol in volumes:
        vol_id = vol["id"]
        vol_name = vol["name"]
        vol_subtitle = vol.get("subtitle", "")
        csv_filename = vol.get("csv_file")

        if not csv_filename:
            print(f"⚠️ Volume {vol_id} has no csv_file defined, skipping")
            continue

        csv_file = project_dir / "data" / csv_filename
        if not csv_file.exists():
            print(f"⚠️ CSV not found for {vol_id}: {csv_file}")
            continue

        output_file = project_dir / "plists" / f"{vol_id}.plist"

        build_volume_plist(csv_file, vol_id, vol_name, vol_subtitle, output_file,
                           default_state=default_state)


if __name__ == "__main__":
    # Example run: generates all volume plists for the project
    csvs_to_volume_plists("skp_srimad_bhagavatam")
