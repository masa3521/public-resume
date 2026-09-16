# Claude Codeへの引継ぎ

このリポジトリは浜田将彰の公開職務経歴書です。実行手順・環境要件はREADME.mdを参照してください。

## 最初に確認すること

1. `git status --short` とブランチを確認し、ユーザーの編集中ファイルを把握する。
2. `content.json` と `docs/resume.md` の差分を確認する。Markdownに指摘がある場合は、元データへ反映してから再生成する。
3. `./build.sh --help` で利用する出力を確認する。

## 更新方法

- 本文・日付・工程・技術の正本は `content.json`。
- まず `./build.sh --output-dir /tmp/resume-preview --xlsx-qa-dir /tmp/resume-qa` で確認する。
- 通常ビルドは `./build.sh`。元書式ExcelとA4 PDF・Markdown・Webを生成する。
- Excelと同じ表のA3横PDFは `--excel-pdf` の試験実装。Excel 16.112.4で保存APIのエラー・タイムアウトが出ており、最終確認未完了。公開更新には通常ビルドを使い、再検証は別の `--output-dir` で行う。
- `python3 -m unittest discover -s tests -v` で案件追加等の回帰を確認する。
- 原稿と必要な生成物を一緒にcommitする。pushの実行はユーザーの指示範囲に従う。

## 維持する仕様

- Excelは `templates/skillsheet.xlsx` の元書式を使用。17列の案件表、5列の技術一覧、罫線・配色・列幅・工程縦書きを保つ。
- 案件期間・担当工程は `projects[].workbook`。日付の配列や案件数を生成コードに固定しない。
- `end: null` の期間計算は `as_of_month` まで。更新時は `updated` と基準月、表示用 `period`・職歴一覧の整合性を確認する。
- 全文を収録する。収めるために勝手に要約・削除したり、文字サイズを下げたりしない。
- 「録画保管のライフサイクル・約7割削減」の実績説明と、技術一覧の経験年数注釈は本人の指示で削除済み。復活させない。
- 動画マイページの受託期間は2022年7月〜2023年7月。開発は2022年7〜9月、以後は修正・運用・保守。

## 公開ファイルとテンプレート

- このリポジトリ自体が公開される。元の私用Excel、個人情報、認証情報、私用案件リポジトリ、一時診断ファイルを追加しない。
- テンプレートは固定見出しと書式だけ。会社名・最寄駅・年齢・性別・稼働開始日などの私用欄を原本から復元しない。
- `docs/` は生成専用。手書きの引継ぎ資料やテスト出力を置かない。
- `tools/workbook_native.py` は、実際に確認されたartifact-toolの印刷設定・縦書き・追加行書式の保存制限を補うもの。ここで本文を書き換えない。
- `skillsheet.layout.json` は生成器と印刷処理の契約。案件・技術分類を途中で切らないための行範囲とPDF用余白を記録する。
- A3印刷は余白の推定を含む。本文を変えたときはPDF全体を確認し、途中分割や文字切れがあれば出力をそのまま採用しない。

## 依存関係

同じMacではCodex同梱のNode/Python/artifact-toolを自動検出するため、Claude Codeからそのまま実行できる。別環境ではREADMEの明示パス指定が必要。原本のDownloadsファイルや過去の `/private/tmp` スクリプトには依存しない。

公開先：`https://github.com/masa3521/public-resume`、Pages：`https://masa3521.github.io/public-resume/`。
