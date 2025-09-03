import plistlib
from pathlib import Path
from admin.config.utils import get_project_path
from admin.support.translation import Translator, InputType


def tweak_file(txt_file: Path, lang: str, add_header: bool, collapse_couplets: bool):
    with open(txt_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    insert_line_raw = None
    new_lines = []
    first_verse_encountered = False

    # --- Step 1: find title_body2 ---
    if add_header:
        for line in lines:
            if line.startswith("title_body3:"):
                insert_line_raw = line.split(":", 1)[1].strip()
                break

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Step 2: after metadata, insert header if missing ---
        if add_header and line.strip() == "--END METADATA" and insert_line_raw:
            new_lines.append(line)
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else None
            if next_line != insert_line_raw:
                insert_line = insert_line_raw
                # Special case: Tamil transliteration
                if lang == "ta":
                    translator = Translator()
                    insert_line = translator.transliterate(
                        False, False, InputType.STRING, insert_line
                    )
                new_lines.append(insert_line + "\n")
            i += 1
            continue

        # --- Step 3: collapse couplets ---
        if (
                collapse_couplets
                and first_verse_encountered
                and i + 1 < len(lines)
                and not any(x in line for x in ["।", "॥"])
                and ("।" in lines[i + 1] or "॥" in lines[i + 1])
        ):
            merged = line.rstrip("\n") + "{b}{t}" + lines[i + 1].lstrip()
            new_lines.append(merged)
            i += 2
            continue

        # Mark first verse line after metadata
        if not first_verse_encountered and not line.strip().startswith("--"):
            first_verse_encountered = True

        new_lines.append(line)
        i += 1

    # overwrite file
    with open(txt_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"   ✏️ Updated {txt_file}")


def content_tweaks(project_id: str):
    """Step 4: Apply content tweaks (headers, couplets) per orchestrator.plist."""
    project_dir = get_project_path(project_id)
    orch_plist = project_dir / "orchestrator.plist"

    with open(orch_plist, "rb") as f:
        config = plistlib.load(f)

    staging_root = Path(config.get("staging_root", ""))
    if not staging_root:
        raise ValueError("❌ staging_root not defined in orchestrator.plist")

    step_cfg = config.get("content_tweaks", {})
    add_header = step_cfg.get("add_header", False)
    collapse_couplets = step_cfg.get("collapse_couplets", False)
    langs = step_cfg.get("langs", [])
    volumes_cfg = step_cfg.get("volumes", {})

    for vol_id, vol_cfg in volumes_cfg.items():
        if not vol_cfg.get("orchestrate", False):
            print(f"⏭️ Skipping {vol_id}")
            continue

        # ✅ Input directory is always staging_root/content/<volume>
        input_dir = staging_root / "content" / vol_id

        if not input_dir.exists():
            print(f"⚠️ Input dir not found for {vol_id}: {input_dir}")
            continue

        print(f"🔧 Tweaking {vol_id}")

        for lang in langs:
            lang_dir = input_dir / lang
            if not lang_dir.exists():
                print(f"   ⚠️ Lang folder missing: {lang_dir}")
                continue

            for txt_file in sorted(lang_dir.glob("*.txt")):
                tweak_file(txt_file, lang, add_header, collapse_couplets)


if __name__ == "__main__":
    content_tweaks("skp_srimad_bhagavatam")
