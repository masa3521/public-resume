# 浜田 将彰の職務経歴書

`content.json` を共通原稿として、元の表形式のExcel、A4の職務経歴PDF、Markdown、Webを生成します。

- 公開サイト：<https://masa3521.github.io/public-resume/>
- 原稿：[`content.json`](content.json)
- 文言確認：[`docs/resume.md`](docs/resume.md)
- Claude Codeへの引継ぎ：[`CLAUDE.md`](CLAUDE.md)

## 生成コマンド

リポジトリのルートで実行します。CodexとClaude Codeで同じコマンドです。

```sh
./build.sh
```

| 出力 | 用途 |
| --- | --- |
| `docs/skillsheet.xlsx` | 元の17列の案件表＋5列の技術一覧。罫線・配色・列幅を継承 |
| `docs/resume.pdf` | 読み物として組版するA4縦の職務経歴書 |
| `docs/resume.md` | 文言確認用Markdown |
| `docs/index.html`、`docs/designs/` | Web版とA〜Dのデザイン比較 |
| `docs/skillsheet.layout.json` | Excelの案件・技術分類の行範囲と印刷用レイアウト |
| `docs/manifest.json` | 原稿・テンプレート・成果物のハッシュと件数 |

通常の生成はMicrosoft Excelを起動しません。Excel・A4 PDF・Markdown・Webは同じJSONから生成し、変換を重ねて本文が失われることを避けています。全形式の生成成功後に出力ディレクトリを置き換えます。

### Excelと同じ表形式のPDF（試験実装）

Microsoft Excel for Macを使ってA3横の `docs/skillsheet.pdf` を生成する処理もあります。ただし、2026年9月16日のExcel 16.112.4では保存APIのエラー・タイムアウトが発生し、**自動出力の最終確認は未完了です**。現時点の公開更新には通常の `./build.sh` を使用してください。公開中のPDFは動作確認済みのA4版です。

Excel連携を再検証する場合に限り、公開用 `docs/` と別の出力先で実行します。

```sh
./build.sh --excel-pdf --output-dir /tmp/resume-excel-pdf-preview
```

こちらはExcelの印刷機能を使います。macOSが求める場合はExcelへのAutomation操作を許可してください。一時コピーだけの印刷設定・余白を調整し、入力Excelや利用中のブックは変更しません。案件・技術分類の境界で改ページし、ページに収まらない大きな案件はエラーで停止します。文字を小さくして無理に詰め込む処理はしません。書き出しに失敗した場合も、既存の出力は保持します。

`resume.pdf` はA4縦、`skillsheet.pdf` はExcel書式のA3横です。通常の `./build.sh` では任意のA3 PDFを生成しないため、公開後もA3版を維持するときは毎回 `--excel-pdf` を付けてください。

印刷計画だけを確認する場合：

```sh
python3 tools/export_excel_pdf.py docs/skillsheet.xlsx /tmp/skillsheet-preview.pdf --dry-run
```

## 元のExcel書式を保つ仕組み

1. `templates/skillsheet.xlsx` の空テンプレートを読み込みます。
2. `content.json` の案件を4行ずつのブロックに配置します。案件や技術行の追加・並べ替えに追従します。
3. 文章量に応じて行高を調整し、期間はExcel日付と `DATEDIF` 数式で保持します。
4. 印刷範囲・反復見出し・担当工程の縦書き・追加行の書式を保存します。
5. 保存済みExcelを再読込し、書き込んだ値と期間計算を照合します。

テンプレートは原本の書式と固定見出しだけです。原本の職歴、所属会社、年齢、性別、最寄駅、稼働開始日、未使用の共有文字列、ローカルパスは含めていません。公開用のプロフィール欄は職種・更新日などに置き換えています。個人提出用の元Excelをこの公開リポジトリへ追加しないでください。

元のDownloadsファイルや、作業時の一時スクリプトは実行時に必要ありません。テンプレートと生成処理はすべてこのリポジトリ内にあります。

## 文言・案件の更新

変更は `content.json` に反映してから生成してください。生成済みのExcel・PDF・HTMLを直接編集しても、次回生成時に上書きされます。

Markdownへの指摘を先に書く場合は、指摘を元データに反映してから再生成します。`resume.md` に行頭の `→` がある場合や、生成中に原稿・Markdownが変更された場合は停止し、編集中の内容を守ります。

