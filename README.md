# 浜田 将彰の職務経歴書

`content.json` を共通の元データとして、Excel・PDF・Markdown・Webを一括生成します。案件の担当内容・体制・工程・環境と、技術スキルの経験年数・利用状況・使用場面を各形式に収録します。

## 文言の確認と修正

- **編集する原稿：** [`content.json`](content.json)
- **読み通して確認する原稿：** [`docs/resume.md`](docs/resume.md)
- **Web：** <https://masa3521.github.io/public-resume/>

Markdownに付けた修正指示を元データへ反映してから再生成します。生成済みのExcel・PDF・Markdown・HTMLを直接編集すると次回の生成で上書きされるため、確定した修正は `content.json` に入れます。

## 一括生成

このMacでは、次の1コマンドで全形式を更新できます。

```sh
./build.sh
```

処理の流れは次のとおりです。

```text
content.json（共通原稿）
    ├── docs/skillsheet.xlsx  Excel：スキルシート・技術スキル一覧
    ├── docs/resume.pdf       A4の提出用PDF
    ├── docs/resume.md        文言確認・共有用Markdown
    ├── docs/index.html      GitHub PagesのWeb版
    └── docs/designs/         同じ本文を使ったA〜Dの比較用Web版
```

Excel→PDF→Markdownと抽出・再変換する方式ではなく、すべて同じ元データから生成します。ExcelとPDFはそれぞれ読みやすいレイアウトにし、原稿の詳細が変換途中で消えない構成です。すべての生成が成功してから `docs/` に出力します。

### 実行環境

- Python 3と `requirements.txt` のReportLab
- Node.jsとCodexランタイムの `@oai/artifact-tool`（Excel生成・保存後の値照合に使用）
- PDFに埋め込む日本語TrueTypeフォント

`build.sh` はCodexの同梱Python、リポジトリの `.venv`、システムPythonの順に探します。`RESUME_PYTHON` で指定もできます。Nodeとartifact-toolはCodexランタイムの既定配置を検出し、プロジェクトに依存ファイルをコピーしません。他の配置を使う場合は `--node` と `CODEX_ARTIFACT_NODE_MODULES` で指定してください。一般のPython環境では先に `pip install -r requirements.txt` を実行します。

macOSのArial Unicodeを自動検出します。他のフォントを使う場合：

```sh
./build.sh --font /path/to/japanese-font.ttf
```

フォントファイル自体はリポジトリに含めません。埋め込み条件は使用するフォントのライセンスに従ってください。

### 出力確認

```sh
./build.sh --xlsx-qa-dir /tmp/resume-xlsx-qa
```

Excelの全範囲のプレビューと値照合結果を保存します。Excelは通常の生成でも、保存後に再読み込みして全セルの文字列と位置を照合します。PDFは改ページと表示を確認してください。`docs/manifest.json` に元データと成果物のハッシュ、案件・スキル件数を記録します。

別の原稿・保存先で確認する場合：

```sh
./build.sh --source /path/to/draft.json --output-dir /tmp/resume-draft
```

## 元データの項目

- `summary`・`strengths`：職務概要と強み
- `history`：職歴一覧。並行担当・空白期間の補足は `history_note`
- `projects`：案件ごとの期間・役割・工程・体制・概要・業務詳細・環境・技術・公開資料
- `skill_groups`：分類ごとの技術・経験年数・利用状況・使用場面
- `experience_as_of`：経験年数・利用状況の基準日と読み方
- `qualifications`・`approach`：資格と仕事の進め方

## デザインと公開

A：端正なドキュメント、B：余白のあるプロフィール、C：エンジニアノート、D：キャリアタイムライン。全案の本文とダウンロードファイルは共通です。デザインの原本は `designs/`。形式間の更新漏れを防ぐため、デザイン変更時も `./build.sh` で一括生成します。

GitHub Pagesの公開元は `main` ブランチの `/docs`。原稿・生成スクリプト・`docs/` をまとめてコミットしてpushします。

## 原稿の範囲

公開向けに整理した職務情報を収録します。2026年9月16日時点で、原資料にあるチーム人数・設備規模・改善率も本人確認のうえ反映しています。勤務先・顧客名、連絡先、最寄り駅などは含めません。全体の設備規模と本人の担当範囲を区別し、並行期間は単純合算しません。

元の提出用Excelは別に保管し、読み取り元として保持しています。このリポジトリが生成するExcelは詳細を引き継いだ新しい共通原稿版で、元Excelの個人情報欄や既存様式を複製するものではありません。
