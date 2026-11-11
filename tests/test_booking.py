import allure
import pytest
from jsonschema import validate

from data import schemas
from data.payloads import booking_payload


@allure.epic("Restful Booker API")
@allure.feature("Бронирования")
class TestBooking:

    # ---------- Создание и чтение ----------

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Бронирование создаётся с переданными данными")
    def test_create_booking(self, client, token):
        payload = booking_payload()

        response = client.create_booking(payload)

        assert response.status_code == 200
        body = response.json()
        validate(body, schemas.CREATED_BOOKING)
        assert body["booking"] == payload

        client.delete_booking(body["bookingid"], token=token)  # уборка

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Созданное бронирование можно получить по id")
    def test_get_booking(self, client, created_booking):
        booking_id, payload = created_booking

        response = client.get_booking(booking_id)

        assert response.status_code == 200
        validate(response.json(), schemas.BOOKING)
        assert response.json() == payload

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Бронирование находится в списке по имени и фамилии")
    def test_filter_by_name(self, client, created_booking):
        booking_id, payload = created_booking

        response = client.get_booking_ids(firstname=payload["firstname"],
                                          lastname=payload["lastname"])

        assert response.status_code == 200
        validate(response.json(), schemas.BOOKING_IDS)
        assert {"bookingid": booking_id} in response.json()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Несуществующее бронирование возвращает 404")
    def test_get_nonexistent_booking(self, client):
        response = client.get_booking(999_999_999)

        assert response.status_code == 404

    # ---------- Обновление ----------

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("PUT полностью заменяет данные бронирования")
    def test_update_booking(self, client, token, created_booking):
        booking_id, _ = created_booking
        new_payload = booking_payload(totalprice=300, depositpaid=False,
                                      additionalneeds="Late checkout")

        response = client.update_booking(booking_id, new_payload, token=token)

        assert response.status_code == 200
        assert response.json() == new_payload
        # Проверяем, что изменения действительно сохранились, а не только вернулись в ответе
        assert client.get_booking(booking_id).json() == new_payload

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("PATCH меняет только переданные поля")
    def test_partial_update_booking(self, client, token, created_booking):
        booking_id, payload = created_booking

        response = client.partial_update_booking(
            booking_id, {"totalprice": 999, "additionalneeds": "Dinner"}, token=token)

        assert response.status_code == 200
        expected = {**payload, "totalprice": 999, "additionalneeds": "Dinner"}
        assert response.json() == expected

    # ---------- Удаление ----------

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Удалённое бронирование больше не находится")
    def test_delete_booking(self, client, token, created_booking):
        booking_id, _ = created_booking

        response = client.delete_booking(booking_id, token=token)

        # Особенность API: успешное удаление возвращает 201, а не 200 или 204
        assert response.status_code == 201
        assert client.get_booking(booking_id).status_code == 404

    # ---------- Безопасность ----------

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Без токена нельзя {action}")
    @pytest.mark.parametrize("action", ["обновить", "частично обновить", "удалить"],
                             ids=["put", "patch", "delete"])
    def test_changes_require_token(self, client, created_booking, action):
        booking_id, payload = created_booking
        requests_by_action = {
            "обновить": lambda: client.update_booking(booking_id, booking_payload()),
            "частично обновить": lambda: client.partial_update_booking(booking_id, {"totalprice": 1}),
            "удалить": lambda: client.delete_booking(booking_id),
        }

        response = requests_by_action[action]()

        assert response.status_code == 403
        # Данные не изменились
        assert client.get_booking(booking_id).json() == payload

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("С поддельным токеном нельзя удалить бронирование")
    def test_delete_with_invalid_token(self, client, created_booking):
        booking_id, _ = created_booking

        response = client.delete_booking(booking_id, token="fake-token")

        assert response.status_code == 403
        assert client.get_booking(booking_id).status_code == 200

    # ---------- Валидация ----------

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Создание без обязательного поля «{missing_field}» отклоняется")
    @pytest.mark.parametrize("missing_field", ["firstname", "lastname", "totalprice", "bookingdates"])
    @pytest.mark.xfail(reason="Известный баг API: вместо 400 Bad Request возвращает 500", strict=False)
    def test_create_without_required_field(self, client, missing_field):
        payload = booking_payload()
        del payload[missing_field]

        response = client.create_booking(payload)

        # Правильное поведение — ошибка клиента 400, а не падение сервера 500
        assert response.status_code == 400
