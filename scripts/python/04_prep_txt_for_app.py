import os
from pathlib import Path
from projects.ramayanam_sriramghanapatigal import folders
from Global.Translation import Translator
from Global.Translation import InputType

volume = 5
langs=["be", "ka", "ma", "gu", "en", "te", "sa", "sa_bt", "ta"]
#langs=["sa"]
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
    input_folder = folders[volume].FLDR_CONTENT_FINAL

    txt_full_paths = get_filepaths(input_folder, ".txt")
    for txt_file in txt_full_paths:
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        insert_line = None
        new_lines = []

        for i, line in enumerate(lines):
            new_lines.append(line)

            if line.startswith("title_body2:"):
                insert_line = line.split(":", 1)[1].strip()
                if send_for_trans_ta and lang == "ta":
                    translator = Translator()
                    insert_line = translator.transliterate(False, False, InputType.STRING, insert_line)

            if line.strip() == "--END METADATA" and insert_line:
                # Check if the next line already matches insert_line
                next_line = lines[i+1].strip() if i+1 < len(lines) else None
                if next_line != insert_line:
                    new_lines.append(insert_line + "\n")

        # overwrite file
        with open(txt_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"Updated: {txt_file}")
