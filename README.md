# LoadWhistler

シンプルなデスクトップ音楽プレーヤーです。`lw-files/` フォルダ以下の音楽ファイルをツリー形式で管理し、再生できます。

将来的にLinuxに対応予定ですが、現在Windows向けのみ。

<img width="862" height="520" alt="image" src="https://github.com/user-attachments/assets/815bbf33-8cdb-4c20-8274-4e1e58178166" />


## 動作環境

- Windows 10 以降
- Python 3.10 以降（ソースから実行する場合）

## インストール

### ビルド済みバイナリ（推奨）

[公式サイト](https://abatbeliever.net/software/bin/LoadWhistler) からダウンロードして、任意のフォルダに展開してください。インストールは不要です。

### ソースから実行

Windowsの場合
```bash
scripts/devkit-win.bat
uv run python LoadWhistler.py
```

## 使い方

### 音楽ファイルの配置

`LoadWhistler.exe`（またはスクリプト）と同じ場所に `lw-files/` フォルダを作成し、その中に音楽ファイルを置きます。サブフォルダも利用可能。

```
LoadWhistler.exe
lw-files/
├── アルバム名/
│   ├── track01.mp3
│   └── track02.ogg
└── BGM/
    └── ambient.wav
```

対応フォーマット: **MP3 / OGG / WAV**

### 基本操作

左ペインでグループ（フォルダ）を選択すると、右ペインにファイル一覧が表示されます。ファイルをダブルクリックまたはEnterキーで再生します。

| 操作 | 内容 |
|------|------|
| `Space` | 再生 / 一時停止 |
| `M` | 再生モードの切り替え |

### 再生モード

- **SINGLE/1曲ループ** — 同じ曲をリピート
- **GROUP/順番再生** — グループ内の曲を順番に再生
- **RANDOM/ランダム再生** — グループ内をランダム再生

## 多言語対応

`i18n/` フォルダに言語ファイル (`.ini`) を置くと、ツールバーの言語メニューに追加されます。

## 更新確認

起動時に自動で更新を確認します（オフライン時・無効の場合は無視されます）。

また、About画面からいつでも手動確認や、自動確認の無効化ができます。

## ライセンス

| コンポーネント | ライセンス |
|--------------|-----------|
| Python | PSF License |
| pygame | LGPL v2.1 |
| tkinter / Tcl-Tk | Tcl/Tk License (BSD-like) |
| Noto Sans JP | SIL OFL 1.1 |

## 既知の問題

- Linux環境ではシークバーおよび再生位置の表示が正しく動作しない場合があります。
