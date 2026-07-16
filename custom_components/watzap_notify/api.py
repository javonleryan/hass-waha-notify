import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class WahaApiClient:
    def __init__(
        self,
        base_url: str,
        cf_access_client_id: str,
        cf_access_client_secret: str,
        session_name: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._session_name = session_name
        self._headers = {
            "Content-Type": "application/json",
            "CF-Access-Client-Id": cf_access_client_id,
            "CF-Access-Client-Secret": cf_access_client_secret,
        }

    async def validate(self):
        url = f"{self._base_url}/api/sessions/{self._session_name}"
        async with self._session.get(url, headers=self._headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _post(self, endpoint: str, payload: dict):
        url = f"{self._base_url}{endpoint}"
        async with self._session.post(url, headers=self._headers, json=payload) as resp:
            resp.raise_for_status()
            if resp.content_type == "application/json":
                return await resp.json()
            return await resp.text()

    async def send_text(self, chat_id: str, message: str):
        return await self._post(
            "/api/sendText",
            {
                "session": self._session_name,
                "chatId": chat_id,
                "text": message,
            },
        )

    async def send_image(self, chat_id: str, image_url: str, caption: str = ""):
        return await self._post(
            "/api/sendImage",
            {
                "session": self._session_name,
                "chatId": chat_id,
                "file": {"url": image_url},
                "caption": caption,
            },
        )