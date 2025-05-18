from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.utils import timezone

from .models import BusRoute, TrainRoute, DAY_CHOICES

def generate_pdf_response(title, data, headers, filename_prefix="Timetable"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()

    travel_mithra_style = ParagraphStyle(
        'TravelMithraStyle',
        parent=styles['h1'],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=0,
        fontName='Helvetica-Bold'
    )
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['h1'],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=14
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        textColor=colors.white,
        spaceAfter=0
    )
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        spaceAfter=0
    )

    elements = []

    elements.append(Paragraph("Travel Mithra", travel_mithra_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2 * inch))

    table_data = []
    header_row = [Paragraph(h, header_style) for h in headers]
    table_data.append(header_row)

    for row_data_list in data:
        formatted_row = []
        for item in row_data_list:
            if isinstance(item, datetime.datetime):
                formatted_item = timezone.localtime(item).strftime('%Y-%m-%d %I:%M %p')
            elif isinstance(item, list) and all(isinstance(i, tuple) for i in item):
                formatted_item = "<br/>".join([f"• {s[0]} ({s[1]})" if s[1] else f"• {s[0]}" for s in item])
            elif item is None:
                formatted_item = "N/A"
            else:
                formatted_item = str(item)
            formatted_row.append(Paragraph(formatted_item, content_style))
        table_data.append(formatted_row)

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00acc1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])

   
    if len(headers) == 8:
        col_widths = [0.8*inch, 0.7*inch, 1.1*inch, 1.2*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.4*inch]
    elif len(headers) == 9: 
      
        col_widths = [
            0.8*inch,  
            0.6*inch,   
            0.8*inch,   
            0.8*inch,   
            0.8*inch,   
            1.0*inch,   
            0.8*inch,  
            0.8*inch,   
            1.1*inch    
        ]
    else:
        col_widths = [inch for _ in headers]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    base_filename = f"{filename_prefix}"
    if title:
        sanitized_title = ''.join(c for c in title if c.isalnum() or c.isspace()).replace(' ', '_').strip()
        if sanitized_title:
            base_filename = sanitized_title

    final_filename = f"Travel_Mithra_{base_filename}.pdf"

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{final_filename}"'
    return response

def get_filtered_routes(model, start_query, destination_query):
    matching_routes = []
    queryset = model.objects.all().order_by('departure_time')

    if start_query:
        queryset = queryset.filter(
            Q(start_point__icontains=start_query) | Q(via_stops__icontains=start_query)
        )
    if destination_query:
        queryset = queryset.filter(
            Q(destination_point__icontains=destination_query) | Q(via_stops__icontains=destination_query)
        )
    for route in queryset.distinct():
        route_points = []
        route_points.append(route.start_point.lower())
        if isinstance(route.via_stops, list):
            for stop_data in route.via_stops:
                route_points.append(stop_data.get('stop', '').lower())
        route_points.append(route.destination_point.lower())

        start_found_index = -1
        for i, point in enumerate(route_points):
            if start_query.lower() in point:
                start_found_index = i
                break

        destination_found_index = -1
        for i, point in enumerate(route_points):
            if destination_query.lower() in point:
                destination_found_index = i
                break
        if start_query and destination_query:
            if start_found_index != -1 and destination_found_index != -1 and start_found_index < destination_found_index:
                matching_routes.append(route)
        elif start_query and not destination_query:
            if start_found_index != -1:
                matching_routes.append(route)
        elif destination_query and not start_query:
            if destination_found_index != -1:
                matching_routes.append(route)
    return matching_routes

def home(request):
    return render(request, 'timetable/home.html')

def about(request):
    return render(request, 'timetable/about.html')

def contact_us(request):
    return render(request, 'timetable/contact_us.html')

