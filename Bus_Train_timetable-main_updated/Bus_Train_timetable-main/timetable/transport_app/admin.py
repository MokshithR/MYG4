from django import forms
from django.contrib import admin
from django.db import models
from transport_app.models import BusRoute, TrainRoute, DAY_CHOICES
from timetable.widgets import SimpleJSONTextarea
class BusRouteAdminForm(forms.ModelForm):
    class Meta:
        model = BusRoute
        fields = '__all__'
        widgets = {
            'via_stops': SimpleJSONTextarea(),
        }

@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    form = BusRouteAdminForm
    list_display = (
        'number', 'bus_type', 'start_point', 'destination_point',
        'arrival_time', 'departure_time', 'reaching_time',
        'get_via_stops_display',
    )
    search_fields = (
        'number', 'start_point', 'destination_point', 'via_stops'
    )
    list_filter = ('bus_type', 'start_point', 'destination_point')
    ordering = ('number',)

    def get_via_stops_display(self, obj):
        if isinstance(obj.via_stops, list) and obj.via_stops:
            return ", ".join([f"{item.get('stop', 'N/A')} ({item.get('time', 'N/A')})" for item in obj.via_stops])
        return "N/A"
    get_via_stops_display.short_description = "Via Stops"

class TrainRouteAdminForm(forms.ModelForm):
    days_of_service = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select days the train operates."
    )

    class Meta:
        model = TrainRoute
        fields = '__all__'
        widgets = {
            'via_stops': SimpleJSONTextarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.days_of_service:
            self.initial['days_of_service'] = [
                d.strip() for d in self.instance.days_of_service.split(',') if d.strip()
            ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_days = sorted(self.cleaned_data['days_of_service'], key=lambda x: [d[0] for d in DAY_CHOICES].index(x))
        instance.days_of_service = ",".join(selected_days)
        if commit:
            instance.save()
        return instance


@admin.register(TrainRoute)
class TrainRouteAdmin(admin.ModelAdmin):
    form = TrainRouteAdminForm
    list_display = (
        'number', 'train_type', 'start_point', 'destination_point',
        'arrival_time', 'departure_time', 'reaching_time',
        'get_via_stops_display', 'get_days_display',
    )
    search_fields = (
        'number', 'start_point', 'destination_point', 'via_stops'
    )
    list_filter = ('train_type', 'start_point', 'destination_point', 'days_of_service')
    ordering = ('number',)

    def get_via_stops_display(self, obj):
        if isinstance(obj.via_stops, list) and obj.via_stops:
            return ", ".join([f"{item.get('stop', 'N/A')} ({item.get('time', 'N/A')})" for item in obj.via_stops])
        return "N/A"
    get_via_stops_display.short_description = "Via Stops"

    def get_days_display(self, obj):
        return obj.get_days_display()
    get_days_display.short_description = "Days of Service"