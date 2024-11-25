from django.shortcuts import render
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
    # county = request.GET.get('county', None)
    # urban_rural = request.GET.get('urban_rural_status', None)
    demographic_filter = request.GET.get('demographic', None)
    sort_by = request.GET.get('sort_by', None)
    sort_order = request.GET.get('sort_order', 'asc')
    aggregate = request.GET.get('aggregate', None)
    # school_type = request.GET.get('school_type', None)

    # Define valid metrics for each model
    valid_metrics_metrics = [
        'dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio', 'free_reduced_lunch_pct', 'enrollment_size'
    ]
    valid_metrics_discipline = [
        'discipline_incidents_rate', 'discipline_removal_in_schl_susp_rate',
        'discipline_removal_out_schl_susp_rate', 'discipline_removal_expulsion_rate',
        'discipline_more_10_days_rate'
    ]

    valid_metrics = valid_metrics_metrics + valid_metrics_discipline

    # Validate the selected metrics
    invalid_metrics = [metric for metric in selected_metrics if metric not in valid_metrics]
    if invalid_metrics:
        return JsonResponse({'error': f'Invalid metrics selected: {", ".join(invalid_metrics)}'}, status=400)

    # Start building queries
    query = Q()
    if start_year:
        query &= Q(year__gte=int(start_year))
    if end_year:
        query &= Q(year__lte=int(end_year))

    # Filter by district code(s)
    district_codes = [code.strip() for code in district_codes if code.strip()]  # Clean district codes
    if district_codes:
        valid_districts = set(District.objects.values_list('county_district_code', flat=True))
        invalid_codes = set(district_codes) - valid_districts
        if invalid_codes:
            return JsonResponse({'error': f'Invalid district codes: {", ".join(invalid_codes)}'}, status=400)
        query &= Q(county_district_code__in=district_codes)

    # if county:
    #     query &= Q(county_district_code__county_name=county)
    # if urban_rural:
    #     query &= Q(county_district_code__urban_rural_status=urban_rural)
    # if school_type:
    #     query &= Q(county_district_code__school_type=school_type)

    # Apply filters to both models
    metrics_query = DistrictMetrics.objects.filter(query)
    discipline_query = DistrictDiscipline.objects.filter(query)

    # Demographic filter
    if demographic_filter:
        try:
            key, operator, value = parse_demographic_filter(demographic_filter)
            value = float(value)  # Ensure value is numeric
            
            # Construct RawSQL query
            raw_sql = RawSQL(
                f"CAST(json_extract(demographic_composition, '$.{key}') AS REAL) {operator} %s",
                [value]
            )
            metrics_query = metrics_query.filter(raw_sql)
            
            # #debugging: print the generated query
            # print("Demographic filter applied with RawSQL:", metrics_query.query)
            
        except ValueError as e:
            return JsonResponse({'error': f'Invalid demographic filter format: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error applying demographic filter: {str(e)}'}, status=400)

    # Aggregate data
    if aggregate:
        if aggregate not in ['avg', 'sum']:
            return JsonResponse({'error': 'Invalid aggregate operation. Must be "avg" or "sum".'}, status=400)
        aggregates = {}
        for metric in selected_metrics:
            model_query = metrics_query if metric in valid_metrics_metrics else discipline_query
            if aggregate == 'avg':
                aggregates[f'{metric}_avg'] = model_query.aggregate(Avg(metric))[f'{metric}__avg']
            elif aggregate == 'sum':
                aggregates[f'{metric}_sum'] = model_query.aggregate(Sum(metric))[f'{metric}__sum']
        return JsonResponse(aggregates)

    # Fetch data
    data = []
    if any(metric in valid_metrics_metrics for metric in selected_metrics):
        data += list(metrics_query.values('year', 'county_district_code', *[m for m in selected_metrics if m in valid_metrics_metrics]))
    if any(metric in valid_metrics_discipline for metric in selected_metrics):
        data += list(discipline_query.values('year', 'county_district_code', *[m for m in selected_metrics if m in valid_metrics_discipline]))

    # Sorting
    if sort_by:
        if sort_by in valid_metrics_metrics:
            metrics_query = metrics_query.order_by(f'{"-" if sort_order == "desc" else ""}{sort_by}')
        elif sort_by in valid_metrics_discipline:
            discipline_query = discipline_query.order_by(f'{"-" if sort_order == "desc" else ""}{sort_by}')
        else:
            return JsonResponse({'error': f'Invalid sort field: {sort_by}'}, status=400)

    # Retrieve the district metadata (county_name, urban_rural_status, school_type) from the District model
    district_metadata = District.objects.filter(county_district_code__in=district_codes).values(
        'county_district_code', 'district_name', 'county_name', 'urban_rural_status', 'school_type'
    ).distinct()

    # If no data is found for the given district codes, return an error
    if not district_metadata:
        return JsonResponse({'error': 'No district data found for the provided district codes.'}, status=400)

    # Assuming all districts in the response share the same values, take the first district metadata entry
    district_info = district_metadata[0]

    # Prepare metadata with additional fields in the response
    response = {
        'metadata': {
            'records': len(data),
            'selected_metrics': selected_metrics,
            'start_year': start_year,
            'end_year': end_year,
            'district_codes': district_codes,
            'county_district_code': district_info['county_district_code'],
            'district_name': district_info['district_name'],
            'county_name': district_info['county_name'],
            'urban_rural_status': district_info['urban_rural_status'],
            'school_type': district_info['school_type'],
            'sort_by': sort_by,
            'sort_order': sort_order,
        },
        'data': data,
    }

    if not data:
        response['metadata']['message'] = 'No records found for the given filters.'

    return JsonResponse(response, safe=False)


