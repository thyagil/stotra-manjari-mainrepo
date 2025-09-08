# orchestration/forms.py
from django import forms

class AudioExtractionForm(forms.Form):
    volume = forms.ChoiceField(required=False, label="Volume")
    video_dir = forms.CharField(label="Video folder/file path")

    audio_format = forms.ChoiceField(
        choices=[("aac", "AAC (.m4a)"), ("mp3", "MP3 (.mp3)")],
        initial="aac",
        label="Output format"
    )
    output_dir = forms.CharField(label="Output folder path")
