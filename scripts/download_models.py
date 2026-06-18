"""Downloads Kokoro ONNX TTS model files to models/kokoro/."""
import urllib.request
import sys
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent / "models" / "kokoro"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "kokoro-v0_19.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx",
    "voices.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin",
}


def download(name, url):
    dest = MODELS_DIR / name
    if dest.exists():
        print(f"  {name} already exists, skipping.")
        return
    print(f"  Downloading {name}...")
    try:
        def progress(count, block_size, total_size):
            pct = count * block_size * 100 // total_size if total_size > 0 else 0
            print(f"\r  {name}: {min(pct, 100)}%", end="", flush=True)
        urllib.request.urlretrieve(url, dest, reporthook=progress)
        print(f"\r  {name}: done           ")
    except Exception as e:
        print(f"\n  ERROR downloading {name}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Downloading Kokoro TTS model files...")
    for name, url in FILES.items():
        download(name, url)
    print("Kokoro models ready.")
