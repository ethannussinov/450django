from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser
import csv
from dbconnect.models import District

class Command(BaseCommand):
    help = 'Import districts from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                county_district_code = row['county_district_code']
                district_name = row['district_name']

                district, created = District.objects.get_or_create(
                    county_district_code=county_district_code,
                    defaults={'district_name': district_name},
                )

                if not created and district.district_name != district_name:
                    district.district_name = district_name
                    district.save()

                if created:
                    self.stdout.write(f"Added district: {district_name} ({county_district_code})")
                else:
                    self.stdout.write(f"Updated district: {district_name} ({county_district_code})")