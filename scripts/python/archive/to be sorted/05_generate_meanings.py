#!/usr/bin/env python3
import os, sys
import openai
from pathlib import Path

# ✅ API key
openai.api_key = "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"
if not openai.api_key:
    try:
        from secrets import OPENAI_API_KEY
        openai.api_key = OPENAI_API_KEY
    except ImportError:
        print("❌ No API key found. Set OPENAI_API_KEY env var or create secrets.py")
        sys.exit(1)

END_MARKS = ("।", "॥")

def combine_continuations(lines):
    """Merge Sanskrit lines where the first lacks । or ॥ but the next ends properly."""
    merged = []
    buffer = ""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if buffer:
            buffer += " " + stripped
        else:
            buffer = stripped

        if buffer.endswith(END_MARKS):
            merged.append(buffer)
            buffer = ""
    if buffer:  # leftover
        merged.append(buffer)
    return merged

def fetch_meanings_batch(slokas, target_lang):
    """Translate a batch of slokas and return one meaning per input line."""
    prompt = f"""Translate these Sanskrit slokas into {target_lang}.
⚠️ RULES:
- Output plain translation only, one line per sloka.
- Do NOT add numbering, quotes, or prefixes like 'The verse translates to'.
- Keep order identical to input.
- No empty lines unless the sloka is blank (should not happen).
- If a verse is direct speech, only then use quotes naturally.

Slokas:
{chr(10).join(slokas)}"""

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    out = resp.choices[0].message.content.strip().splitlines()
    # Ensure 1:1 mapping
    results = []
    for i, s in enumerate(slokas):
        if i < len(out) and out[i].strip():
            results.append(out[i].strip())
        else:
            results.append("⚠️ Missing meaning")
    return results

def process_chapter(input_file: Path, output_dir: Path, lang: str, batch_size=15):
    print(f"📖 Processing {input_file.name}...")
    lines = input_file.read_text(encoding="utf-8").splitlines()

    # Copy metadata
    output_lines = []
    idx = 0
    while idx < len(lines) and not lines[idx].strip().startswith("--END METADATA"):
        output_lines.append(lines[idx])
        idx += 1
    if idx < len(lines):
        output_lines.append(lines[idx])  # include --END METADATA
        idx += 1

    # Add header
    output_lines.append(f"Beginning of {input_file.stem}")
    print("   ✅ Metadata copied.")

    # Combine continuation lines
    verses = combine_continuations([l for l in lines[idx:] if l.strip()])

    # Translate in batches
    for i in range(0, len(verses), batch_size):
        chunk = verses[i:i+batch_size]
        print(f"   🔄 Translating {len(chunk)} slokas ({i+1}–{i+len(chunk)})...")
        meanings = fetch_meanings_batch(chunk, lang)
        output_lines.extend(meanings)

    # Save output
    output_file = output_dir / input_file.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"   💾 Saved to {output_file}")

def main():
    if len(sys.argv) != 4:
        print("Usage: 05_generate_meanings.py <input_dir> <output_dir> <lang>")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    lang = sys.argv[3]

    for txt_file in sorted(input_dir.glob("*.txt")):
        process_chapter(txt_file, output_dir, lang)

if __name__ == "__main__":
    main()
