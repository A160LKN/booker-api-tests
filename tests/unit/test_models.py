"""Проверки самих моделей — без сети, за доли секунды.

Модели — это проверка контракта API, поэтому они тоже должны быть проверены:
модель, которая пропускает неверный ответ, хуже, чем никакой.
"""
import allure
import pytest
from pydantic import ValidationError

from data.payloads import booking_payload
from models.booking import AuthError, Booking, CreatedBooking, Token

pytestmark = [pytest.mark.unit, allure.epic("Модели данных"), allure.feature("Контракт API")]


def test_valid_response_passes():
    created = CreatedBooking.model_validate({"bookingid": 1, "booking": booking_payload()})
    assert created.booking.bookingdates.checkin.isoformat() == "2027-01-10"


def test_request_body_format():
    body = booking_payload()
    assert body["bookingdates"] == {"checkin": "2027-01-10", "checkout": "2027-01-15"}
    assert isinstance(body["totalprice"], int)


def test_optional_field_is_not_sent_when_empty():
    assert "additionalneeds" not in booking_payload(additionalneeds=None)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("totalprice", "150"),        # число строкой
        ("totalprice", 150.5),        # дробная цена
        ("totalprice", -1),           # отрицательная цена
        ("depositpaid", "true"),      # булево строкой
        ("depositpaid", 1),           # булево числом
        ("firstname", ""),            # пустое имя
        ("firstname", None),          # null в обязательном поле
    ],
    ids=["price-string", "price-float", "price-negative", "deposit-string", "deposit-int", "name-empty", "name-null"],
)
def test_wrong_type_is_rejected(field, value):
    with pytest.raises(ValidationError):
        Booking.model_validate({**booking_payload(), field: value})


@pytest.mark.parametrize("field", ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"])
def test_missing_required_field_is_rejected(field):
    body = booking_payload()
    del body[field]
    with pytest.raises(ValidationError):
        Booking.model_validate(body)


def test_unknown_field_is_rejected():
    with pytest.raises(ValidationError, match="Extra inputs"):
        Booking.model_validate({**booking_payload(), "discount": 10})


@pytest.mark.parametrize("checkin", ["2027-02-30", "10.01.2027", "завтра"])
def test_invalid_date_is_rejected(checkin):
    body = booking_payload()
    body["bookingdates"]["checkin"] = checkin
    with pytest.raises(ValidationError):
        Booking.model_validate(body)


def test_checkout_before_checkin_is_rejected():
    body = booking_payload()
    body["bookingdates"] = {"checkin": "2027-01-15", "checkout": "2027-01-10"}
    with pytest.raises(ValidationError, match="дата выезда раньше даты заезда"):
        Booking.model_validate(body)


def test_same_day_checkout_is_allowed():
    body = booking_payload()
    body["bookingdates"] = {"checkin": "2027-01-10", "checkout": "2027-01-10"}
    Booking.model_validate(body)


def test_auth_error_with_token_is_rejected():
    """Если API вернёт токен вместе с ошибкой — это баг безопасности, модель его поймает."""
    with pytest.raises(ValidationError):
        AuthError.model_validate({"reason": "Bad credentials", "token": "abc"})


def test_empty_token_is_rejected():
    with pytest.raises(ValidationError):
        Token.model_validate({"token": ""})
