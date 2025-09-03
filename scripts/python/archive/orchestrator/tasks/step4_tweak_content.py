# orchestrator/tasks/step4_tweak_content.py
from pathlib import Path

def run(args, resolver):
    """
    Step 4: Apply tweaks to content (merge lines, insert titles).
    """
    langs = args.langs or ["en"]
    volume = args.volume if args.project_type == "volume" else None

    for lang in langs:
        folder = resolver.resolve("content", volume=volume, lang=lang)
        for txt_file in Path(folder).glob("*.txt"):
            lines = txt_file.read_text(encoding="utf-8").splitlines()
            new_lines = []
            for line in lines:
                new_lines.append(line.replace(" \n", "{b}{t}"))
            txt_file.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"✍️ Tweaked {txt_file}")
