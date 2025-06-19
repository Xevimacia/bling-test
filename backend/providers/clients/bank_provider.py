import requests
from datetime import datetime


class BanBankProviderClient:
    base_url = "https://bankprovider.com/"

    def create_card(self, user_external_id: str, color: str) -> dict:
        """
        ----------
        Provider endpoint documentation:
        ----------
        path: "/api/v2/card/"
        verb: POST
        accept: JSON
        input data:
         - user_id (user external id)
         - color (COLOR_1, COLOR_2) -> Mapping: COLOR_1=PINK, COLOR_2=BLACK
        responses:
         - 201:
         {"expiration_date": datetime, "id": string,
         "color": str ["COLOR_1" (PINK), "COLOR_2" (BLACK)],
         "status": str ["ORDERED", "SENT", "ACTIVATED", "CANCELLED", "EXPIRED", "OPPOSED", "FAILED"]}
         - 400: {"error": "Invalid input"}
         - 500: {"error": "Provider internal error"}
         ------------
        """
        # Simulate API call
        if user_external_id == "invalid_user_id":
            raise requests.exceptions.HTTPError("User not found at provider", response=type('obj', (object,), {'status_code': 400})())
        if color not in ["black", "pink"]:
             raise requests.exceptions.HTTPError("Invalid color", response=type('obj', (object,), {'status_code': 400})())
        if user_external_id == "provider_error":
            raise requests.exceptions.HTTPError("Provider internal error", response=type('obj', (object,), {'status_code': 500})())


        # Simulate successful response
        provider_color = "COLOR_1" if color == "pink" else "COLOR_2"
        return {
            "expiration_date": datetime.now().isoformat(),
            "id": f"prov_card_{user_external_id}_{color}_{datetime.now().timestamp()}",
            "color": provider_color,
            "status": "ORDERED"
        }
