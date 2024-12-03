import csv
from django.core.management.base import BaseCommand
from dbconnect.models import District, DistrictMetrics


class Command(BaseCommand):
    help = "Load dropout rates into the DistrictMetrics table from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help="Path to the CSV file containing dropout rates"
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

                    # Clean and parse the dropout rate
                    def clean_value(value):
                        return None if value.strip() == '' else float(value)

                    dropout_rate = clean_value(row.get('DROPOUT_9_12_TOTAL_RATE'))

                    # Update the existing DistrictMetrics record
                    metrics = DistrictMetrics.objects.filter(
                        year=int(row['YEAR']),
                        county_district_code=district
                    ).first()

                    if metrics:
                        metrics.dropout_rate = dropout_rate
                        metrics.save()
                        self.stdout.write(f"Updated dropout rate for {district.district_name} in {row['YEAR']}.")
                    else:
                        self.stderr.write(f"Metrics record for district {row['COUNTY_DISTRICT_CODE']} in year {row['YEAR']} not found. Skipping.")

                self.stdout.write(self.style.SUCCESS("Dropout rate data successfully loaded."))
        except FileNotFoundError:
            self.stderr.write(f"File {csv_file} not found.")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
