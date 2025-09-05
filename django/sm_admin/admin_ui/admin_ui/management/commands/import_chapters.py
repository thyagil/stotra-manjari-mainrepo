import csv
from django.core.management.base import BaseCommand
from provisioning.models import Volume, Chapter


class Command(BaseCommand):
    help = "Import chapters from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to chapters.csv")
        parser.add_argument("project_code", type=str, help="Project code, e.g. sgp_srimad_ramayanam")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        project_code = options["project_code"]

        self.stdout.write(self.style.NOTICE(f"Importing chapters from {csv_file}..."))

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                volume_number, chapter_number, subtitle = row
                index = int(chapter_number)

                # find volume (assumes volume codes are like "01_bala_kandam")
                volume_code = f"{int(volume_number):02d}_"
                volume = Volume.objects.filter(project__code=project_code, code__startswith=volume_code).first()
                if not volume:
                    self.stdout.write(self.style.ERROR(f"No volume found for row: {row}"))
                    continue

                chapter_id = f"chapter{index:03d}"
                chapter, created = Chapter.objects.get_or_create(
                    id=chapter_id,
                    volume=volume,
                    defaults={
                        "index": index,
                        "title": f"Sarga {index}",
                        "subtitle": subtitle,
                        "state": 2,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created {chapter_id} in {volume.code}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Skipped existing {chapter_id}"))
