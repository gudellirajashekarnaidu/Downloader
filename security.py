"""URL validation and SSRF protection.

Every URL a user sends is checked here before the server touches it. A link is
rejected if it isn't plain http(s), carries credentials, uses an unusual port,
or resolves to anything other than a public internet address.

Known limit: we resolve the hostname to check it, and the HTTP client resolves
it again when it connects. A hostile DNS server could answer differently the
second time (DNS rebinding). For a public deployment, also block private
ranges at the network level (egress firewall) as a second layer.
"""
import ipaddress
import socket
from urllib.parse import urlparse

from . import config


class UnsafeURL(ValueError):
    """The link can't be used. The message is safe to show to the user."""


def is_public_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip.split("%")[0])  # drop IPv6 zone id
    if addr.version == 6 and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped  # ::ffff:127.0.0.1 is still loopback
    return addr.is_global and not addr.is_multicast


def resolve_public(host: str, port: int) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise UnsafeURL("We couldn't find that website. Check the link and try again.")
    ips = sorted({info[4][0] for info in infos})
    if not ips:
        raise UnsafeURL("We couldn't find that website. Check the link and try again.")
    if not all(is_public_ip(ip) for ip in ips):
        raise UnsafeURL("That link points to a private or internal address, so it can't be used.")
    return ips


def validate_url(raw: str) -> str:
    """Return a cleaned URL, or raise UnsafeURL with a user-facing message."""
    url = (raw or "").strip()
    if not url:
        raise UnsafeURL("Paste a link to get started.")
    if len(url) > 2048:
        raise UnsafeURL("That link is too long.")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURL("Links must start with http:// or https://.")
    if not parsed.hostname:
        raise UnsafeURL("That doesn't look like a valid link.")
    if parsed.username or parsed.password:
        raise UnsafeURL("Links that contain a username or password aren't supported.")

    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        raise UnsafeURL("That doesn't look like a valid link.")
    if port not in config.ALLOWED_PORTS:
        raise UnsafeURL("Links with a custom port aren't supported.")

    resolve_public(parsed.hostname, port)
    return url


def match_platform(url: str) -> str | None:
    """Name of the supported platform this link belongs to, if any."""
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    for suffix, label in config.EXTRACTOR_PLATFORMS.items():
        if host == suffix or host.endswith("." + suffix):
            return label
    return None
