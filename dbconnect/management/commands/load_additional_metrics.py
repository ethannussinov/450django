import csv
from django.core.management.base import BaseCommand
from dbconnect.models import District, DistrictMetrics


class Command(BaseCommand):
    help = "Load additional metrics (student_teacher_ratio, graduation_rate, act_score_avg) into the DistrictMetrics table"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help="Path to the CSV file containing additional metrics data"
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # Ensure the district exists
                    district = District.objects.filter(county_district_code=row['county_district_code']).first()
                    if not district:
                        self.stderr.write(f"District with code {row['county_district_code']} not found. Skipping.")
                        continue

                    # Clean and parse values
                    def clean_value(value):
                        return None if value.strip() == '' else float(value)

                    # Update existing DistrictMetrics record
                    metrics = DistrictMetrics.objects.filter(
                        year=int(row['year']),
                        county_district_code=district
                    ).first()

                    if metrics:
                        metrics.student_teacher_ratio = clean_value(row.get('student_teacher_ratio'))
                        metrics.graduation_rate = clean_value(row.get('graduation_rate'))
                        metrics.act_score_avg = clean_value(row.get('act_score_avg'))
                        metrics.save()
                        self.stdout.write(f"Updated metrics for {district.district_name} in {row['year']}.")
                    else:
                        self.stderr.write(f"Metrics record for district {row['county_district_code']} in year {row['year']} not found. Skipping.")

                self.stdout.write(self.style.SUCCESS("Additional metrics data successfully loaded."))
        except FileNotFoundError:
            self.stderr.write(f"File {csv_file} not found.")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
