from subprocess import run, DEVNULL
from pathlib    import Path
from re         import search
from typing     import Literal
from os         import PathLike


class TTS:
    def __init__(
        self,
        piper_path:  str,
        fa_model:    str | PathLike,
        en_model:    str | PathLike = None,
        sounds_file: str = "sounds",
        systemOS:    str | Literal["Windows", "Linux", "Termux", "Raspberry Pi", "macOS"] = "Windows"
    ):
        self.ROOT     = Path(__file__).resolve().parent.parent
        self.system   = systemOS
        self.Piper    = Path(piper_path)
        self.FA_model = Path(fa_model)
        self.EN_model = Path(en_model) if en_model else None
        self.cache    = Path(sounds_file)
        self.cache.mkdir(exist_ok=True)

    # ------------------------------------------------ #
    @staticmethod
    def detect_language(text: str) -> str:

        if search(r'[\u0600-\u06FF]', text):
            return "fa"
        return "en"
    # ------------------------------------------------ #
    def generate(
        self,
        text: str,
        filename: str = "output.wav"
    ) -> Path:

        lang   = self.detect_language(text)
        model  = self.EN_model if lang == "en" and self.EN_model else self.FA_model
        output = self.cache / filename
        command = (str(self.Piper), "--model", str(model), "--output_file", str(output))

        result = run(
            command,
            input=text,
            text=True,
            capture_output=True,
            encoding="utf-8"
        )

        if result.returncode != 0:
            raise RuntimeError("Piper failed.")

        return output
    # ------------------------------------------------ #
    def speak(self, text: str):

        file = self.generate(text)
        self.play(file)
    # ------------------------------------------------ #
    def play(self, sound_file: str | Path):

        sound_file = str(sound_file)
        if self.system == "Android-Termux":
            command = ["termux-media-player", "play", sound_file]
        else:
            command = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", sound_file]
        run(command, stdout=DEVNULL, stderr=DEVNULL)
    # ------------------------------------------------ #
    def save(self, text: str, filename: str):
        self.generate(text, filename)