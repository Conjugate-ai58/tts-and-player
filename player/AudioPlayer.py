"""
Audio playback module with pluggable backends.

Provides a small backend-agnostic player (`AudioPlayer`) for playing
audio files through one of a few built-in backends (`sounddevice`,
`ffplay`, `termux-media-player`), or through any custom executable
that accepts a file path as its argument.

Tested on Windows.
"""

from subprocess import run, DEVNULL
from pathlib    import Path
from typing     import Literal
# lazy importing:
# from sounddevice import play, wait
# from soundfile   import read


class AudioPlayer:
    """
    Backend-agnostic audio player.

    Supported backends
    -------------------
    - "sounddevice" (default): plays audio in-process via the
      `sounddevice` + `soundfile` libraries. Cross-platform, no
      external executable required.
    - "ffplay": shells out to the `ffplay` executable (part of FFmpeg).
    - "termux-media-player": shells out to Termux's built-in media
      player command (Android/Termux only).
    - Custom: any other string/Path is treated as the name or path of
      an external executable, invoked as `<backend> <sound_file>`.
    """

    def __init__(
        self,
        backend: str | Literal["ffplay", "termux-media-player", "sounddevice"] | Path = "sounddevice"
    ):
        """
        Parameters
        ----------
        backend : str | Path, default "sounddevice"
            One of the built-in backend names ("sounddevice", "ffplay",
            "termux-media-player"), or a custom executable name/path
            to use as the playback command.

        Raises
        ------
        TypeError
            If `backend` is neither a `str` nor a `Path`.
        """

        backends = ("ffplay", "termux-media-player", "sounddevice")
        if backend in backends:
            self.backend = backend
        elif isinstance(backend, (str, Path)):
            # Anything else (custom executable name/path) is stored as-is;
            # `str()` also normalizes a Path into the matching backend
            # name if it happens to equal one, e.g. Path("ffplay").
            self.backend = str(backend)
        else:
            raise TypeError("backend must be str or Path")
    # ------------------------------------------------ #
    def play(self, sound_file: str | Path = "output.wav") -> None:
        """
        Play `sound_file` using the configured backend.

        Parameters
        ----------
        sound_file : str | Path, default "output.wav"
            Path to the audio file to play.
        """

        sound_file = Path(sound_file)
        # Make sure the parent directory exists before playback is attempted
        # (e.g. when `sound_file` lives in a cache folder that may not have
        # been created yet by the caller).
        sound_file.parent.mkdir(parents=True, exist_ok=True)

        if self.backend == "sounddevice":
            self.__play_sounddevice(sound_file)
        elif self.backend == "termux-media-player":
            self.__play_termux(sound_file)
        elif self.backend == "ffplay":
            self.__play_ffplay(sound_file)
        else:
            self.__play_custom(sound_file)
    # ------------------------------------------------ #
    @staticmethod
    def __play_sounddevice(sound_file: Path) -> None:
        """Play `sound_file` in-process via `sounddevice` + `soundfile`."""
        from sounddevice import play, wait
        from soundfile   import read

        data, samplerate = read(sound_file, dtype="float32")
        play(data, samplerate)
        wait()  # block until playback finishes
    # ------------------------------------------------ #
    @staticmethod
    def __play_ffplay(sound_file: Path) -> None:
        """Play `sound_file` by shelling out to the `ffplay` executable."""

        run(["ffplay","-nodisp","-autoexit","-loglevel","quiet",str(sound_file)],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )
    # ------------------------------------------------ #
    @staticmethod
    def __play_termux(sound_file: Path) -> None:
        """Play `sound_file` via Termux's `termux-media-player` command."""

        run(["termux-media-player","play", str(sound_file)],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )
    # ------------------------------------------------ #
    def __play_custom(self, sound_file: Path) -> None:
        """Play `sound_file` via a custom executable: `<backend> <sound_file>`."""

        run([self.backend, str(sound_file)],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True,
        )
    # ------------------------------------------------ #