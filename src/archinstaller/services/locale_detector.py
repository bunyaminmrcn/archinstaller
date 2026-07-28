from archinstaller.config import InstallerConfig
from archinstaller.constants import (
    AVAILABLE_LOCALES,
    AVAILABLE_KEYBOARDS,
    TIMEZONE_REGIONS,
    MIRROR_COUNTRIES,
)


def get_available_locales() -> list[str]:
    return list(AVAILABLE_LOCALES)


def get_available_keyboards() -> list[str]:
    return list(AVAILABLE_KEYBOARDS)


def get_timezone_regions() -> dict[str, list[str]]:
    return dict(TIMEZONE_REGIONS)


def get_mirror_countries() -> dict[str, str]:
    return dict(MIRROR_COUNTRIES)
