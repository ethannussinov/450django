from django.db import models

# Create your models here.

class District(models.Model):
    county_district_code = models.CharField(max_length=20, primary_key=True)
    district_name = models.CharField(max_length=100)
    county_name = models.CharField(max_length=100, null=True, blank=True)
    urban_rural_status = models.CharField(max_length=50, choices=[('urban', 'Urban'), ('suburban', 'Suburban'), ('rural', 'Rural')], default='suburban')
    school_type = models.CharField(max_length=50, choices=[('public', 'Public'), ('charter', 'Charter')], default='public')


    class Meta:
        db_table = 'district'

    def __str__(self):
        return self.district_name
    
class DistrictDiscipline(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    county_district_code = models.ForeignKey(
        'District', on_delete=models.CASCADE, to_field='county_district_code'
    )
    discipline_incidents = models.IntegerField(null=True, blank=True)
    discipline_incidents_rate = models.FloatField(null=True, blank=True)
    discipline_removal_in_schl_susp = models.IntegerField(null=True, blank=True)
    discipline_removal_in_schl_susp_rate = models.FloatField(null=True, blank=True)
    discipline_removal_out_schl_susp = models.IntegerField(null=True, blank=True)
    discipline_removal_out_schl_susp_rate = models.FloatField(null=True, blank=True)
    discipline_removal_expulsion = models.IntegerField(null=True, blank=True)
    discipline_removal_expulsion_rate = models.FloatField(null=True, blank=True)
    discipline_more_10_days = models.IntegerField(null=True, blank=True)
    discipline_more_10_days_rate = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'district_discipline'
        unique_together = ('year', 'county_district_code')

    def __str__(self):
        return f"{self.year} - {self.county_district_code.district_name} District Discipline"
    

class DistrictMetrics(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    county_district_code = models.ForeignKey(
        'District', on_delete=models.CASCADE, to_field='county_district_code'
    )
    enrollment_size = models.IntegerField(null=True, blank=True)

    enrollment_white_pct = models.FloatField(null=True, blank=True)
    enrollment_black_pct = models.FloatField(null=True, blank=True)
    enrollment_asian_pct = models.FloatField(null=True, blank=True)
    enrollment_hispanic_pct = models.FloatField(null=True, blank=True)
    enrollment_multiracial_pct = models.FloatField(null=True, blank=True)
    
    student_teacher_ratio = models.FloatField(null=True, blank=True)
    graduation_rate = models.FloatField(null=True, blank=True)
    dropout_rate = models.FloatField(null=True, blank=True)
    free_reduced_lunch_pct = models.FloatField(null=True, blank=True)
    act_score_avg = models.FloatField(null=True, blank=True)



    class Meta:
        db_table = 'district_metrics'
        unique_together = ('year', 'county_district_code')

    def __str__(self):
        return f"{self.year} - {self.county_district_code.district_name} District Metrics"
