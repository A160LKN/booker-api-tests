import allure
from jsonschema import validate

from data import schemas
from data.payloads import ADMIN_PASSWORD, ADMIN_USERNAME


@allure.epic("Restful Booker API")
@allure.feature("Доступность")
class TestHealth:

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Сервис отвечает на /ping")
    def test_ping(self, client):
        response = client.ping()

        # По документации /ping возвращает 201 Created — нестандартно, но так задумано
        assert response.status_code == 201


@allure.epic("Restful Booker API")
@allure.feature("Авторизация")
class TestAuth:

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("С верными данными выдаётся токен")
    def test_auth_success(self, client):
        response = client.auth(ADMIN_USERNAME, ADMIN_PASSWORD)

        assert response.status_code == 200
        validate(response.json(), schemas.TOKEN)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("С неверным паролем токен не выдаётся")
    def test_auth_wrong_password(self, client):
        response = client.auth(ADMIN_USERNAME, "wrong_password")

        # Известная особенность API: ошибка приходит со статусом 200, а не 401.
        # Поэтому проверяем тело ответа, а не только код.
        assert response.status_code == 200
        assert response.json() == {"reason": "Bad credentials"}
        assert "token" not in response.json()
