from archinstaller.constants import (
    DesktopEnvironment,
    DE_METAPACKAGES,
    EXTRA_PACKAGE_GROUPS,
)


def get_de_packages(de: DesktopEnvironment) -> list[str]:
    return list(DE_METAPACKAGES.get(de, []))


def get_extra_package_groups() -> dict[str, list[str]]:
    return dict(EXTRA_PACKAGE_GROUPS)


def get_extra_package_names() -> list[str]:
    return list(EXTRA_PACKAGE_GROUPS.keys())
