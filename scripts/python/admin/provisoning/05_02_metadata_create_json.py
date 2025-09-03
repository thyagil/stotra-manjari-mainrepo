import json
import plistlib
from pathlib import Path
from admin.config.utils import get_project_path


def plist_to_project_json(project_id: str, output_file: Path = None, overwrite: bool = True):
    """
    Build final project metadata.json by merging project.plist
    with all per-volume plists (volumeXX.plist).
    """

    # Locate project dir and plist
    project_dir = get_project_path(project_id)
    project_plist = project_dir / "project.plist"

    if not project_plist.exists():
        raise FileNotFoundError(f"❌ Project plist not found: {project_plist}")

    # Load project plist
    with open(project_plist, "rb") as f:
        project_meta = plistlib.load(f)

    # Extract volume definitions
    volumes_defs = project_meta.get("volumes", [])
    volumes_data = []

    for vol in volumes_defs:
        vol_id = vol["id"]
        vol_name = vol.get("name", "")
        vol_subtitle = vol.get("subtitle", "")

        vol_data = {
            "id": vol_id,
            "name": vol_name,
            "subtitle": vol_subtitle,
            "chapters": []
        }

        # ✅ Always read from plists/volumeXX.plist
        vol_plist = project_dir / "plists" / f"{vol_id}.plist"
        if not vol_plist.exists():
            print(f"⚠️ Missing {vol_plist}, skipping {vol_id}")
            continue

        with open(vol_plist, "rb") as vf:
            vol_meta = plistlib.load(vf)

        vol_data.update({
            "name": vol_meta.get("name", vol_name),
            "subtitle": vol_meta.get("subtitle", vol_subtitle),
            "chapters": vol_meta.get("chapters", [])
        })

        if "images" in vol_meta:
            vol_data["images"] = vol_meta["images"]

        print(f"✅ Loaded {vol_id} from {vol_plist.name} with {len(vol_data['chapters'])} chapters")
        volumes_data.append(vol_data)

    # Replace the "volumes" entry with structured volumes
    project_meta["structure"] = {"volumes": volumes_data}
    if "volumes" in project_meta:
        del project_meta["volumes"]

    # Decide output path
    if output_file is None:
        output_file = project_dir / "metadata.json"

    if output_file.exists() and not overwrite:
        print(f"⚠️ Skipping existing {output_file}")
        return

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(project_meta, out, ensure_ascii=False, indent=2)

    print(f"📘 Wrote final project metadata to {output_file}")


if __name__ == "__main__":
    plist_to_project_json("skp_srimad_bhagavatam")
