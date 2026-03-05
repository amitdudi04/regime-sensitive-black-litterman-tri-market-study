"""Ownership classification for China tickers.

Defines canonical SOE and Private ticker lists and a simple helper to classify
an input ticker as SOE or PRIVATE.
"""
from typing import List

SOE_TICKERS: List[str] = [
    '601398.SS',  # ICBC
    '601939.SS',  # CCB
    '601988.SS',  # Bank of China
    '600028.SS',  # Sinopec
    '601857.SS',  # PetroChina
    '601088.SS',  # China Shenhua
    '601668.SS',  # CSCEC
    '601390.SS'   # China Railway
]

PRIVATE_TICKERS: List[str] = [
    '000651.SZ',  # Gree
    '000333.SZ',  # Midea
    '000858.SZ',  # Wuliangye
    '002594.SZ',  # BYD
    '300750.SZ',  # CATL
    '600276.SS',  # Hengrui Pharma
    '600309.SS',  # Wanhua Chemical
    '300059.SZ'   # East Money
]


def classify_ownership(ticker: str) -> str:
    """Classify a ticker as 'SOE' or 'PRIVATE'.

    The classification is case-sensitive with standard ticker suffixes.
    If a ticker is not found in either list, returns 'PRIVATE' by default.
    """
    if ticker in SOE_TICKERS:
        return 'SOE'
    if ticker in PRIVATE_TICKERS:
        return 'PRIVATE'
    # Default: conservative choice treat unknown as PRIVATE
    return 'PRIVATE'
