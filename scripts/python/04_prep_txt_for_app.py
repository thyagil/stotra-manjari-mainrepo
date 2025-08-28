import os
from pathlib import Path
from projects.ramayanam_sriramghanapatigal import folders
from Global.Translation import Translator
from Global.Translation import InputType

volume = 5
#langs=["be", "ka", "ma", "gu", "en", "te", "sa", "sa_bt", "ta"]
langs = ["ta"]
send_for_trans_ta = True

def get_filepaths(directory, file_type, skip_subdir=True):
    """Collect file paths of a certain type in a directory."""
    file_paths = []
    if skip_subdir:
        for filename in sorted(os.listdir(directory)):
            if not filename.startswith('.') and not filename.startswith('~') and filename.endswith(file_type):
                filepath = os.path.join(directory, filename)
                file_paths.append(filepath)
    else:
        for root, directories, files in os.walk(directory):
            for filename in files:
                if filename.endswith(file_type):
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
    return sorted(file_paths)

for lang in langs:
    folders[volume].lang = lang
    input_folder = folders[volume].STAGING_FLDR_CONTENT

    txt_full_paths = get_filepaths(input_folder, ".txt")
    for txt_file in txt_full_paths:
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        insert_line_raw = None
        new_lines = []
        first_verse_encountered = False  # 👈 track first verse line

        # --- Step 1: grab title_body2 value if present ---
        for line in lines:
            if line.startswith("title_body2:"):
                insert_line_raw = line.split(":", 1)[1].strip()
                break

        i = 0
        while i < len(lines):
            line = lines[i]

            # --- Step 2: after metadata, insert title if missing ---
            if line.strip() == "--END METADATA" and insert_line_raw:
                new_lines.append(line)
                next_line = lines[i+1].strip() if i+1 < len(lines) else None
                if next_line != insert_line_raw:
                    insert_line = insert_line_raw
                    if send_for_trans_ta and lang == "ta":
                        translator = Translator()
                        insert_line = translator.transliterate(
                            False, False, InputType.STRING, insert_line
                        )
                    new_lines.append(insert_line + "\n")
                i += 1
                continue

            # --- Step 3: collapse couplets (skip very first verse line) ---
            if (
                    first_verse_encountered  # 👈 don't collapse the first verse
                    and i + 1 < len(lines)
                    and not any(x in line for x in ["।", "॥"])
                    and ("।" in lines[i+1] or "॥" in lines[i+1])
            ):
                merged = line.rstrip("\n") + "{b}{t}" + lines[i+1].lstrip()
                new_lines.append(merged)
                i += 2
                continue

            # Mark first verse line after metadata
            if not first_verse_encountered and not line.strip().startswith("--"):
                first_verse_encountered = True

            # default: just copy the line
            new_lines.append(line)
            i += 1

        # overwrite file
        with open(txt_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"Updated: {txt_file}")
