"""
ノイズ除去スクリプト
raw_audio/{speaker_name}/ 以下の全WAVファイルを一括処理する

Usage:
    python denoise.py --speaker hiroyuki
    python denoise.py --speaker hiroyuki --strength 0.8
"""

import argparse
from pathlib import Path

import noisereduce as nr
import soundfile as sf
from tqdm import tqdm

# このスクリプトは style-bert-repo/ 内にある
BASE_DIR = Path(__file__).parent.parent  # style-bert-vit2/


def denoise(speaker: str, strength: float = 1.0) -> None:
    input_dir = BASE_DIR / "raw_audio" / speaker
    output_dir = BASE_DIR / "raw_audio" / f"{speaker}_denoised"
    output_dir.mkdir(parents=True, exist_ok=True)

    wav_files = list(input_dir.rglob("*.wav"))
    if not wav_files:
        print(f"WAVファイルが見つかりません: {input_dir}")
        return

    print(f"{len(wav_files)}ファイルを処理します (strength={strength})")

    for wav_path in tqdm(wav_files):
        data, rate = sf.read(wav_path)

        # ステレオの場合モノラルに変換
        if data.ndim == 2:
            data = data.mean(axis=1)

        reduced = nr.reduce_noise(y=data, sr=rate, prop_decrease=strength)

        # サブフォルダ構造を維持して出力
        rel_path = wav_path.relative_to(input_dir)
        out_path = output_dir / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out_path), reduced, rate)

    print(f"\n完了: {output_dir} に保存しました")
    print("確認後、問題なければ以下のコマンドで置き換えてください:")
    print(f"  rm -rf {input_dir} && mv {output_dir} {input_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--speaker", required=True, help="話者名 (raw_audio/以下のフォルダ名)")
    parser.add_argument(
        "--strength",
        type=float,
        default=1.0,
        help="ノイズ除去強度 0.0〜1.0 (デフォルト: 1.0, 強すぎる場合は0.5〜0.8を試す)",
    )
    args = parser.parse_args()
    denoise(args.speaker, args.strength)
