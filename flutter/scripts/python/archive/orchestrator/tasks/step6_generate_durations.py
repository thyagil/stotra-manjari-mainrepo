# orchestrator/tasks/step6_generate_durations.py
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

def run(args, resolver):
    """
    Step 6: Generate durations CSVs from Final Cut Pro FCPXML files.
    """
    volume = args.volume if args.project_type == "volume" else None
    fcpxml_file = resolver.resolve("fcpxml", volume=volume) / f"{args.lang}.fcpxml"
    out_dir = resolver.resolve("durations", volume=volume)
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(fcpxml_file)
    root = tree.getroot()

    # strip namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    projects = root.findall(".//project")
    for project in projects:
        name = project.get("name")
        rows = []
        for video in project.findall(".//video"):
            offset = video.get("offset")
            duration = video.get("duration")
            if offset and duration:
                rows.append((offset, duration))

        if rows:
            out_csv = out_dir / f"{name}.csv"
            with open(out_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["offset", "duration"])
                writer.writerows(rows)
            print(f"⏱ Durations → {out_csv}")
        else:
            print(f"⚠️ No durations found in {name}")
