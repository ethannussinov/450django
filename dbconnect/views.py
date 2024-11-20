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
    county = request.GET.get('county', None)
    urban_rural = request.GET.get('urban_rural_status', None)
    demographic_filter = request.GET.get('demographic', None)
    sort_by = request.GET.get('sort_by', None)
    sort_order = request.GET.get('sort_order', 'asc')
    aggregate = request.GET.get('aggregate', None)
    school_type = request.GET.get('school_type', None)

    # Define valid metrics for each model
    valid_metrics_metrics = [
        'dropout_rate', 'graduation_rate', 'act_score_avg', 'student_teacher_ratio', 'free_reduced_lunch_pct'
    ]
    valid_metrics_discipline = [
        'discipline_incidents_rate', 'discipline_removal_in_schl_susp_rate',
        'discipline_removal_out_schl_susp_rate', 'discipline_removal_expulsion_rate',
        'discipline_more_10_days_rate'
    ]

    valid_metrics = valid_metrics_metrics + valid_metrics_discipline

    # Validate selected metrics
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

    if county:
        query &= Q(county_district_code__county_name=county)
    if urban_rural:
        query &= Q(county_district_code__urban_rural_status=urban_rural)
    if school_type:
        query &= Q(county_district_code__school_type=school_type)

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
            
            # Debugging: print the generated query
            print("Demographic filter applied with RawSQL:", metrics_query.query)
            
        except ValueError as e:
            return JsonResponse({'error': f'Invalid demographic filter format: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error applying demographic filter: {str(e)}'}, status=400)
    # Aggregate
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

    response = {
        'metadata': {
            'records': len(data),
            'selected_metrics': selected_metrics,
            'start_year': start_year,
            'end_year': end_year,
            'district_codes': district_codes,
            'county': county,
            'urban_rural_status': urban_rural,
            'school_type': school_type,
            'sort_by': sort_by,
            'sort_order': sort_order,
        },
        'data': data,
    }

    if not data:
        response['metadata']['message'] = 'No records found for the given filters.'

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
