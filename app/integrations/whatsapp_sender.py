import requests
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logger import request_logger


def _wa_url() -> str:
    return settings.waofficial_base_url.rstrip("/")


def _wa_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def send_whatsapp_message(
    recipient_number: str,
    message_text: str,
    phone_number_id: str,
    whatsapp_token: str,
) -> Optional[Dict[str, Any]]:
    try:
        response = requests.post(
            _wa_url(),
            json={
                "to": recipient_number,
                "phoneNoId": phone_number_id,
                "type": "text",
                "text": message_text,
            },
            headers=_wa_headers(whatsapp_token),
            timeout=10,
        )

        if response.status_code not in [200, 201]:
            request_logger.error(
                f"WhatsApp API error: Status {response.status_code}, {response.text}"
            )
            return None

        data = response.json()
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
        }

    except requests.exceptions.Timeout:
        request_logger.error("WhatsApp API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        request_logger.error(f"WhatsApp API request error: {str(e)}")
        return None
    except Exception as e:
        request_logger.error(f"Error sending WhatsApp message: {str(e)}")
        return None


def send_template_message(
    recipient_number: str,
    template_name: str,
    template_language: str,
    parameters: Optional[list] = None,
    phone_number_id: str = None,
    whatsapp_token: str = None,
) -> Optional[Dict[str, Any]]:
    try:
        template_body: Dict[str, Any] = {
            "name": template_name,
            "language": {"code": template_language},
        }
        if parameters:
            template_body["components"] = [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in parameters],
                }
            ]

        response = requests.post(
            _wa_url(),
            json={
                "to": recipient_number,
                "phoneNoId": phone_number_id,
                "type": "template",
                "template": template_body,
            },
            headers=_wa_headers(whatsapp_token),
            timeout=10,
        )

        if response.status_code not in [200, 201]:
            request_logger.error(
                f"WhatsApp template API error: Status {response.status_code}, {response.text}"
            )
            return None

        data = response.json()
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
            "template": template_name,
        }

    except Exception as e:
        request_logger.error(f"Error sending WhatsApp template: {str(e)}")
        return None


def send_interactive_list(
    recipient_number: str,
    header: str,
    body: str,
    button_text: str,
    sections: list,
    phone_number_id: str = None,
    whatsapp_token: str = None,
) -> Optional[Dict[str, Any]]:
    """
    Send a WhatsApp interactive list message.

    sections format: [{"title": "...", "rows": [{"id": "SKU", "title": "...", "description": "..."}]}]
    Row id is returned when the user taps — set it to the SKU code for direct lookup.
    """
    if not phone_number_id or not whatsapp_token:
        return None

    try:
        response = requests.post(
            _wa_url(),
            json={
                "to": recipient_number,
                "phoneNoId": phone_number_id,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {"type": "text", "text": header},
                    "body": {"text": body},
                    "action": {"button": button_text, "sections": sections},
                },
            },
            headers=_wa_headers(whatsapp_token),
            timeout=10,
        )

        if response.status_code not in [200, 201]:
            request_logger.error(
                f"WhatsApp list API error: {response.status_code}, {response.text}"
            )
            return None

        data = response.json()
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
        }

    except Exception as e:
        request_logger.error(f"Error sending WhatsApp interactive list: {str(e)}")
        return None


def send_media_message(
    recipient_number: str,
    media_url: str,
    media_type: str,
    caption: Optional[str] = None,
    phone_number_id: str = None,
    whatsapp_token: str = None,
) -> Optional[Dict[str, Any]]:
    valid_types = ["image", "video", "audio", "document"]
    if media_type not in valid_types:
        request_logger.error(f"Invalid media type: {media_type}")
        return None

    try:
        media_payload: Dict[str, Any] = {"link": media_url}
        if caption and media_type in ["image", "video"]:
            media_payload["caption"] = caption

        response = requests.post(
            _wa_url(),
            json={
                "to": recipient_number,
                "phoneNoId": phone_number_id,
                "type": media_type,
                media_type: media_payload,
            },
            headers=_wa_headers(whatsapp_token),
            timeout=10,
        )

        if response.status_code not in [200, 201]:
            request_logger.error(
                f"WhatsApp media API error: Status {response.status_code}, {response.text}"
            )
            return None

        data = response.json()
        return {
            "message_id": data.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "recipient": recipient_number,
            "media_type": media_type,
        }

    except Exception as e:
        request_logger.error(f"Error sending WhatsApp media: {str(e)}")
        return None
