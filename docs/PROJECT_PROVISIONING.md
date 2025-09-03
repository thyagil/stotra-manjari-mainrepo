# 📖 Stotra Manjari – Project Provisioning Guide

This document describes the **end-to-end pipeline** for onboarding a new project into the **Stotra Manjari app**.  
It includes both **conceptual steps** and the **current working scripts**.  
Later, this can be streamlined into a CI/CD pipeline.

---

## Overview

A project can be one of three types:
- **Volume-based** → e.g., *Śrīmad Rāmāyaṇam* (6 kandams → chapters → videos).  
- **Chapter-based** → e.g., *Bhagavad Gītā* (18 adhyāyas → videos).  
- **Standalone** → e.g., *Kanakadhara Stotram*, *Viṣṇu Sahasranāmam* (single video).  

Every project flows through the same **provisioning pipeline**:

1. Extract audio from videos (Final Cut Pro output).  
2. Extract text/verses from PPTM (PowerPoint).  
3. Translate Sanskrit to other languages.  
4. Apply content tweaks for app compatibility.  
5. Generate meanings (AI-assisted).  
6. Generate durations (from FCPXML).  
7. Create metadata JSON files.  
8. Create images (banner, cover, volume thumbnails).  
9. Deploy to staging (file sync).  
10. Deploy to production (Google Cloud Storage).  

---

## Directory Layout

Working directories are standardized:

```json
{
  "base": "/Volumes/AMRUTHAM/{artist}/{project_name}",

  "staging": {
    "content": "Video/Mastering/Source Files/DOC/TXT/{volume_code} {volume_name}/Bounces/{lang}/",
    "audio": "Audio/Bounces/{volume_code} {volume_name}/audio/{audio_format}/",
    "durations": "Audio/Bounces/{volume_code} {volume_name}/durations/",
    "meanings": "Video/Mastering/Source Files/DOC/TXT/{volume_code} {volume_name}/Meanings/{lang}/"
  },

  "source": {
    "metadata": "Video/Mastering/Source Files/DOC/TXT/{volume_code} {volume_name}/{lang}/",
    "ppts": "Video/Mastering/Source Files/PPT/{volume_code} {volume_name}/Without Dupes/ta/",
    "videos": "Video/Bounces/{volume_code} {volume_name}/Published/",
    "fcpxml": "Video/Mastering/Final Cut Pro/FCPXML/Localized/{volume_code} {volume_name}/"
  }
}
```

---

## Step 1 – Extract Audio

### Purpose
- Extract clean **AAC/MP3 audio** from FCP-exported videos.
- Ensures app audio matches corrected video audio.

### Script

```python
#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path
from scripts.python.stotra_manjari.projects.ramayanam_sriramghanapatigal import folders

volume = 1
audio_format = "aac"
folders[volume].audio_format = audio_format

INPUT_DIR = folders[volume].FLDR_VIDEOS
OUTPUT_DIR = folders[volume].FLDR_AUDIO_FINAL
os.makedirs(OUTPUT_DIR, exist_ok=True)

for f in sorted(Path(INPUT_DIR).glob("*.mp4")):
    base = f.stem
    if audio_format == "mp3":
        cmd = ["ffmpeg","-y","-i",str(f),"-vn","-acodec","libmp3lame","-qscale:a","2",str(Path(OUTPUT_DIR)/f"{base}.mp3")]
    elif audio_format == "aac":
        cmd = ["ffmpeg","-y","-i",str(f),"-vn","-c:a","aac","-b:a","128k","-movflags","+faststart",str(Path(OUTPUT_DIR)/f"{base}.m4a")]
    else:
        sys.exit(1)
    subprocess.run(cmd, check=True)
    exit()
```

---

## Step 2 – Extract Text from PPTM

### Purpose
- Extract **Sanskrit/Tamil verses** (and metadata) from PowerPoint slides.

### Script

