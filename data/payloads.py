import uuid

# Учётные данные из документации Restful Booker
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"


def booking_payload(**overrides):
    """Тело запроса для создания бронирования.

    Имя уникальное: API общий для всех, и так тест находит
    именно своё бронирование, а не чужое с таким же именем.
    """
    payload = {
        "firstname": f"Aibol-{uuid.uuid4().hex[:8]}",
        "lastname": "Tester",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-01-10",
            "checkout": "2027-01-15",
        },
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload
