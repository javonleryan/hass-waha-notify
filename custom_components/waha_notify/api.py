import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class WahaApiClient:
    def __init__(
        self,
        base_url: str,
        cf_access_client_id: str,
        cf_access_client_secret: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._headers = {
            "CF-Access-Client-Id": cf_access_client_id,
            "CF-Access-Client-Secret": cf_access_client_secret,
        }

    async def _post_form(self, endpoint: str, payload: dict):
        url = f"{self._base_url}{endpoint}"
        async with self._session.post(url, headers=self._headers, data=payload) as resp:
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await resp.json()
            return await resp.text()

    async def check_phone(self, phone: str, session_name: str):
        return await self._post_form(
            f"/api/waha/{session_name}/check_phone",
            {"phone": phone},
        )

    async def send_personal(self, phone: str, message: str, session_name: str):
        return await self._post_form(
            f"/api/waha/{session_name}/send_message",
            {
                "session": session_name,
                "phone": phone,
                "data": message,
                "type": "message",
            },
        )

    async def send_group(self, group_id: str, message: str, session_name: str):
        return await self._post_form(
            f"/api/waha/{session_name}/send_message",
            {
                "session": session_name,
                "phone": group_id,
                "data": message,
                "type": "message",
            },
        )