import csv
import re
import plistlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from admin.config.utils import get_project_path


def extract_chapter_num(name: str, regex: str) -> Optional[int]:
    """Extract chapter number from a string using regex (supports multiple groups)."""
    match = re.search(regex, name)
    if match:
        for g in match.groups():
            if g:
                try:
                    return int(g)
                except ValueError:
                    return None
    return None


def process_fcpxml(fcpxml_file: Path, out_dir: Path, project_format: str, chapter_regex: str):
    tree = ET.parse(fcpxml_file)
    root = tree.getroot()

    # strip namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    projects = root.findall(".//project")
    for project in projects:
        raw_name = project.get("name") or fcpxml_file.stem

        if project_format == "standalone":
            chap_num = 1
        else:
            chap_num = extract_chapter_num(raw_name, chapter_regex)

        if chap_num is None:
            print(f"⚠️ Could not extract chapter from '{raw_name}' in {fcpxml_file}")
            continue

        chapter_id = f"chapter{chap_num:03d}"
        rows = []
        for video in project.findall(".//video"):
            offset = video.get("offset")
            duration = video.get("duration")
            if offset and duration:
                rows.append((offset, duration))

        if rows:
            out_csv = out_dir / f"{chapter_id}.csv"
            with open(out_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["offset", "duration"])
                writer.writerows(rows)
            print(f"⏱ Durations → {out_csv}")
        else:
            print(f"⚠️ No durations found in {fcpxml_file}")


def extract_durations(project_id: str):
    """Step 6: Extract durations from FCPXMLs as per orchestrator.plist."""
    project_dir = get_project_path(project_id)
    orch_plist = project_dir / "orchestrator.plist"

    with open(orch_plist, "rb") as f:
        config = plistlib.load(f)

    project_format = config.get("format", "volume")
    staging_root = Path(config.get("staging_root", ""))
    if not staging_root:
        raise ValueError("❌ staging_root not defined in orchestrator.plist")

    step_cfg = config.get("durations", {})
    volumes_cfg = step_cfg.get("volumes", {})
    step_regex = step_cfg.get("chapter_regex", r"(\d+)")  # ✅ step-level default

    for vol_id, vol_cfg in volumes_cfg.items():
        if not vol_cfg.get("orchestrate", False):
            print(f"⏭️ Skipping {vol_id}")
            continue

        input_path = Path(vol_cfg.get("input_dir", ""))
        if not input_path.exists():
            print(f"⚠️ Input path not found for {vol_id}: {input_path}")
            continue

        # ✅ Volume regex override if present
        regex = vol_cfg.get("chapter_regex", step_regex)

        # Output path = staging_root/durations/<volume>
        output_dir = staging_root / "durations" / vol_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect FCPXML files
        fcpxml_files = []
        if input_path.is_file() and input_path.suffix == ".fcpxmld":
            # packaged folder, use info.fcpxml inside
            packaged_fcpxml = input_path / "info.fcpxml"
            if packaged_fcpxml.exists():
                fcpxml_files = [packaged_fcpxml]
            else:
                print(f"⚠️ info.fcpxml not found in {input_path}")
                continue
        elif input_path.is_dir():
            fcpxml_files = sorted(input_path.glob("*.fcpxml"))
        elif input_path.suffix == ".fcpxml":
            fcpxml_files = [input_path]
        else:
            print(f"⚠️ Input path is neither a dir of .fcpxml nor a .fcpxmld package: {input_path}")
            continue

        if not fcpxml_files:
            print(f"⚠️ No FCPXML files to process in {input_path}")
            continue

        print(f"📂 Processing {vol_id}")
        for fcpxml_file in fcpxml_files:
            process_fcpxml(fcpxml_file, output_dir, project_format, regex)


if __name__ == "__main__":
    extract_durations("skp_srimad_bhagavatam")
