from django.core.management.base import BaseCommand
import csv
from dbconnect.models import District, DistrictDiscipline

class Command(BaseCommand):
    help = 'Import discipline data from a CSV file into the DistrictDiscipline table'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        try:
            with open(csv_file, mode='r') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    year = int(row['YEAR'])
                    county_district_code = row['COUNTY_DISTRICT_CODE']
                    discipline_incidents = int(row['DISCIPLINE_INCIDENTS'])
                    discipline_incidents_rate = float(row['DISCIPLINE_INCIDENT_RATE'])
                    discipline_removal_in_schl_susp = int(row['DISCIPLINE_REMOVAL_IN_SCHL_SUSP'])
                    discipline_removal_in_schl_susp_rate = float(row['DISCIPLINE_REMOVAL_IN_SCHL_SUSP_RATE'])
                    discipline_removal_out_schl_susp = int(row['DISCIPLINE_REMOVAL_OUT_SCHL_SUSP'])
                    discipline_removal_out_schl_susp_rate = float(row['DISCIPLINE_REMOVAL_OUT_SCHL_SUSP_RATE'])
                    discipline_removal_expulsion = int(row['DISCIPLINE_REMOVAL_EXPULSION'])
                    discipline_expulsion_rate = float(row['DISCIPLINE_EXPULSION_RATE'])
                    discipline_more_10_days = int(row['DISCIPLINE_MORE_10_DAYS'])
                    discipline_more_10_days_rate = float(row['DISCIPLINE_MORE_10_DAYS_RATE'])

                    district = District.objects.filter(county_district_code=county_district_code).first()

                    if district:
                        obj, created = DistrictDiscipline.objects.update_or_create(
                            year=year,
                            county_district_code=district,
                            defaults={
                                'discipline_incidents': discipline_incidents,
                                'discipline_incidents_rate': discipline_incidents_rate,
                                'discipline_removal_in_schl_susp': discipline_removal_in_schl_susp,
                                'discipline_removal_in_schl_susp_rate': discipline_removal_in_schl_susp_rate,
                                'discipline_removal_out_schl_susp': discipline_removal_out_schl_susp,
                                'discipline_removal_out_schl_susp_rate': discipline_removal_out_schl_susp_rate,
                                'discipline_removal_expulsion': discipline_removal_expulsion,
                                'discipline_removal_expulsion_rate': discipline_expulsion_rate,
                                'discipline_more_10_days': discipline_more_10_days,
                                'discipline_more_10_days_rate': discipline_more_10_days_rate,
                            }
                        )

                        if created:
                            self.stdout.write(
                                f"Added discipline data for district {county_district_code}, year {year}"
                            )
                        else:
                            self.stdout.write(
                                f"Updated discipline data for district {county_district_code}, year {year}"
                            )
                    else:
                        self.stdout.write(f"District {county_district_code} not found. Skipping.")
        except FileNotFoundError:
            self.stderr.write(f"File {csv_file} not found. Please provide a valid path.")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