def privacy_policy(request):
    return render(request, 'timetable/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'timetable/terms_of_service.html')


def search_buses(request):
    start_query = request.GET.get('start', '').strip()
    destination_query = request.GET.get('destination', '').strip()

    search_performed = bool(start_query or destination_query)

    buses = []
    if search_performed:
        buses = get_filtered_routes(BusRoute, start_query, destination_query)
    context = {
        'buses': buses,
        'search_performed': search_performed,
        'start_query': start_query,
        'destination_query': destination_query,
    }
    return render(request, 'timetable/bus_results.html', context)

def search_trains(request):
    start_query = request.GET.get('start', '').strip()
    destination_query = request.GET.get('destination', '').strip()

    search_performed = bool(start_query or destination_query)

    trains = []
    if search_performed:
        trains = get_filtered_routes(TrainRoute, start_query, destination_query)

    context = {
        'trains': trains,
        'search_performed': search_performed,
        'start_query': start_query,
        'destination_query': destination_query,
    }
    return render(request, 'timetable/train_results.html', context)


def generate_bus_pdf(request):
    start_query = request.GET.get('start', '').strip()
    destination_query = request.GET.get('destination', '').strip()

    buses_to_pdf = get_filtered_routes(BusRoute, start_query, destination_query)

    title = f"Bus Timetable for {start_query} to {destination_query}" if start_query and destination_query else "Bus Timetable"
    headers = ["Bus No.", "Type", "Arrival Time", "Departure Time", "Reaching Time", "Start Point", "Destination Point", "Via Stops"]

    data = []
    for bus in buses_to_pdf:
        data.append([
            bus.number,
            bus.bus_type,
            bus.arrival_time,
            bus.departure_time,
            bus.reaching_time,
            bus.start_point,
            bus.destination_point,
            bus.get_via_with_times()
        ])

    return generate_pdf_response(title, data, headers, filename_prefix="Bus_Timetable")


def generate_train_pdf(request):
    start_query = request.GET.get('start', '').strip()
    destination_query = request.GET.get('destination', '').strip()

    trains_to_pdf = get_filtered_routes(TrainRoute, start_query, destination_query)

    title = f"Train Timetable for {start_query} to {destination_query}" if start_query and destination_query else "Train Timetable"
    headers = ["Train No.", "Type", "Arrival Time", "Departure Time", "Reaching Time", "Days of Service", "Start Point", "Destination Point", "Via Stops"]

    data = []
    for train in trains_to_pdf:
        data.append([
            train.number,
            train.train_type,
            train.arrival_time,
            train.departure_time,
            train.reaching_time,
            train.get_days_display(),
            train.start_point,
            train.destination_point,
            train.get_via_with_times()
        ])

    return generate_pdf_response(title, data, headers, filename_prefix="Train_Timetable")


def suggest_routes(request):
    term = request.GET.get('term', '').strip()
    suggestions = set()
    if term:
        bus_routes_starts = BusRoute.objects.filter(start_point__icontains=term).values_list('start_point', flat=True)
        bus_routes_destinations = BusRoute.objects.filter(destination_point__icontains=term).values_list('destination_point', flat=True)
        bus_routes_via = BusRoute.objects.filter(via_stops__icontains=term).values_list('via_stops', flat=True)

        train_routes_starts = TrainRoute.objects.filter(start_point__icontains=term).values_list('start_point', flat=True)
        train_routes_destinations = TrainRoute.objects.filter(destination_point__icontains=term).values_list('destination_point', flat=True)
        train_routes_via = TrainRoute.objects.filter(via_stops__icontains=term).values_list('via_stops', flat=True)

        suggestions.update(bus_routes_starts)
        suggestions.update(bus_routes_destinations)
        suggestions.update(train_routes_starts)
        suggestions.update(train_routes_destinations)

        for stops_list in bus_routes_via:
            if isinstance(stops_list, list):
                for item in stops_list:
                    if 'stop' in item and term.lower() in item['stop'].lower():
                        suggestions.add(item['stop'])

        for stops_list in train_routes_via:
            if isinstance(stops_list, list):
                for item in stops_list:
                    if 'stop' in item and term.lower() in item['stop'].lower():
                        suggestions.add(item['stop'])

    final_suggestions = sorted(list(suggestions))[:15]
    return JsonResponse(final_suggestions, safe=False)