#!/bin/bash
set -e

# uv install
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Python 3.10 setup
uv python install 3.10
uv python pin 3.10

# Move to repo
cd /workspace/style-bert-repo

# PyTorch (CUDA 11.8) first
uv pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# Remaining dependencies (exclude torch/torchaudio to avoid overwrite)
uv pip install -r requirements.txt --no-deps torch torchaudio

# ノイズ除去用
uv pip install noisereduce soundfile tqdm

# YouTubeダウンロード用
uv pip install yt-dlp

# Create working directories
mkdir -p /workspace/raw_audio/speaker_name
mkdir -p /workspace/dataset
mkdir -p /workspace/model_assets

echo "Setup complete!"
