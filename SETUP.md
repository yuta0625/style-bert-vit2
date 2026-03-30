# vast.ai セットアップ手順

## 前提
- vast.ai でインスタンスを借りてSSH接続済みの状態から始める
- 推奨インスタンス: RTX 3090/4090、CUDA 11.8+、Ubuntu 22.04

---

## 1. リポジトリのクローン

```bash
git clone https://github.com/litagin02/Style-Bert-VITS2.git /workspace/style-bert-repo
```

---

## 2. カスタムスクリプトを配置

このディレクトリ (`vast.ai/`) の中身を `style-bert-repo/` にコピーする。

```bash
cp prepare_dataset.py denoise.py download_audio.py /workspace/style-bert-repo/
```

---

## 3. 環境構築

```bash
bash setup.sh
```

以下が自動で実行される:
- uv のインストール
- Python 3.10 のセットアップ
- PyTorch (CUDA 11.8) のインストール
- requirements.txt の依存パッケージのインストール
- ノイズ除去・ダウンロード用パッケージのインストール
- 作業ディレクトリの作成 (`/workspace/raw_audio/`, `/workspace/dataset/`, `/workspace/model_assets/`)

---

## 4. 音声ダウンロード

```bash
cd /workspace/style-bert-repo
source .venv/bin/activate

# 1本ダウンロード
python download_audio.py --url "https://www.youtube.com/watch?v=XXXXX"

# スタイル指定あり
python download_audio.py --url "https://www.youtube.com/watch?v=XXXXX" --style normal

# プレイリスト丸ごと
python download_audio.py --url "https://www.youtube.com/playlist?list=XXXXX"
```

保存先: `/workspace/raw_audio/hiroyuki/{style}/`

---

## 5. ノイズ除去

```bash
# 基本 (strength=1.0)
python denoise.py --speaker hiroyuki

# 声が不自然な場合は強度を下げる
python denoise.py --speaker hiroyuki --strength 0.6
```

出力先: `/workspace/raw_audio/hiroyuki_denoised/`
確認後、問題なければ置き換える:

```bash
rm -rf /workspace/raw_audio/hiroyuki
mv /workspace/raw_audio/hiroyuki_denoised /workspace/raw_audio/hiroyuki
```

---

## 6. データセット作成

`prepare_dataset.py` の CONFIG を編集:

```python
MODEL_NAME     = "hiroyuki"
INITIAL_PROMPT = "そうですね。えーっと、どういうことかというとですね、それは違うと思うんですよ。"
#                ↑ 対象話者の話し方に合った例文に変える
```

実行:

```bash
python prepare_dataset.py
```

内部でこの順に実行される:

| ステップ | 処理内容 |
|---|---|
| Step 1 | 音声を2〜12秒にスライス |
| Step 2 | faster-whisperで文字起こし |
| Step 3 | テキスト前処理 + BERT特徴量生成 |

### 文字起こし結果の確認・修正

Step 2 完了後に `/workspace/dataset/hiroyuki/esd.list` を確認して誤りを修正する。
修正後、Step 3 だけ再実行:

```bash
python prepare_dataset.py --skip_slice --skip_transcribe
```

---

## 7. 学習

```bash
cd /workspace/style-bert-repo
python train_ms_jp_extra.py --config config.yml --model hiroyuki
```

TensorBoard で進捗確認 (ポート6006を開放):

```bash
tensorboard --logdir /workspace/dataset/hiroyuki/models --host 0.0.0.0 --port 6006
```

---

## 8. スタイルベクトル生成

```bash
python default_style.py --model_name hiroyuki
```

---

## 9. モデルをローカルにダウンロード

vast.ai インスタンスからローカルMacへ:

```bash
# ローカルのターミナルで実行
scp -r root@{インスタンスIP}:/workspace/model_assets/hiroyuki ~/style-bert-vit2/model_assets/
```

必要なファイル:
- `config.json`
- `*.safetensors`
- `style_vectors.npy`
