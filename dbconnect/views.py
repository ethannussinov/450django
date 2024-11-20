from django.shortcuts import render

from django.http import JsonResponse
from dbconnect.models import DistrictMetrics, District
from django.db.models import Avg, Sum


# Create your views here.

#TODO: add filter for charter vs public schools

def fetch_dashboard_data(request):
    #extract user inputs from GET params
    selected_metrics = request.GET.get('metrics', '') 
    selected_metrics = selected_metrics.split(',')
    start_year = request.GET.get('start_year', None)
    end_year = request.GET.get('end_year', None)
    district_codes = request.GET.getlist('district_code')
    sort_by = request.GET.get('sort_by', None)
    sort_order = request.GET.get('sort_order', 'asc')
    aggregate = request.GET.get('aggregate', None)

    #validate inputs
    if not selected_metrics:
        return JsonResponse({'error': 'No metrics selected'}, status=400)

    query = DistrictMetrics.objects.all()

    #filter by year(s)
    if start_year and end_year:
        try:
            query = query.filter(year__gte=int(start_year), year__lte=int(end_year))
        except ValueError:
            return JsonResponse({'error': 'Invalid year format'}, status=400)
    elif start_year:
        try:
            query = query.filter(year=int(start_year))
        except ValueError:
            return JsonResponse({'error': 'Invalid year format'}, status=400)

    #filter by district code(s)
    if district_codes:
        valid_districts = District.objects.filter(county_district_code__in=district_codes).values_list('county_district_code', flat=True)
        invalid_codes = set(district_codes) - set(valid_districts)
        if invalid_codes:
            return JsonResponse({'error': f'Invalid district codes: {", ".join(invalid_codes)}'}, status=400)
        query = query.filter(county_district_code__in=valid_districts)

    #sort
    if sort_by:
        if sort_order == 'desc':
            query = query.order_by(f'-{sort_by}')
        else:
            query = query.order_by(sort_by)

    #aggregate
    if aggregate:
        aggregates = {}
        for metric in selected_metrics:
            if aggregate == 'avg':
                aggregates[f'{metric}_avg'] = query.aggregate(Avg(metric))[f'{metric}__avg']
            elif aggregate == 'sum':
                aggregates[f'{metric}_sum'] = query.aggregate(Sum(metric))[f'{metric}__sum']
        return JsonResponse(aggregates)

    #fetch data
    data = list(query.values('year', 'county_district_code', *selected_metrics))
    response = {
        "metadata": {
            "records": len(data),
            "selected_metrics": selected_metrics,
            "start_year": start_year,
            "end_year": end_year,
            "district_codes": district_codes,
        },
        "data": data
    }
    return JsonResponse(response)


def dashboard(request):
    return render(request, 'dashboard.html')