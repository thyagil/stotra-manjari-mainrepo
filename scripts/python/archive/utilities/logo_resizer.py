from PIL import Image, ImageDraw, ImageFont

img_dir = "/Volumes/WORKBENCH/projects/flutter/stotra_manjari/assets/images/"

def logo_resizer():
    # Load your source logo
    img = Image.open(f"{img_dir}amrutham_logo.png")

    # Resize to 512x512
    img = img.resize((512, 512), Image.LANCZOS)

    # Save as PNG under 1MB
    img.save(f"{img_dir}playstore_icon.png", format="PNG", optimize=True)


def feature_image():

    # Create blank image
    img = Image.new("RGB", (1024, 500), color=(255, 153, 51))  # saffron orange

    # Draw text
    draw = ImageDraw.Draw(img)

    # Load fonts (use a font file you have, e.g. NotoSans, or custom Sanskrit font)
    title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", 90)
    subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)

    draw.text((80, 150), "Stotra Manjari", font=title_font, fill=(255, 255, 255))
    draw.text((80, 280), "Listen. Read. Reflect.", font=subtitle_font, fill=(255, 255, 255))

    # Save
    img.save(f"{img_dir}feature_graphic.png", format="PNG", quality=95)


feature_image()