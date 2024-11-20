from django.contrib import admin
from .models import District, DistrictDiscipline, DistrictMetrics

# Register your models here.

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('county_district_code', 'district_name', 'county_name', 'urban_rural_status')
    search_fields = ('county_district_code', 'district_name', 'county_name')

class DistrictDisciplineAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'year',
        'county_district_code',
        'discipline_incidents',
        'discipline_incidents_rate',
        'discipline_removal_in_schl_susp',
        'discipline_removal_in_schl_susp_rate',
        'discipline_removal_out_schl_susp',
        'discipline_removal_out_schl_susp_rate',
        'discipline_removal_expulsion',
        'discipline_removal_expulsion_rate',
        'discipline_more_10_days',
        'discipline_more_10_days_rate',
    )
    search_fields = ('year', 'county_district_code__district_name')  #allows searching by district name
    list_filter = ('year',)  #adds fltering by year in admin interface

class DistrictMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'year',
        'county_district_code',
        'enrollment_size',
        'demographic_composition',
        'student_teacher_ratio',
        'graduation_rate',
        'dropout_rate',
        'free_reduced_lunch_pct',
        'act_score_avg',
    )
    search_fields = ('year', 'county_district_code__district_name')
    list_filter = ('year',)

admin.site.register(District, DistrictAdmin)
admin.site.register(DistrictDiscipline, DistrictDisciplineAdmin)
admin.site.register(DistrictMetrics, DistrictMetricsAdmin)
