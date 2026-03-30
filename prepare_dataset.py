"""
データセット作成パイプライン
slice.py → transcribe.py → preprocess_all.py を順番に実行する

Usage:
    # vast.ai (GPU) 推奨
    python prepare_dataset.py

    # CPUのみ (ローカルMac等) ※文字起こしが遅い
    python prepare_dataset.py --device cpu

    # スタイル分けなしで1フォルダまとめて処理
    python prepare_dataset.py --no_style

設定は下の CONFIG セクションを編集する。
"""

import argparse
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIG: ここを編集する
# =============================================================================

# 話者名 (英数字推奨)
MODEL_NAME = "hiroyuki"

# 文字起こしのスタイル指示
# 句読点の入れ方・話し方のクセを例文で示す (対象話者の話し方に合わせる)
INITIAL_PROMPT = "そうですね。えーっと、どういうことかというとですね、それは違うと思うんですよ。"

# =============================================================================
# 以下は通常変更不要
# =============================================================================

# このスクリプトは style-bert-repo/ 内にある
REPO_DIR = Path(__file__).parent                    # style-bert-repo/
BASE_DIR = REPO_DIR.parent                          # style-bert-vit2/
INPUT_DIR = BASE_DIR / "raw_audio" / MODEL_NAME     # style-bert-vit2/raw_audio/hiroyuki/
DATASET_ROOT = BASE_DIR / "dataset"                 # style-bert-vit2/dataset/
ASSETS_ROOT = BASE_DIR / "model_assets"             # style-bert-vit2/model_assets/


def run(cmd: list[str], label: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  $ {' '.join(cmd)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=REPO_DIR)
    if result.returncode != 0:
        print(f"\n[ERROR] {label} が失敗しました (code={result.returncode})")
        sys.exit(result.returncode)


def write_paths_yml() -> None:
    """configs/paths.yml を実際のパスで上書きする"""
    paths_yml = REPO_DIR / "configs" / "paths.yml"
    content = (
        f"dataset_root: {DATASET_ROOT.as_posix()}\n"
        f"assets_root: {ASSETS_ROOT.as_posix()}\n"
    )
    paths_yml.write_text(content, encoding="utf-8")
    print(f"[paths.yml] dataset_root={DATASET_ROOT}")
    print(f"[paths.yml] assets_root={ASSETS_ROOT}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["cuda", "cpu"],
        help="文字起こしに使うデバイス (デフォルト: cuda)",
    )
    parser.add_argument(
        "--whisper_model",
        type=str,
        default="large-v3",
        help="faster-whisperのモデルサイズ (デフォルト: large-v3)",
    )
    parser.add_argument(
        "--no_style",
        action="store_true",
        help="サブフォルダなし、スタイル分け不要の場合に指定",
    )
    parser.add_argument(
        "--skip_slice",
        action="store_true",
        help="スライス済みの場合スキップ",
    )
    parser.add_argument(
        "--skip_transcribe",
        action="store_true",
        help="文字起こし済みの場合スキップ",
    )
    args = parser.parse_args()

    if not INPUT_DIR.exists():
        print(f"[ERROR] 音声フォルダが見つかりません: {INPUT_DIR}")
        sys.exit(1)

    # configs/paths.yml を実際のパスで上書き
    write_paths_yml()

    # ------------------------------------------------------------------
    # Step 1: スライス
    # ------------------------------------------------------------------
    if not args.skip_slice:
        run(
            [
                sys.executable, "slice.py",
                "--input_dir", str(INPUT_DIR),
                "--model_name", MODEL_NAME,
                "--min_sec", "2",
                "--max_sec", "12",
            ],
            "Step 1: 音声スライス",
        )
    else:
        print("\n[SKIP] Step 1: スライス")

    # ------------------------------------------------------------------
    # Step 2: 文字起こし
    # ------------------------------------------------------------------
    if not args.skip_transcribe:
        transcribe_cmd = [
            sys.executable, "transcribe.py",
            "--model_name", MODEL_NAME,
            "--initial_prompt", INITIAL_PROMPT,
            "--language", "ja",
            "--model", args.whisper_model,
            "--device", args.device,
        ]
        if args.device == "cpu":
            transcribe_cmd += ["--compute_type", "int8"]
        run(transcribe_cmd, "Step 2: 文字起こし (faster-whisper)")
    else:
        print("\n[SKIP] Step 2: 文字起こし")

    # ------------------------------------------------------------------
    # Step 3: テキスト前処理 + BERT特徴量生成
    # ------------------------------------------------------------------
    run(
        [
            sys.executable, "preprocess_all.py",
            "--model_name", MODEL_NAME,
            "--use_jp_extra",
            "--normalize",
            "--trim",
        ],
        "Step 3: テキスト前処理 + BERT特徴量生成",
    )

    print("\n" + "="*60)
    print("  データセット作成完了!")
    print(f"  出力先: {DATASET_ROOT / MODEL_NAME}")
    print("  次のステップ: python train_ms_jp_extra.py --config config.yml")
    print("="*60)


if __name__ == "__main__":
    main()
