import json

import allure
import requests


class BookerClient:
    """Клиент API Restful Booker: один метод на один эндпоинт."""

    def __init__(self, base_url, timeout=15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Session переиспользует соединение и хранит общие заголовки
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        # Каждый ответ автоматически прикрепляется к Allure-отчёту
        self.session.hooks["response"].append(self._attach_to_allure)

    # ---------- Служебное ----------

    def _request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    @staticmethod
    def _auth_cookie(token):
        # API принимает токен в cookie: Cookie: token=<значение>
        return {"Cookie": f"token={token}"} if token else {}

    @staticmethod
    def _attach_to_allure(response, *args, **kwargs):
        request = response.request
        body = request.body.decode() if isinstance(request.body, bytes) else request.body
        allure.attach(
            f"{request.method} {request.url}\n\n{body or ''}",
            name=f"Запрос: {request.method} {request.path_url}",
            attachment_type=allure.attachment_type.TEXT,
        )
        try:
            text = json.dumps(response.json(), ensure_ascii=False, indent=2)
            attachment_type = allure.attachment_type.JSON
        except ValueError:
            text = response.text
            attachment_type = allure.attachment_type.TEXT
        allure.attach(
            text,
            name=f"Ответ: {response.status_code}",
            attachment_type=attachment_type,
        )

    # ---------- Эндпоинты ----------

    @allure.step("GET /ping — проверка доступности")
    def ping(self):
        return self._request("GET", "/ping")

    @allure.step("POST /auth — получить токен для «{username}»")
    def auth(self, username, password):
        return self._request("POST", "/auth", json={"username": username, "password": password})

    @allure.step("GET /booking — список бронирований")
    def get_booking_ids(self, **filters):
        return self._request("GET", "/booking", params=filters)

    @allure.step("GET /booking/{booking_id} — получить бронирование")
    def get_booking(self, booking_id):
        return self._request("GET", f"/booking/{booking_id}")

    @allure.step("POST /booking — создать бронирование")
    def create_booking(self, payload):
        return self._request("POST", "/booking", json=payload)

    @allure.step("PUT /booking/{booking_id} — полностью обновить бронирование")
    def update_booking(self, booking_id, payload, token=None):
        return self._request("PUT", f"/booking/{booking_id}", json=payload,
                             headers=self._auth_cookie(token))

    @allure.step("PATCH /booking/{booking_id} — частично обновить бронирование")
    def partial_update_booking(self, booking_id, payload, token=None):
        return self._request("PATCH", f"/booking/{booking_id}", json=payload,
                             headers=self._auth_cookie(token))

    @allure.step("DELETE /booking/{booking_id} — удалить бронирование")
    def delete_booking(self, booking_id, token=None):
        return self._request("DELETE", f"/booking/{booking_id}",
                             headers=self._auth_cookie(token))