```python
#!/usr/bin/env python3
from pptx import Presentation
import os
from pathlib import Path

def insert_bt(textbox):
    updated_text, i = "", 0
    while i < len(textbox.paragraphs) - 1:
        line, next_line = textbox.paragraphs[i].text, textbox.paragraphs[i+1].text
        if next_line.startswith('\t'):
            updated_text += line.strip() + "{b}{t}" + next_line.strip() + "\n"
            i += 2
        else:
            updated_text += line.strip() + "\n"
            i += 1
    return updated_text
```

*(full script omitted here but included in repo – see `02_extract_text.py`)*

---

## Step 3 – Translate Content

### Purpose
- Translate **Sanskrit → multiple languages**.  
- Tamil is **never translated** (only copied from PPT).

### Script

```python
from Global.Translation import Translator, InputType
import os

def translate(input_txt_folder, output_txt_folder, lang):
    translator = Translator(FILE_LOGGER=False)
    translator.input_directory = input_txt_folder
    translator.output_directory = output_txt_folder
    translator.input_language = "sa"
    translator.output_language = lang
    processed_text = translator.transliterate(True, False, InputType.FILE)
```

---

## Step 4 – Content Tweaks

### Purpose
- Insert missing titles.  
- Merge couplets with `{b}{t}` markers.  
- Fix transliterations where needed.  

### Script

```python
for lang in langs:
    input_folder = folders[volume].STAGING_FLDR_CONTENT
    for txt_file in get_filepaths(input_folder, ".txt"):
        with open(txt_file,"r",encoding="utf-8") as f:
            lines=f.readlines()
        # Insert title + merge couplets...
```

---

## Step 5 – Generate Meanings

### Purpose
- Use **OpenAI GPT** to produce plain-English (or other target lang) line-by-line meanings.

### Script

```python
import openai, sys
from pathlib import Path

def fetch_meanings_batch(slokas, target_lang):
    prompt = f"Translate Sanskrit slokas into {target_lang}, one line per sloka..."
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip().splitlines()
```

---

## Step 6 – Generate Durations (FCPXML)

### Purpose
- Parse Final Cut Pro XML to extract **verse timings**.

### Script

```python
import xml.etree.ElementTree as ET
from pathlib import Path
import csv

def extract_project_durations(project):
    rows=[]
    for video in project.findall(".//video"):
        rows.append((video.get("offset"),video.get("duration")))
    return rows
```

---

## Step 7 – Metadata

### Purpose
- Generate **metadata.json** files:
  1. Marketplace `stotras.json` (global index).  
  2. Project-level `metadata.json`.  
  3. Volume-level `metadata.json`.  
  4. Chapter-level `metadata.json`.  

### Script

```python
def generate_chapter_metadata(csv_file, project_id, volume_id, output_root):
    root_path = Path(output_root)/project_id/"volumes"/volume_id
    # Generate per-chapter + volume-level metadata.json
```

---

## Step 8 – Images

### Required
- **banner.png/jpg** → featured card + project browser.  
- **cover.png/jpg** → marketplace project card.  
- **thumbnail.png** → currently unused (reserved).  
- **volXX.png** → volume list screen.  

👉 Currently **manual creation** (from PPT exports + design).  

---

## Step 9 – Deploy to Staging

### Purpose
- Copy from **working directories → staging structure**.  
- Normalize into the SM app’s expected directory layout.

### Script

```python
def sync_assets(root, project_code, volume_code, volume_name, langs, sync_content=True, sync_audio=True):
    # Copy verses, meanings, durations, audio into staging
```

---

## Step 10 – Deploy to Production (Google Cloud)

### Purpose
- Sync staging → **Google Cloud Storage bucket**.  
- Set correct MIME types (UTF-8 for txt/csv/json).  

### Script

```python
import subprocess
def sync_folder(local, bucket):
    subprocess.run(["gsutil","-m","rsync","-r",str(local),bucket], check=True)
```

---

## ✅ Summary

By the end of Step 10, the project is:
- Visible in **marketplace**.  
- Fully playable (verses, audio, durations, meanings).  
- Deployed to **production** on GCS.  

Next iteration:  
- Unify all steps under a **Makefile or Python Orchestrator**.  
- Add CI/CD hooks.  
- Automate image generation.  

---
