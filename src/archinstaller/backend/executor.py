from __future__ import annotations
import subprocess
import threading
from collections.abc import Callable

import gi
gi.require_version("GLib", "2.0")
from gi.repository import GLib

from archinstaller.backend.exceptions import CommandFailedError


class CommandExecutor:
    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def reset(self) -> None:
        self._cancelled = False

    def run_sync(
        self,
        cmd: list[str],
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        if self._cancelled:
            raise CommandFailedError(cmd, -1, "Cancelled by user")

        if on_stdout or on_stderr:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                **kwargs,
            )
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            def _read_stream(stream, callback, collector):
                for line in iter(stream.readline, ""):
                    if self._cancelled:
                        proc.terminate()
                        return
                    collector.append(line)
                    if callback:
                        GLib.idle_add(callback, line.rstrip("\n"))
                stream.close()

            t_stdout = threading.Thread(target=_read_stream, args=(proc.stdout, on_stdout, stdout_lines))
            t_stderr = threading.Thread(target=_read_stream, args=(proc.stderr, on_stderr, stderr_lines))
            t_stdout.start()
            t_stderr.start()
            t_stdout.join()
            t_stderr.join()
            returncode = proc.wait()

            result = subprocess.CompletedProcess(cmd, returncode, stdout="".join(stdout_lines), stderr="".join(stderr_lines))
            if returncode != 0 and not self._cancelled:
                raise CommandFailedError(cmd, returncode, result.stderr.strip())
            return result
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
            if result.returncode != 0:
                raise CommandFailedError(cmd, result.returncode, result.stderr.strip())
            return result

    def run_threaded(
        self,
        cmd: list[str],
        on_complete: Callable[[], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        **kwargs,
    ) -> None:
        def _target() -> None:
            try:
                self.run_sync(cmd, on_stdout=on_stdout, on_stderr=on_stderr, **kwargs)
                if on_complete:
                    GLib.idle_add(on_complete)
            except CommandFailedError as e:
                if on_error:
                    GLib.idle_add(on_error, str(e))
        t = threading.Thread(target=_target, daemon=True)
        t.start()
