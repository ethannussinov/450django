import csv
from django.core.management.base import BaseCommand
from dbconnect.models import District, DistrictMetrics


class Command(BaseCommand):
    help = "Load demographic data into the DistrictMetrics table from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help="Path to the CSV file containing demographic data"
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # Ensure the district exists
                    district = District.objects.filter(county_district_code=row['COUNTY_DISTRICT_CODE']).first()
                    if not district:
                        self.stderr.write(f"District with code {row['COUNTY_DISTRICT_CODE']} not found. Skipping.")
                        continue

                    # Clean and parse values
                    def clean_value(value):
                        return None if value.strip() == '' else float(value)

                    # Insert or update the DistrictMetrics record
                    DistrictMetrics.objects.update_or_create(
                        year=int(row['YEAR']),
                        county_district_code=district,
                        defaults={
                            'enrollment_size': clean_value(row.get('ENROLLMENT_GRADES_K_12')),
                            'enrollment_white_pct': clean_value(row.get('ENROLLMENT_WHITE_PCT')),
                            'enrollment_black_pct': clean_value(row.get('ENROLLMENT_BLACK_PCT')),
                            'enrollment_asian_pct': clean_value(row.get('ENROLLMENT_ASIAN_PCT')),
                            'enrollment_hispanic_pct': clean_value(row.get('ENROLLMENT_HISPANIC_PCT')),
                            'enrollment_multiracial_pct': clean_value(row.get('ENROLLMENT_MULTIRACIAL_PCT')),
                            'student_teacher_ratio': None,  # Placeholder if missing in CSV
                            'graduation_rate': None,        # Placeholder if missing in CSV
                            'dropout_rate': None,           # Placeholder if missing in CSV
                            'free_reduced_lunch_pct': clean_value(row.get('LUNCH_COUNT_FREE_REDUCED_PCT')),
                            'act_score_avg': None,          # Placeholder if missing in CSV
                        }
                    )
                self.stdout.write(self.style.SUCCESS("Demographic data successfully loaded into DistrictMetrics."))
        except FileNotFoundError:
            self.stderr.write(f"File {csv_file} not found.")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
