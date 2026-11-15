# -*- coding: utf-8 -*-
"""
Network hooks to work around tile-provider anti-scraping quirks.

Naver (map.pstatic.net) returns HTTP 500 whenever the request's
User-Agent matches the pattern `Mozilla/5.0 QGIS/<version>` — which is
exactly QGIS's default UA shape. The block is keyed off the literal
substring `QGIS/<digit>`, so any UA that does NOT match still gets a
normal HTTP 200.

This module installs a global request preprocessor that rewrites the UA
header for Naver tile requests only; every other network request in QGIS
is left untouched.

Verified 2026-05-15 via curl against map.pstatic.net:
    HTTP 500  UA="Mozilla/5.0 QGIS/4.0.1"          (QGIS default — blocked)
    HTTP 200  UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."  (after fix)
"""

import contextlib

from qgis.core import QgsNetworkAccessManager, QgsMessageLog, Qgis


NAVER_HOST = "map.pstatic.net"

# A real-looking desktop browser UA. The exact string does not matter —
# Naver's filter is keyed on the `QGIS/<digit>` substring, not on a
# whitelist — so any UA without that pattern works.
NAVER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _naver_preprocessor(request):
    # A preprocessor exception must never break unrelated network
    # traffic, so swallow anything unexpected here (no logging: this runs
    # for every request).
    with contextlib.suppress(Exception):
        if request.url().host() == NAVER_HOST:
            request.setRawHeader(b"User-Agent", NAVER_UA.encode("utf-8"))


def install():
    """Register the Naver UA preprocessor; return its ID (or None on failure)."""
    try:
        processor_id = QgsNetworkAccessManager.setRequestPreprocessor(_naver_preprocessor)
        QgsMessageLog.logMessage(
            "Installed Naver UA preprocessor (id=%s)" % processor_id,
            "TMS for Korea",
            Qgis.MessageLevel.Info,
        )
        return processor_id
    except Exception as exc:
        QgsMessageLog.logMessage(
            "Could not install Naver UA preprocessor: %s. Naver tiles may "
            "fail with HTTP 500 due to upstream UA filtering." % exc,
            "TMS for Korea",
            Qgis.MessageLevel.Warning,
        )
        return None


def uninstall(processor_id):
    if not processor_id:
        return
    with contextlib.suppress(Exception):
        QgsNetworkAccessManager.removeRequestPreprocessor(processor_id)
