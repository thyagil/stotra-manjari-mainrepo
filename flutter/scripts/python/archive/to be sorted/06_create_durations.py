import os
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from projects.ramayanam_sriramghanapatigal import folders

# -------- CONFIG --------
volume = 5
FCPXML_FILE = Path(f"{folders[volume].FLDR_FCPXML}ta.fcpxmld/Info.fcpxml")
OUT_DIR = Path(folders[volume].STAGING_FLDR_DURATIONS)

def parse_rational_time(v: str) -> str:
    v = v.strip()
    return v if v.endswith("s") else v + "s"

def extract_project_durations(project):
    rows = []
    for video in project.findall(".//video"):
        offset = video.get("offset")
        duration = video.get("duration")
        if offset and duration:
            rows.append((parse_rational_time(offset),
                         parse_rational_time(duration)))
    return rows

def process_fcpxml(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()

    # strip namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    projects = root.findall(".//project")
    for idx, project in enumerate(projects, start=1):
        name = project.get("name")
        filename = f"{name}.csv"
        rows = extract_project_durations(project)
        if not rows:
            print(f"⚠️ No rows in {name}")
            continue

        out_csv = OUT_DIR / filename
        with open(out_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["offset", "duration"])
            writer.writerows(rows)

        print(f"✅ {name} → {out_csv}.csv ({len(rows)} rows)")

if __name__ == "__main__":
    process_fcpxml(FCPXML_FILE)
