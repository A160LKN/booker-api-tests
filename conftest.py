import os

import pytest

from api.client import BookerClient
from data.payloads import ADMIN_PASSWORD, ADMIN_USERNAME, new_booking

# Адрес API. Для другого стенда: BOOKER_URL=http://localhost:3001 pytest
BASE_URL = os.getenv("BOOKER_URL", "https://restful-booker.herokuapp.com")


@pytest.fixture(scope="session")
def client():
    """Один клиент на весь прогон."""
    return BookerClient(BASE_URL)


@pytest.fixture(scope="session")
def token(client):
    """Токен администратора: запрашивается один раз на весь прогон."""
    response = client.auth(ADMIN_USERNAME, ADMIN_PASSWORD)
    assert response.status_code == 200, "Не удалось получить токен"
    return response.json()["token"]


@pytest.fixture
def created_booking(client, token):
    """Создаёт бронирование перед тестом и удаляет после.

    Возвращает (booking_id, booking) — id и модель Booking, с которой оно создано.
    """
    booking = new_booking()
    response = client.create_booking(booking.to_json())
    assert response.status_code == 200, "Не удалось создать бронирование"
    booking_id = response.json()["bookingid"]

    yield booking_id, booking

    # Уборка: тест мог уже удалить бронирование сам — тогда API вернёт 405, это нормально
    client.delete_booking(booking_id, token=token)
