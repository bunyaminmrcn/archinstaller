import subprocess


def run_reflector(country: str = "", latest: int = 10, protocol: str = "https") -> str | None:
    cmd = ["reflector", "--latest", str(latest), "--protocol", protocol, "--sort", "rate", "--save", "/etc/pacman.d/mirrorlist"]
    if country and country != "Worldwide":
        cmd.extend(["--country", country])
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        with open("/etc/pacman.d/mirrorlist") as f:
            return f.read()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def update_mirrorlist(country: str = "") -> bool:
    return run_reflector(country) is not None
