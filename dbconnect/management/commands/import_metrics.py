import csv
from django.core.management.base import BaseCommand
from dbconnect.models import District, DistrictMetrics

class Command(BaseCommand):
    help = "Load metrics data into the DistrictMetrics table from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help="Path to the CSV file containing district metrics data"
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    district = District.objects.filter(county_district_code=row['county_district_code']).first()
                    if not district:
                        self.stderr.write(f"District with code {row['county_district_code']} not found. Skipping.")
                        continue

                    #clean fields (bug here)
                    def clean_value(value):
                        return None if value == '' else value

                    DistrictMetrics.objects.update_or_create(
                        year=row['year'],
                        county_district_code=district,
                        defaults={
                            'enrollment_size': clean_value(row.get('enrollment_size', None)),
                            'demographic_composition': row.get('demographic_composition', None),
                            'student_teacher_ratio': clean_value(row.get('student_teacher_ratio', None)),
                            'graduation_rate': clean_value(row.get('graduation_rate', None)),
                            'dropout_rate': clean_value(row.get('dropout_rate', None)),  # Add if available in future
                            'free_reduced_lunch_pct': clean_value(row.get('free_reduced_lunch_pct', None)),
                            'act_score_avg': clean_value(row.get('act_score_avg', None)),
                        }
                    )
                self.stdout.write(self.style.SUCCESS("DistrictMetrics data successfully loaded."))
        except FileNotFoundError:
            self.stderr.write(f"File {csv_file} not found.")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
