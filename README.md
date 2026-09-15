# 浜田 将彰の職務経歴書

公開用の職務経歴書。Web版とA4のPDF版を、同じ `content.json` から生成します。

## 更新方法

1. `content.json` の本文・日付・経験年数を編集する。
2. Python環境に `pip install -r requirements.txt` で依存を入れる。
3. `python build.py` でWeb版とPDF版を生成する。
4. PDFの改ページ・表示を確認して、原稿と `docs/` を一緒にコミット・pushする。

日本語TrueTypeフォントが必要です。macOSのArial Unicodeを自動検出します。他の環境では `python build.py --font /path/to/japanese-font.ttf` を使ってください。フォントの埋め込み条件は利用するフォントのライセンスに従ってください。フォントファイル自体はこのリポジトリに含めません。

`docs/index.html` がWeb版、`docs/resume.pdf` が提出用PDFです。Web版はモバイル表示と印刷にも対応しています。

## 公開設定

GitHub Pagesの公開元は `main` ブランチの `/docs`。生成済みファイルを配信するため、独自のActionsワークフローは不要です。

設定方法：[GitHub Pages公式ドキュメント](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

## 原稿の扱い

このリポジトリには公開向けに整理した情報だけを収録しています。会社・顧客名や未公開の事業数値、連絡先は含めていません。経験年数は原稿内に示した基準日時点の概算です。
