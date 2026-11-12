"""Модели данных API на Pydantic.

Одна модель — и тело запроса, и проверка ответа. Pydantic проверяет:
- обязательные поля и их типы — строго: «150» вместо 150 считается ошибкой;
- лишние поля: если API начнёт возвращать что-то новое, тест об этом скажет;
- формат дат и правило «выезд не раньше заезда».
"""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, model_validator


class ApiModel(BaseModel):
    # extra="forbid" — неизвестное поле в ответе считается ошибкой контракта
    model_config = ConfigDict(extra="forbid")


class BookingDates(ApiModel):
    checkin: date
    checkout: date

    @model_validator(mode="after")
    def checkout_not_before_checkin(self):
        if self.checkout < self.checkin:
            raise ValueError("дата выезда раньше даты заезда")
        return self


class Booking(ApiModel):
    firstname: StrictStr = Field(min_length=1)
    lastname: StrictStr = Field(min_length=1)
    totalprice: StrictInt = Field(ge=0)
    depositpaid: StrictBool
    bookingdates: BookingDates
    additionalneeds: StrictStr | None = None

    def to_json(self):
        """Тело запроса: даты — строками, пустые необязательные поля не отправляются."""
        return self.model_dump(mode="json", exclude_none=True)


class CreatedBooking(ApiModel):
    """Ответ на POST /booking"""
    bookingid: StrictInt
    booking: Booking


class BookingId(ApiModel):
    """Элемент списка GET /booking"""
    bookingid: StrictInt


class Token(ApiModel):
    """Ответ на POST /auth с верными данными"""
    token: StrictStr = Field(min_length=1)


class AuthError(ApiModel):
    """Ответ на POST /auth с неверными данными — API возвращает его со статусом 200"""
    reason: StrictStr
