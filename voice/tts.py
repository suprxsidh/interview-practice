import numpy as np
from pathlib import Path

_pipeline = None
MODEL_DIR = Path(__file__).parent.parent / "models" / "kokoro"
VOICE = "af_sarah"


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kokoro_onnx import Kokoro
        model_file = MODEL_DIR / "kokoro-v0_19.onnx"
        voices_file = MODEL_DIR / "voices.bin"
        if not model_file.exists() or not voices_file.exists():
            raise FileNotFoundError(
                "Kokoro model files not found. Please run Install.bat to download them."
            )
        _pipeline = Kokoro(str(model_file), str(voices_file))
    return _pipeline


def synthesize(text: str) -> tuple[int, np.ndarray]:
    pipeline = _get_pipeline()
    samples, sample_rate = pipeline.create(text, voice=VOICE, speed=1.0, lang="en-us")
    audio = np.array(samples, dtype=np.float32)
    return sample_rate, audio


def is_model_ready() -> bool:
    return (
        (MODEL_DIR / "kokoro-v0_19.onnx").exists()
        and (MODEL_DIR / "voices.bin").exists()
    )
