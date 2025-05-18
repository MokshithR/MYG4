from django.db import models
from django.utils import timezone

DAY_CHOICES = (
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
)

class BusRoute(models.Model):
    number = models.CharField(max_length=50, unique=True, help_text="KA21Fxyza")
    bus_type = models.CharField(
        max_length=50,
        choices=[
            ('AC', 'AC'),
            ('Non-AC', 'Non-AC'),
            ('Sleeper', 'Sleeper'),
            ('Ordinary', 'Ordinary'),
            ('Express', 'Express'),
        ],
        default='Ordinary',
        help_text="Type of bus (e.g., AC, Non-AC, Sleeper)."
    )
    start_point = models.CharField(max_length=100, help_text="Starting location of the bus route.")
    destination_point = models.CharField(max_length=100, help_text="Destination location of the bus route.")
    arrival_time = models.DateTimeField(help_text="Scheduled arrival time at the start point.")
    departure_time = models.DateTimeField(help_text="Scheduled departure time from the start point.")
    reaching_time = models.DateTimeField(help_text="Scheduled reaching time at the destination point.")
    via_stops = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text=" [Type like this {'stop': 'City A', 'time': 'HH:MM AM/PM'}]."
    )

    class Meta:
        verbose_name = "Bus Route"
        verbose_name_plural = "Bus Routes"
        ordering = ['departure_time'] 
    def __str__(self):
        return f"Bus {self.number}: {self.start_point} to {self.destination_point} (Departs: {self.departure_time.strftime('%Y-%m-%d %H:%M')})"

    def get_via_with_times(self):
        if not isinstance(self.via_stops, list):
            return []
        return [(item.get('stop', 'N/A'), item.get('time', 'N/A')) for item in self.via_stops]


class TrainRoute(models.Model):
    number = models.CharField(max_length=50, unique=True, help_text="Enter the no of train.")
    train_type = models.CharField(
        max_length=50,
        choices=[
            ('Express', 'Express'),
            ('Local', 'Local'),
            ('Passenger', 'Passenger'),
        ],
        default='Express',
        help_text="Type of train (e.g., Express, Local, Passenger)."
    )
    start_point = models.CharField(max_length=100, help_text="Starting station of the train route.")
    destination_point = models.CharField(max_length=100, help_text="Destination station of the train route.")
    arrival_time = models.DateTimeField(help_text="Scheduled arrival time at the start station.")
    departure_time = models.DateTimeField(help_text="Scheduled departure time from the start station.")
    reaching_time = models.DateTimeField(help_text="Scheduled reaching time at the destination station.")
    via_stops = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of intermediate stations (Type like this()This is for Bhavish B[{'stop': 'Station A', 'time': 'HH:MM AM/PM'}])."
    )
    days_of_service = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="Comma-separated list of days the train operates (e.g., 'MON,WED,FRI')."
    )

    class Meta:
        verbose_name = "Train Route"
        verbose_name_plural = "Train Routes"
        ordering = ['departure_time']
    def __str__(self):
        return f"Train {self.number}: {self.start_point} to {self.destination_point} (Departs: {self.departure_time.strftime('%Y-%m-%d %H:%M')})"

    def get_via_with_times(self):
        if not isinstance(self.via_stops, list):
            return []
        return [(item.get('stop', 'N/A'), item.get('time', 'N/A')) for item in self.via_stops]

    def get_days_display(self):
        if self.days_of_service:
            day_codes = [d.strip() for d in self.days_of_service.split(',') if d.strip()]
            day_map = dict(DAY_CHOICES)
            display_names = [day_map.get(code, code) for code in day_codes] 
            return ", ".join(display_names)
        return "N/A"