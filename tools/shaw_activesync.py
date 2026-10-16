"""Read-only capabilities negotiation for Shaw's documented ActiveSync HTTPS service.

No email content is sent, fetched or changed by this module. All requests
remain on the explicitly named, certificate-verified wm.shaw.ca endpoint.
"""
import base64
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import (
    Request, HTTPSHandler, HTTPRedirectHandler, build_opener,
)

from shaw_mail import credentials, imap_tls_context

EAS_URL = "https://wm.shaw.ca/Microsoft-Server-ActiveSync"


class NoRedirect(HTTPRedirectHandler):
    """Never forward Basic authentication to a different URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def safe_header(value, allowed):
    return "".join(ch for ch in (value or "") if ch in allowed)[:600]


def discover():
    """Return sanitized EAS support, or exact HTTP status if not accepted."""
    _, username, password = credentials()
    encoded = base64.b64encode((username + ":" + password).encode("utf-8")).decode("ascii")
    context = imap_tls_context()
    request = Request(
        EAS_URL,
        method="OPTIONS",
        headers={
            "Authorization": "Basic " + encoded,
            "User-Agent": "ShawMailBridge/1.0",
            "MS-ASProtocolVersion": "12.1",
        },
    )
    opener = build_opener(NoRedirect(), HTTPSHandler(context=context))

    try:
        try:
            response = opener.open(request, timeout=20)
        except HTTPError as error:
            response = error
        with response:
            code = int(response.status)
            headers = response.headers
            versions = safe_header(
                headers.get("MS-ASProtocolVersions"),
                frozenset("0123456789., "),
            )
            commands = safe_header(
                headers.get("MS-ASProtocolCommands"),
                frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz, "),
            )
            return {
                "http_status": code,
                "auth_accepted": code == 200,
                "protocol_versions": versions.split(",") if versions else [],
                "supports_sendmail": "SendMail" in commands.split(","),
                "commands_advertised": bool(commands),
            }
    except ssl.SSLError:
        return {"error": "tls_failure"}
    except URLError:
        return {"error": "network_failure"}
    except OSError:
        return {"error": "network_failure"}
