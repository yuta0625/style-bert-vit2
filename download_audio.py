"""
YouTube音声ダウンロードスクリプト
指定したURLの音声をWAV形式でダウンロードする

Usage:
    # 1本ダウンロード
    python download_audio.py --url "https://www.youtube.com/watch?v=XXXXX"

    # プレイリスト丸ごと
    python download_audio.py --url "https://www.youtube.com/playlist?list=XXXXX"

    # スタイル指定 (raw_audio/hiroyuki/calm/ に保存)
    python download_audio.py --url "https://..." --style calm

事前準備:
    pip install yt-dlp
"""

import argparse
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIG: ここを編集する
# =============================================================================

MODEL_NAME = "hiroyuki"

# =============================================================================

# このスクリプトは style-bert-repo/ 内にある
BASE_DIR = Path(__file__).parent.parent  # style-bert-vit2/


def download(url: str, style: str | None) -> None:
    if style:
        output_dir = BASE_DIR / "raw_audio" / MODEL_NAME / style
    else:
        output_dir = BASE_DIR / "raw_audio" / MODEL_NAME

    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(playlist_index)s_%(title)s.%(ext)s")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--output", output_template,
        "--no-playlist",
        url,
    ]

    # プレイリストURLの場合はプレイリスト展開を有効にする
    if "playlist" in url or "list=" in url:
        cmd.remove("--no-playlist")

    print(f"出力先: {output_dir}")
    print(f"URL: {url}\n")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n[ERROR] ダウンロードに失敗しました (code={result.returncode})")
        sys.exit(result.returncode)

    wav_files = list(output_dir.glob("*.wav"))
    print(f"\n完了: {len(wav_files)} ファイルを保存しました → {output_dir}")
    print("次のステップ: python denoise.py --speaker hiroyuki")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="YouTubeのURL (単体 or プレイリスト)")
    parser.add_argument(
        "--style",
        type=str,
        default=None,
        choices=["normal", "angry", "calm"],
        help="保存先のスタイルフォルダ (指定しない場合は hiroyuki/ 直下)",
    )
    args = parser.parse_args()
    download(args.url, args.style)
