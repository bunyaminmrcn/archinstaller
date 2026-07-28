from enum import IntEnum, StrEnum, auto


class StepID(IntEnum):
    WELCOME = 0
    LOCATION = 1
    PARTITIONING = 2
    FILESYSTEMS = 3
    USERS = 4
    DESKTOP = 5
    BOOTLOADER = 6
    SUMMARY = 7
    INSTALL = 8


class FilesystemType(StrEnum):
    EXT4 = "ext4"
    BTRFS = "btrfs"
    XFS = "xfs"
    F2FS = "f2fs"
    FAT32 = "vfat"
    SWAP = "swap"
    NTFS = "ntfs"


class BootloaderType(StrEnum):
    GRUB_BIOS = "grub-bios"
    GRUB_UEFI = "grub-efi"
    SYSTEMD_BOOT = "systemd-boot"


class AurHelper(StrEnum):
    YAY = "yay"
    PARU = "paru"


class DesktopEnvironment(StrEnum):
    GNOME = "gnome"
    KDE_PLASMA = "plasma"
    XFCE = "xfce"
    CINNAMON = "cinnamon"
    MATE = "mate"
    BUDGIE = "budgie"
    SWAY = "sway"
    HYPRLAND = "hyprland"
    I3 = "i3"
    NONE = "none"


class PartitionRole(StrEnum):
    ROOT = "root"
    HOME = "home"
    ESP = "esp"
    SWAP = "swap"
    BOOT = "boot"
    DATA = "data"


DE_METAPACKAGES: dict[DesktopEnvironment, list[str]] = {
    DesktopEnvironment.GNOME: ["gnome", "gnome-extra"],
    DesktopEnvironment.KDE_PLASMA: ["plasma-meta", "kde-applications-meta"],
    DesktopEnvironment.XFCE: ["xfce4", "xfce4-goodies"],
    DesktopEnvironment.CINNAMON: ["cinnamon"],
    DesktopEnvironment.MATE: ["mate", "mate-extra"],
    DesktopEnvironment.BUDGIE: ["budgie-desktop"],
    DesktopEnvironment.SWAY: ["sway", "swaybg", "swaylock", "swayidle", "foot"],
    DesktopEnvironment.HYPRLAND: ["hyprland", "kitty", "waybar"],
    DesktopEnvironment.I3: ["i3-wm", "i3status", "i3lock", "dmenu"],
    DesktopEnvironment.NONE: [],
}

EXTRA_PACKAGE_GROUPS: dict[str, list[str]] = {
    "Printing Support": ["cups", "cups-pdf", "ghostscript", "system-config-printer"],
    "Audio (PipeWire)": ["pipewire", "pipewire-pulse", "pipewire-alsa", "wireplumber"],
    "Bluetooth": ["bluez", "bluez-utils", "blueman"],
    "Development Tools": ["base-devel", "git", "gcc", "make"],
    "Firefox Browser": ["firefox"],
    "LibreOffice Suite": ["libreoffice-fresh"],
    "Gaming (Steam + Vulkan)": ["steam", "vulkan-radeon", "vulkan-intel", "lib32-vulkan-radeon", "lib32-vulkan-intel"],
    "Virtualization (QEMU/KVM)": ["qemu-full", "libvirt", "virt-manager", "dnsmasq", "edk2-ovmf"],
    "Security Tools": ["firewalld", "nftables", "openssh"],
}

AVAILABLE_LOCALES = [
    "en_US.UTF-8", "en_GB.UTF-8", "de_DE.UTF-8", "fr_FR.UTF-8",
    "es_ES.UTF-8", "it_IT.UTF-8", "pt_BR.UTF-8", "pt_PT.UTF-8",
    "ru_RU.UTF-8", "ja_JP.UTF-8", "zh_CN.UTF-8", "zh_TW.UTF-8",
    "ko_KR.UTF-8", "ar_SA.UTF-8", "nl_NL.UTF-8", "pl_PL.UTF-8",
    "sv_SE.UTF-8", "tr_TR.UTF-8", "cs_CZ.UTF-8", "uk_UA.UTF-8",
    "fi_FI.UTF-8", "da_DK.UTF-8", "nb_NO.UTF-8", "hu_HU.UTF-8",
    "el_GR.UTF-8", "ro_RO.UTF-8", "sk_SK.UTF-8", "bg_BG.UTF-8",
    "hr_HR.UTF-8", "sr_RS.UTF-8",
]

AVAILABLE_KEYBOARDS = [
    "us", "uk", "de", "fr", "es", "it", "pt", "br",
    "ru", "jp", "cn", "kr", "ar", "nl", "pl", "se",
    "tr", "cz", "ua", "fi", "dk", "no", "hu", "gr",
    "ro", "sk", "bg", "hr", "rs", "be", "ch", "ca",
]

TIMEZONE_REGIONS: dict[str, list[str]] = {
    "Africa": ["Africa/Cairo", "Africa/Johannesburg", "Africa/Lagos", "Africa/Nairobi"],
    "America": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
                "America/Toronto", "America/Vancouver", "America/Mexico_City",
                "America/Sao_Paulo", "America/Argentina/Buenos_Aires"],
    "Asia": ["Asia/Tokyo", "Asia/Shanghai", "Asia/Seoul", "Asia/Kolkata",
             "Asia/Dubai", "Asia/Singapore", "Asia/Bangkok", "Asia/Jerusalem"],
    "Australia": ["Australia/Sydney", "Australia/Melbourne", "Australia/Perth", "Australia/Brisbane"],
    "Europe": ["Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
               "Europe/Rome", "Europe/Madrid", "Europe/Amsterdam", "Europe/Warsaw",
               "Europe/Stockholm", "Europe/Istanbul", "Europe/Kiev"],
    "Pacific": ["Pacific/Auckland", "Pacific/Fiji", "Pacific/Honolulu"],
}

MIRROR_COUNTRIES = {
    "Worldwide": "Worldwide",
    "Australia": "Australia",
    "Austria": "Austria",
    "Belgium": "Belgium",
    "Brazil": "Brazil",
    "Canada": "Canada",
    "Chile": "Chile",
    "China": "China",
    "Czechia": "Czechia",
    "Denmark": "Denmark",
    "Finland": "Finland",
    "France": "France",
    "Germany": "Germany",
    "Greece": "Greece",
    "Hong Kong": "Hong Kong",
    "India": "India",
    "Indonesia": "Indonesia",
    "Iran": "Iran",
    "Italy": "Italy",
    "Japan": "Japan",
    "Netherlands": "Netherlands",
    "New Zealand": "New Zealand",
    "Norway": "Norway",
    "Poland": "Poland",
    "Portugal": "Portugal",
    "Romania": "Romania",
    "Russia": "Russia",
    "Singapore": "Singapore",
    "South Africa": "South Africa",
    "South Korea": "South Korea",
    "Spain": "Spain",
    "Sweden": "Sweden",
    "Switzerland": "Switzerland",
    "Taiwan": "Taiwan",
    "Thailand": "Thailand",
    "Turkey": "Turkey",
    "United Kingdom": "United Kingdom",
    "United States": "United States",
    "Vietnam": "Vietnam",
}