def fetch_heatmap_data(request):
    #extract user inputs from GET params
    metric = request.GET.get('metric', None)
    start_year = request.GET.get('start_year', None)
    end_year = request.GET.get('end_year', None)
    county = request.GET.get('county', None)
    urban_rural = request.GET.get('urban_rural_status', None)
    school_type = request.GET.get('school_type', None)

    #validate selected metric
    valid_metrics = [
        'dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio', 
        'discipline_incidents_rate', 'discipline_removal_in_schl_susp_rate',
        'discipline_removal_out_schl_susp_rate', 'discipline_removal_expulsion_rate',
        'discipline_more_10_days_rate', 'free_reduced_lunch_pct'
    ]
    if not metric or metric not in valid_metrics:
        return JsonResponse({'error': f'Invalid or missing metric: {metric}'}, status=400)

    #build query filters
    query = Q()
    if start_year:
        query &= Q(year__gte=int(start_year))
    if end_year:
        query &= Q(year__lte=int(end_year))
    if county:
        query &= Q(county_district_code__county_name=county)
    if urban_rural:
        query &= Q(county_district_code__urban_rural_status=urban_rural)
    if school_type:
        query &= Q(county_district_code__school_type=school_type)

    #determine model to query
    if metric in ['dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio', 'free_reduced_lunch_pct']:
        data_query = DistrictMetrics.objects.filter(query)
    else:
        data_query = DistrictDiscipline.objects.filter(query)

    #aggregate data
    heatmap_data = (
        data_query
        .values('county_district_code__county_name')
        .annotate(metric_value=Avg(metric))
        .order_by('county_district_code__county_name')
    )

    response = {
        'metadata': {
            'metric': metric,
            'start_year': start_year,
            'end_year': end_year,
            'county': county,
            'urban_rural_status': urban_rural,
            'school_type': school_type,
            'records': len(heatmap_data),
        },
        'data': list(heatmap_data),
    }

    return JsonResponse(response, safe=False)


def parse_demographic_filter(filter_string):
    import re
    allowed_demographics = [
        'ENROLLMENT_WHITE_PCT', 
        'ENROLLMENT_BLACK_PCT', 
        'ENROLLMENT_ASIAN_PCT',
        'ENROLLMENT_HISPANIC_PCT',
        'ENROLLMENT_MULTIRACIAL_PCT'
    ]
    match = re.match(r'(\w+)([><=])([\d.]+)', filter_string)
    if not match:
        raise ValueError('Invalid filter string')
    key, operator, value = match.groups()
    if key not in allowed_demographics:
        raise ValueError(f'Invalid demographic field: {key}')
    return key, operator, value

def dashboard(request):
    return render(request, 'dashboard.html')

# provide district basic info
def get_district_data(request):
    districts = District.objects.all()
    district_data = [
        {"county_district_code": district.county_district_code, "district_name": district.district_name} for district in districts
    ]

    # Get metrics excluding 'id', 'year', and 'county_district_code'
    metric_columns = [field.name for field in DistrictMetrics._meta.get_fields()]
    metric_columns = [col for col in metric_columns if col not in ['id', 'year', 'county_district_code']]

    return JsonResponse({
        "districts": district_data,
        "metrics": metric_columns,
        "counties": ["St. Louis County", "St. Louis City"]
    })