from django.shortcuts import render
from django.db import models
from django.http import JsonResponse
from dbconnect.models import DistrictMetrics, DistrictDiscipline, District
from django.db.models import Avg, Sum, Q, F, Value
from django.db.models.functions import Cast
from django.db.models.expressions import RawSQL

from django.core.exceptions import FieldError

def fetch_dashboard_data(request):
    # Extract user inputs from GET params
    selected_metrics = request.GET.get('metrics', '').split(',')
    start_year = request.GET.get('start_year', None)
    end_year = request.GET.get('end_year', None)
    district_codes = request.GET.get('district_code', '').split(',')
    urban_rural = request.GET.get('urban_rural_status', None)
    school_type = request.GET.get('school_type', None)

    print("Request Parameters:", request.GET)
    print("Selected Metrics:", selected_metrics)
    print("Start Year:", start_year, "End Year:", end_year)
    print("District Codes:", district_codes)

    # Define valid metrics for each model
    valid_metrics_metrics = [
        'dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio',
        'free_reduced_lunch_pct', 'enrollment_size', 'enrollment_white_pct', 'enrollment_black_pct', 
        'enrollment_asian_pct', 'enrollment_hispanic_pct', 'enrollment_multiracial_pct'
    ]
    valid_metrics_discipline = [
        'discipline_incidents_rate', 'discipline_removal_in_schl_susp_rate',
        'discipline_removal_out_schl_susp_rate', 'discipline_removal_expulsion_rate',
        'discipline_more_10_days_rate'
    ]

    # Separate metrics based on the model they belong to
    metrics_for_metrics_model = [m for m in selected_metrics if m in valid_metrics_metrics]
    metrics_for_discipline_model = [m for m in selected_metrics if m in valid_metrics_discipline]

    print("Metrics for DistrictMetrics:", metrics_for_metrics_model)
    print("Metrics for DistrictDiscipline:", metrics_for_discipline_model)

    # Validation: Single district can have multiple metrics, but multiple districts must have only one metric
    if len(district_codes) > 1 and len(selected_metrics) > 1:
        return JsonResponse(
            {'error': 'Invalid combination. Select one metric when choosing multiple districts.'},
            status=400
        )

    # Start building query filters
    query = Q()
    if start_year:
        query &= Q(year__gte=int(start_year))
    if end_year:
        query &= Q(year__lte=int(end_year))
    if district_codes:
        query &= Q(county_district_code__in=district_codes)

    print("Constructed Query:", query)

    # Fetch data for DistrictMetrics
    metrics_data = []
    if metrics_for_metrics_model:
        metrics_query = DistrictMetrics.objects.filter(query)
        print("Metrics Query Results:", list(metrics_query.values()))
        for metric in metrics_for_metrics_model:
            metric_data = metrics_query.annotate(
                district_name=F("county_district_code__district_name"),  # Access through the foreign key
                metric_value=F(metric),
                metric=Value(metric, output_field=models.CharField())
            ).values("year", "county_district_code", "district_name", "metric_value", "metric")
            metrics_data.extend(metric_data)

    # Fetch data for DistrictDiscipline
    discipline_data = []
    if metrics_for_discipline_model:
        discipline_query = DistrictDiscipline.objects.filter(query)
        print("Discipline Query Results:", list(discipline_query.values()))
        for metric in metrics_for_discipline_model:
            discipline_metric_data = discipline_query.annotate(
                district_name=F("county_district_code__district_name"),  # Access through the foreign key
                metric_value=F(metric),
                metric=Value(metric, output_field=models.CharField())
            ).values("year", "county_district_code", "district_name", "metric_value", "metric")
            discipline_data.extend(discipline_metric_data)

    # Combine data
    combined_data = metrics_data + discipline_data
    print("Combined Data:", combined_data)

    # Ensure response includes 'metric_value' for all requested metrics
    structured_data = [
        {
            "year": entry["year"],
            "district_code": entry["county_district_code"],
            "district_name": entry.get("district_name", "Unknown District"),
            "metric_value": entry.get("metric_value", 0),  # Use 0 if metric_value is missing
            "metric": entry.get("metric", "unknown"),      # Use "unknown" if metric is missing
        }
        for entry in combined_data
    ]

    # Prepare response
    response = {
        'metadata': {
            'records': len(structured_data),
            'selected_metrics': selected_metrics,
            'start_year': start_year,
            'end_year': end_year,
            'district_codes': district_codes,
        },
        'data': structured_data,
    }

    print("Structured Data Sent to Frontend:", structured_data)

    if not structured_data:
        response['metadata']['message'] = 'No records found for the given filters.'

    return JsonResponse(response, safe=False)


def fetch_heatmap_data(request):
    metric = request.GET.get('metric', None)
    start_year = request.GET.get('start_year', None)
    end_year = request.GET.get('end_year', None)

    valid_metrics = [
        'dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio', 
        'discipline_incidents_rate', 'discipline_removal_in_schl_susp_rate',
        'discipline_removal_out_schl_susp_rate', 'discipline_removal_expulsion_rate',
        'discipline_more_10_days_rate', 'free_reduced_lunch_pct'
    ]
    if not metric or metric not in valid_metrics:
        return JsonResponse({'error': f'Invalid or missing metric: {metric}'}, status=400)

    query = Q()
    if start_year:
        query &= Q(year__gte=int(start_year))
    if end_year:
        query &= Q(year__lte=int(end_year))

    if metric in ['dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio', 'free_reduced_lunch_pct']:
        data_query = DistrictMetrics.objects.filter(query)
    else:
        data_query = DistrictDiscipline.objects.filter(query)

    heatmap_data = (
        data_query
        .annotate(metric_value=Avg(metric))
        .values("county_district_code__district_name", "metric_value")
        .order_by("county_district_code__district_name")
    )

    response = {
        'metadata': {
            'metric': metric,
            'start_year': start_year,
            'end_year': end_year,
            'records': len(heatmap_data),
        },
        'data': list(heatmap_data),
    }

    return JsonResponse(response, safe=False)

def dashboard(request):
    return render(request, 'dashboard.html')

def get_district_data(request):
    districts = District.objects.all()
    district_data = [
        {"county_district_code": district.county_district_code, "district_name": district.district_name}
        for district in districts
    ]

    metric_columns = [field.name for field in DistrictMetrics._meta.get_fields()] + [
        field.name for field in DistrictDiscipline._meta.get_fields()
    ]
    metric_columns = [
        col for col in metric_columns if col not in ['id', 'year', 'county_district_code']
    ]

    return JsonResponse({
        "districts": district_data,
        "metrics": metric_columns,  # Include both DistrictMetrics and DistrictDiscipline fields
    })