主な項目：

| 項目 | 内容 |
| --- | --- |
| `title`、`summary`、`strengths` | 肩書き、職務概要、自己PR |
| `excel_profile` | 公開Excelの短いプロフィール欄 |
| `updated` | 更新日。更新時に当日の日付へ変更 |
| `as_of_month` | `YYYY-MM`。継続案件の期間計算基準月 |
| `projects` | 案件の本文、体制、工程、技術、公開資料 |
| `projects[].workbook` | Excelの期間・工程欄の構造化情報 |
| `skill_groups` | 技術分類、技術名、経験年数、利用状況、使用場面 |
| `experience_as_of` | 技術一覧の注釈。現在は本人の希望で空文字 |
| `history`、`history_note` | 職歴一覧と並行担当等の補足 |

案件の期間・工程：

```json
"workbook": {
  "start": "2022-03",
  "end": null,
  "phase_flags": [true, true, true, true, true, true, true]
}
```

- `end: null` は継続中です。Excelには「現在」と表示し、`as_of_month` までの月数を計算します。
- フラグ順は **要件定義／基本設計／詳細設計／構築・設定／運用設計／保守・運用／障害対応** です。
- `period` はWeb・Markdown等の読みやすい表示用です。`workbook.start/end` と一致しない場合はビルドを止めます。
- 会員マイページのような開発・保守の内訳は `period` に保持します。期間を変更するときは構造化情報・職歴一覧も確認してください。
- 案件の追加は `projects` に追加します。コードに案件件数や日付を追記する必要はありません。
- 長文がExcelの行高上限を超える場合は、内容を削るのではなく、原稿で案件を適切に分けてください。

## 実行環境

- Python 3.10以上、`requirements.txt` のReportLab
- Node.js（このMacではCodex同梱のNode 24で検証）
- `@oai/artifact-tool` を含むCodexランタイム
- 日本語TrueTypeフォント（このMacではArial Unicode）
- A3表形式PDFを作る場合のみ、Microsoft Excel for Mac

このMacでは `./build.sh` がPython・Node・artifact-tool・フォントを自動検出します。Claude Codeも同じインストール済みランタイムを利用でき、Codexを操作する必要はありません。

**別のPCでは依存環境の用意が必要です。** Git cloneだけではartifact-toolや日本語フォントはインストールされません。artifact-toolがない場合は明確なエラーで停止します。一般のnpm公開パッケージとしてのインストールは前提にしていません。

別のPython環境を使う場合：

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
RESUME_PYTHON="$PWD/.venv/bin/python3" ./build.sh
```

自動検出できない環境では、実在するパスを指定します。

```sh
CODEX_ARTIFACT_NODE_MODULES=/path/to/runtime/node_modules \
RESUME_PYTHON=/path/to/python3 \
./build.sh --node /path/to/node --font /path/to/japanese.ttf
```

フォント・ランタイム・認証情報はリポジトリに含めません。

## 確認・テスト

公開用 `docs/` を変更せずに試す場合：

```sh
./build.sh --output-dir /tmp/resume-preview --xlsx-qa-dir /tmp/resume-qa
python3 -m unittest discover -s tests -v
```

QA画像は公開出力の外へ保存してください。Excelの値・期間計算は通常ビルドでも検証されます。テストは案件追加・並べ替え、継続中の日付表示、技術分類の増減、期間の不一致、空テンプレートの内容を確認します。本文やテンプレートを変えたときは、QA画像と実PDFも目視確認してください。

主な実装：

- `build.py`：全形式生成・失敗時の出力保護・manifest
- `tools/export_resume_xlsx.mjs`：artifact-toolで元書式Excelを生成
- `tools/workbook_native.py`：artifact-toolが保存しない印刷情報・縦書き・追加行書式を補完
- `tools/export_excel_pdf.py`、`.applescript`：任意のExcel実印刷PDF
- `build_designs.py`、`designs/`：Webデザイン比較

## 公開

公開元は `masa3521/public-resume` の `main` ブランチ、`/docs` です。原稿・テンプレート・生成コード・生成物を一緒にコミットしてpushします。ダウンロードURLの版番号には原稿だけでなくテンプレート・生成コードの変更も反映します。

```sh
./build.sh
git diff --check
git status --short
# 内容と出力を確認してから、対象ファイルを指定してcommit/push
```
