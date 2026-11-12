import uuid
from datetime import date

from models.booking import Booking, BookingDates

# Учётные данные из документации Restful Booker
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"


def new_booking(**overrides) -> Booking:
    """Бронирование для теста.

    Имя уникальное: API общий для всех, и так тест находит
    именно своё бронирование, а не чужое с таким же именем.
    """
    data = {
        "firstname": f"Aibol-{uuid.uuid4().hex[:8]}",
        "lastname": "Tester",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": BookingDates(checkin=date(2027, 1, 10), checkout=date(2027, 1, 15)),
        "additionalneeds": "Breakfast",
    }
    data.update(overrides)
    return Booking(**data)


def booking_payload(**overrides) -> dict:
    """То же бронирование в виде тела запроса (JSON)."""
    return new_booking(**overrides).to_json()
