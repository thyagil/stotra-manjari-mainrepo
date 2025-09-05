# Provisioning Orchestrator for Stotra Manjari projects.

## Directory layout
```
scripts/
  python/
    orchestrator/
      provision.py
      tasks/
        __init__.py
        step1_extract_audio.py
        step2_extract_text.py
        step3_translate_content.py
        step4_tweak_content.py
        step5_generate_meanings.py
        step6_generate_durations.py
        step7_generate_metadata.py
        step9_sync_staging.py
        step10_deploy_production.py
```
👉 Add an empty __init__.py inside tasks/ so it works as a package.

From the repo root:
```
python3 scripts/python/orchestrator/provision.py 1 --volume 5 --audio_format aac
```
Or in PyCharm run config:
```
scripts/python/orchestrator/provision.py
--volume 5 --audio_format aac
```

# Path resolver.py usage

Volume-based (Ramayanam Bala Kandam)
```python
resolver = PathResolver(
    base_dir="/Volumes/AMRUTHAM",
    artist="Sriram Ghanapatigal",
    project_name="Srimad Ramayanam",
    project_type="volume",
    volume_code="01",
    volume_name="Bala Kandam",
    audio_format="aac",
    lang="sa"
)

print(resolver.videos)  
# → /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Bounces/01 Bala Kandam/Published
```

Chapter-based (Bhagavad Gita)
```python
resolver = PathResolver(
    base_dir="/Volumes/AMRUTHAM",
    artist="Sriram Ghanapatigal",
    project_name="Bhagavad Gita",
    project_type="chapter",
    audio_format="aac",
    lang="sa"
)

print(resolver.videos)  
# → /Volumes/AMRUTHAM/Sriram Ghanapatigal/Bhagavad Gita/Video/Bounces/Published
```

Standalone (Kanakadhara Stotram)
```python
resolver = PathResolver(
    base_dir="/Volumes/AMRUTHAM",
    artist="Sriram Ghanapatigal",
    project_name="Kanakadhara Stotram",
    project_type="standalone",
    audio_format="aac",
    lang="sa"
)

print(resolver.videos)  
# → /Volumes/AMRUTHAM/Sriram Ghanapatigal/Kanakadhara Stotram/Video/Bounces/Published
```
