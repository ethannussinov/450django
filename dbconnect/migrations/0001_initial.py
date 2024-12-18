# Generated by Django 4.2.16 on 2024-11-20 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="District",
            fields=[
                (
                    "county_district_code",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("district_name", models.CharField(max_length=100)),
                (
                    "county_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "urban_rural_status",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
            ],
            options={"db_table": "district",},
        ),
        migrations.CreateModel(
            name="DistrictMetrics",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("year", models.IntegerField()),
                ("enrollment_size", models.IntegerField(blank=True, null=True)),
                ("demographic_composition", models.JSONField(blank=True, null=True)),
                ("student_teacher_ratio", models.FloatField(blank=True, null=True)),
                ("graduation_rate", models.FloatField(blank=True, null=True)),
                ("dropout_rate", models.FloatField(blank=True, null=True)),
                ("free_reduced_lunch_pct", models.FloatField(blank=True, null=True)),
                ("act_score_avg", models.FloatField(blank=True, null=True)),
                (
                    "county_district_code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dbconnect.district",
                    ),
                ),
            ],
            options={
                "db_table": "district_metrics",
                "unique_together": {("year", "county_district_code")},
            },
        ),
        migrations.CreateModel(
            name="DistrictDiscipline",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("year", models.IntegerField()),
                ("discipline_incidents", models.IntegerField(blank=True, null=True)),
                ("discipline_incidents_rate", models.FloatField(blank=True, null=True)),
                (
                    "discipline_removal_in_schl_susp",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "discipline_removal_in_schl_susp_rate",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "discipline_removal_out_schl_susp",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "discipline_removal_out_schl_susp_rate",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "discipline_removal_expulsion",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "discipline_removal_expulsion_rate",
                    models.FloatField(blank=True, null=True),
                ),
                ("discipline_more_10_days", models.IntegerField(blank=True, null=True)),
                (
                    "discipline_more_10_days_rate",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "county_district_code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dbconnect.district",
                    ),
                ),
            ],
            options={
                "db_table": "disctrict_discipline",
                "unique_together": {("year", "county_district_code")},
            },
        ),
    ]
