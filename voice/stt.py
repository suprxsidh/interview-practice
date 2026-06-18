import numpy as np
import tempfile
import os
from pathlib import Path

_model = None
MODEL_DIR = Path(__file__).parent.parent / "models" / "whisper"


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        _model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8",
            download_root=str(MODEL_DIR),
        )
    return _model


def transcribe(audio_numpy: np.ndarray, sample_rate: int) -> str:
    if audio_numpy is None or len(audio_numpy) == 0:
        return ""

    # Convert to float32 mono [-1, 1]
    if audio_numpy.dtype == np.int16:
        audio = audio_numpy.astype(np.float32) / 32768.0
    elif audio_numpy.dtype == np.int32:
        audio = audio_numpy.astype(np.float32) / 2147483648.0
    else:
        audio = audio_numpy.astype(np.float32)

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    audio = np.clip(audio, -1.0, 1.0)

    import scipy.io.wavfile as wav
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()  # Release Windows file lock before wav.write opens it
    try:
        wav.write(tmp.name, sample_rate, (audio * 32767).astype(np.int16))
        model = _get_model()
        segments, _ = model.transcribe(tmp.name, language="en", beam_size=1)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def is_model_ready() -> bool:
    return MODEL_DIR.exists() and any(MODEL_DIR.iterdir())
