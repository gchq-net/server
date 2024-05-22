import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser

from gchqnet.logistics.models import PlannedLocation
from gchqnet.quest.models.location import LocationDifficulty


class Command(BaseCommand):
    help = "Import planned locations"  # noqa: A003

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--locations_file", type=str, default="locations.csv")

    def handle(
        self,
        *,
        locations_file: str,
        verbosity: int,
        settings: str,
        pythonpath: str,
        traceback: bool,
        no_color: bool,
        force_color: bool,
        skip_checks: bool,
    ) -> None:
        if not os.environ.get("GCHQ_ENABLE_DATA_IMPORT", "false") == "true":
            self.stdout.write(
                "Data import is disabled as it is destructive. Please set GCHQ_ENABLE_DATA_IMPORT=true env var."
            )
            return

        if not input("Please type 1429 as written: ") == "one thousand four hundred and twenty nine":
            self.stdout.write("Nope")
            return

        locations_path = Path(locations_file)
        assert locations_path.is_file()
        assert locations_path.exists()

        PlannedLocation.objects.all().delete()

        with locations_path.open() as fh:
            for row in csv.DictReader(fh):
                if row["Internal Name"]:
                    display_name = row["Display Name (required)"]
                    difficulty = row["Difficulty"]
                    internal_name = row["Internal Name"]
                    hint = row["Hint"]
                    coords_raw = row["Approx Coords"]
                    coords = coords_raw.split(",") if coords_raw else (None, None)

                    self.stdout.write(f"Adding {row}")

                    PlannedLocation.objects.create(
                        display_name=display_name,
                        hint=hint,
                        internal_name=internal_name,
                        difficulty=LocationDifficulty[difficulty.upper()],
                        lat=coords[0],
                        long=coords[1],
                    )
