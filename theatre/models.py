from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models

from user.models import User


class Actor(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.full_name


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")

    def __str__(self):
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField(
        validators=[
            validators.MinValueValidator(
                limit_value=1, message="Theatre Hall must have at least 1 row"
            )
        ]
    )
    seats_in_row = models.IntegerField(
        validators=[
            validators.MinValueValidator(1, "There must be at least 1 seat in a row")
        ]
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} ({self.capacity})"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations"
    )


class Performance(models.Model):
    play = models.ForeignKey(
        Play, on_delete=models.CASCADE, related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall,
        on_delete=models.CASCADE,
    )
    show_time = models.DateTimeField()


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("seat", "row", "performance"),
                name="unique_seat_row_performance",
            )
        ]

    def __str__(self):
        return f"{self.performance.play} {self.performance.theatre_hall.name}: row {self.row} seat {self.seat}"

    @staticmethod
    def validate_ticket(row, seat, performance, error_to_raise):
        if not (1 <= row <= performance.theatre_hall.rows):
            raise error_to_raise(
                {"row": f"Row must be in range 1-{performance.theatre_hall.rows}"}
            )
        if not (1 <= seat <= performance.theatre_hall.seats_in_row):
            raise ValidationError(
                {
                    "seat": f"Seat must be in range 1-{performance.theatre_hall.seats_in_row}"
                }
            )

    def clean(self):
        Ticket.validate_ticket(self.row, self.seat, self.performance, ValidationError)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super().save(
            force_insert=False, force_update=False, using=None, update_fields=None
        )
