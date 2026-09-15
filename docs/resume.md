# 浜田 将彰 — 職務経歴書

Masaaki Hamada

クラウド・IaC エンジニア / CTO

更新：2026年9月16日

## 概要

物理サーバ・ネットワークからクラウド基盤まで、15年以上にわたり設計・構築・運用を経験。AWSを約10年、Azure・Terraformを約3.5年扱い、クラウド移行、IaC、CI/CD、監視設計に取り組んできました。2022年からは自社サービスの取締役・CTOとして、企画から開発・インフラ・運用までを担当しています。

### クラウド基盤を設計し、コードで再現する

AWS約10年、Azure・Terraform約3.5年。決済基盤では開発・検証・本番のほぼ全環境をIaC化し、数時間で再構築できる状態に整備。少人数の基盤立ち上げでは、設計から構築・運用設計まで一貫して担当します。

### 規模と役割に応じて、運用・コストを改善する

約10台のAWSサーバを対象に、時間帯別のAuto ScalingやSpot・RIの活用でコストを3〜4割削減。20名規模のチームでの専門担当、約10名の構築チームでのPM兼任、担当領域の単独遂行を経験しています。

### 事業運営と開発をつなぎ、小規模サービスを育てる

自社サービスでは技術担当1名で企画・要件定義から実装・運用まで対応。Web・SaaS連携・クラウド基盤を横断して開発し、当初3名で担当していた運用をAI活用により1名で回せる形に改善しました。

## 技術スキル

経験年数と利用状況は2026年8月時点の実務経験の概算です。同じ行に複数の技術がある場合、すべてを記載年数使ったという意味ではありません。並行して担当した期間は単純合算していません。Next.js・Vercel・Supabaseは2026年から使用しています。 複数技術をまとめた行の利用状況は、技術群単位の表示です。

### クラウド(AWS)

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| コンピュート(EC2/ECS/Fargate/Lambda) | 約10年 | 使用中 | 決済基盤で併用、自社サービスの予約API・Zoom自動割当・AIレポートを Lambda(コンテナイメージ)で実装 |
| ストレージ・DB(S3/RDS/DynamoDB/ElastiCache) | 約7年 | 使用中 | Wi-Fi 基盤・決済基盤のデータストア、録画アーカイブ約1.75TiBのライフサイクル設計(Glacier Instant Retrieval) |
| ネットワーク・配信(VPC/ELB/CloudFront/Route 53/API Gateway) | 約10年 | 使用中 | 決済基盤・自社サービスのAPI/配信/DNS、ゾーン移管・SPF/DKIM/DMARC |
| 運用・コスト(CloudWatch/IAM/Auto Scaling/Spot・RI) | 約10年 | 使用中 | アラーム→Slack の監視設計、時間帯別の Auto Scaling とスポット/リザーブド化でコスト3〜4割削減 |
| データ処理(EMR/PySpark) | 1年未満 | 過去に使用 | ログ調査基盤(数日→数時間程度に短縮) |

### クラウド(Azure)

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| コンピュート(Virtual Machine Scale Sets/App Service) | 約3.5年 | 過去に使用 | 決済プラットフォームの自動スケール構成を設計・構築 |
| ストレージ・DB(Storage/SQL Database) | 約3.5年 | 過去に使用 | 決済プラットフォームのデータストア |
| ID・ネットワーク(Azure AD(現 Microsoft Entra ID)/DNS) | 約3.5年 | 過去に使用 | 認証基盤・名前解決 |
| 運用(Monitor/Log Analytics/Automation) | 約3.5年 | 過去に使用 | 監視設計・Slack/メール通知、稼働率目標(SLA/SLO)の設定 |

### IaC・CI/CD・コンテナ

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Terraform | 約3.5年 | 過去に使用 | 開発・検証・本番のほぼ全環境を IaC 化(環境構築を数時間で) |
| AWS CloudFormation | 1年未満 | 過去に使用 | CMS基盤の再構築をコード化 |
| Ansible | 約6年 | 過去に使用 | Wi-Fi 基盤の自動構築、決済基盤の構成管理 |
| GitHub Actions | 約6年 | 使用中 | CI/CD、E2E連動デプロイ |
| Jenkins | 約2年 | 過去に使用 | Wi-Fi 基盤の自動化 |
| Docker | 約7年 | 使用中 | コンテナ化・イメージビルド |

### OS・仮想化

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Linux(RHEL/Amazon Linux/Ubuntu) | 15年以上 | 使用中 | 全所属で継続。物理サーバ約100台〜現在のEC2/コンテナまで |
| Windows Server(2000 Server/2003/2008)/Active Directory | 約10年 | 過去に使用 | 社内AD・ファイルサーバの設計・構築・運用 |

### ネットワーク・物理基盤

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| ネットワーク設計・構築(Cisco/L2・L3スイッチ/VLAN/QoS) | 約4.5年 | 過去に使用 | 基幹NWリプレイス(L3SW 4台/L2SW 20台/Client 約1,500台)、認証DBシステムのNW構築 |
| 物理サーバ構築・運用 | 約6年 | 過去に使用 | Server 約100台の社内インフラ、約30台の認証DBシステム |
| F5 BIG-IP/FreeRADIUS | 約1.5年 | 過去に使用 | 公衆無線 Wi-Fi・ローミング認証基盤 |

### ミドルウェア

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Apache HTTP Server/Nginx/Apache Tomcat | 約7年 | 過去に使用 | Webサーバ・リバースプロキシ |
| DNS(BIND/Route 53/SPF・DKIM・DMARC) | 約5年 | 使用中 | 社内DNS運用、ゾーン移管・メール認証設定 |
| Zabbix | 約1.5年 | 過去に使用 | 公衆無線 Wi-Fi 基盤の監視 |

### DB

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Oracle Database | 約6年 | 過去に使用 | 社内システム・認証DB |
| MySQL | 約5年 | 過去に使用 | 社内システム |
| PostgreSQL(Supabase 含む) | 約2年 | 使用中 | Wi-Fi 基盤の Web システム(2018〜19)、法人向けポータル(Supabase/RLS) |

### 言語・フレームワーク

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Python | 約3.5年 | 使用中 | ログ分析(PySpark)、予約システム、AIレポート |
| JavaScript/Node.js/TypeScript | 約4.5年 | 使用中 | Lambda、Shopifyアプリ、Next.js |
| PowerShell | 約3.5年 | 過去に使用 | Azure 環境の運用・自動化スクリプト(2020〜23) |
| React/Next.js | 約1.5年 | 使用中 | React: 会員向けマイページ(2022〜23)、Next.js: 法人向けポータル(2026年〜) |

### SaaS・外部API

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Shopify(Liquid/Admin API/App Proxy) | 約4.5年 | 使用中 | EC+予約+会員基盤の構築・運用 |
| Vercel/Supabase | 1年未満 | 使用中 | 法人向けポータルの新規立ち上げ(2026年〜) |
| Sesami/Zoom/Recharge/Klaviyo/Google Workspace の各API | 約3年 | 使用中 | 予約・配信・課金・メールの統合 |
| Playwright | 1年未満 | 使用中 | E2E・管理画面の自動操作 |

### AI活用

| 技術 | 経験の目安 | 利用状況 | 経験した内容・使用場面 |
| --- | --- | --- | --- |
| Claude Code/MCP(Model Context Protocol) | 約1年 | 使用中 | 開発・運用の主軸。定型オペレーションを再利用可能な手順(スキル)として自動化し1名運用 |
| OpenAI API | 約3年 | 使用中 | AIレポート生成基盤 |

## 職歴一覧

| 期間 | 事業・領域 | 役割 |
| --- | --- | --- |
| 2022/03 - 現在 | 自社サービス | 取締役 / CTO |
| 2026/03 - 2026/07 | Webサービスのクラウド移行 | ITコンサルタント / 事業側・ベンダー間の調整 |
| 2022/07 - 2023/07 | 会員向け動画サービス | 開発全般・運用・保守 / 受託 |
| 2020/01 - 2023/06 | 決済プラットフォーム | クラウドエンジニア / 業務委託 |
| 2018/01 - 2019/12 | 通信サービス基盤 | クラウドエンジニア / 業務委託 |
| 2014/12 - 2016/07 | 通信サービス基盤 | クラウドエンジニア / 派遣 |
| 2013/09 - 2014/11 | 通信キャリア向けシステム | カスタマーエンジニア / 派遣 |
| 2008/04 - 2013/01 | 事業会社の社内インフラ | 社内SE |

動画サービスの受託案件は2022/07 - 09に開発、2022/10 - 2023/07は修正・運用・保守を担当。自社サービス・業務委託と並行。2013/02 - 08は資格取得期間、2016/12 - 2017/12はカナダへ語学留学。 社内ネットワークのリプレイス（2010/01 - 2013/01）は、社内インフラ業務と並行して担当しました。

## 案件経験

### 自社サービスの開発・運用

- 期間：2022/03 - 現在
- 役割：取締役 / CTO
- 担当工程：企画・要件定義・技術選定・基本設計・詳細設計・構築・実装・運用設計・保守・運用・障害対応
- 体制・規模：事業全体：本人を含む3名＋講師約20名。技術担当：本人1名。定型運用はAI活用により3名から1名へ。

グローバル向けのオンライン1on1ヨガ・サブスクリプションサービス（BtoC/BtoB）で技術全般を担当。EC・予約・配信基盤と、予約連携・AIレポート・会議アカウント管理を要件定義から設計・開発、運用・保守まで担っています。採用・予算・技術選定などの意思決定にも携わっています。

#### EC・予約・契約情報の統合

Shopify・Sesami・Zoom・Recharge・Klaviyoを組み合わせ、EC・予約・配信基盤を設計・構築・運用。生徒・講師の現地時刻とJST・PT・UTCが関わる予約情報の整合性を考慮して連携しました。

#### 予約・受講履歴のAPI連携

Node.js・ExpressでShopifyと予約・契約情報を連携。講師情報を含む予約データ・受講URL・タイムゾーンをShopify Metaobjectに保存し、顧客と紐付けました。予約変更・キャンセルに合わせた会議情報の更新、顧客別の受講履歴・注文履歴・契約情報の取得、レッスン単位のコメント管理を実装しました。

#### AIレッスンレポートの生成・配信

Python・AWS Lambdaでレッスン字幕を取得し、OpenAI APIによるレポート生成、Gmailでのメール配信、Shopifyへの保存、Google Docsへの履歴蓄積を自動化。字幕生成の遅延に対応する再試行と、DynamoDBを使って重複処理を抑える実行ロックを実装しました。2025年3月18日に正式リリース。

#### 会議アカウントの自動割り当て

Python・AWS Lambdaで複数のZoomアカウントの会議予定を調べ、開始・終了時刻の重複判定で空きアカウントを選定。会議の作成・削除とGoogle Calendar・スプレッドシートへの記録を連携しました。

#### 運用と保管コストの改善

録画アーカイブ約1.75TiBを、保管から90日でS3 Glacier Instant Retrievalへ移すライフサイクルを設計。月額の実測で保管コストを約7割削減しました。CloudWatch・SNSからSlackへのアラーム通知も整備しました。

#### 法人向けポータルの立ち上げ

2026/07からNext.js・Vercel・Supabaseで法人向け予約ポータルを新規開発。検証・本番の環境分離、PostgreSQL RLSによる認可設計、PlaywrightによるE2Eテストを整備しました。E2Eテストは本番データから隔離する構成を設計しています。

#### AIを活用した事業運用の改善

2025年からClaude Codeを主軸に開発・運用を進め、定型オペレーションを再利用可能な手順として自動化。採用・予算・技術選定を含む事業運営と並行し、当初3名で回していた運用をAI活用により1名で対応できる形に改善しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Amazon Linux / (EC2) |
| データベース | Supabase / (PostgreSQL) |
| ミドルウェア | Supabase Auth |
| クラウド・ツール | AWS (EC2 / Lambda / S3 / ECS / ECR / CloudWatch) / Vercel / Next.js / TypeScript / Shopify / Sesami / Zoom / Recharge / Klaviyo の各API / Playwright / GitHub Actions / Docker / Node.js / Python / OpenAI API / Claude Code |

使用技術：AWS Lambda / API Gateway / DynamoDB / S3 / Docker / Shopify Admin GraphQL API・App Proxy / Liquid / Node.js / Express / Python / OpenAI API / Zoom API / Gmail API / Google Docs API / Google Calendar API / Google Sheets API / Next.js / TypeScript / Vercel / Supabase / Playwright / Claude Code / MCP / GitHub Actions / CloudWatch / SNS / Sesami API / Recharge API / Klaviyo API / Serverless Framework

公開資料：[AIレッスンレポートの正式リリース（PR TIMES・2025/03/23）](https://prtimes.jp/main/html/rd/p/000000002.000119830.html)

### Webサービスのクラウド移行に伴うITコンサルティング

- 期間：2026/03 - 2026/07
- 役割：ITコンサルタント / 事業側・ベンダー間の調整
- 担当工程：要件定義・基本設計
- 体制・規模：全体約20名（事業側・ベンダー・本人）。

BtoC Webサービスの既存ホスティング環境から、AWSのMSPフルマネージド環境への移行を支援。事業側とベンダー側のインフラ部分の調整、構成・手順のチェックを担当しました。

#### 構成レビューと技術判断

移行構成をレビューし、技術判断に必要な情報を整理。移行後の構成を棚卸しし、構成図にまとめました。

#### セッション障害への対応案の比較

負荷分散時に発生するセッション障害について複数の対策案を比較検討。ベンダーに見積もりと実現可能性の確認を依頼し、事業側の判断を支援しました。

#### DNS移管と切り替えの確認

DNS移管の事前検証と切り替え後の確認を担当しました。移行の実作業はベンダー・事業側が実施し、当方は両者間の調整と構成・手順の確認を担いました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Amazon Linux / (EC2) |
| ミドルウェア | Apache HTTP Server / PHP |
| クラウド・ツール | AWS (ALB / Route 53 / S3) |

使用技術：Amazon Linux / (EC2) / Apache HTTP Server / PHP / AWS (ALB / Route 53 / S3)

### 動画配信サービス向け会員マイページの受託開発

- 期間：開発：2022/07 - 09 ／ 修正・運用・保守：2022/10 - 2023/07
- 役割：Webアプリケーション開発 / 受託
- 担当工程：フロントエンド・API・AWS基盤の開発全般、修正・運用・保守
- 体制・規模：フロントエンド・API・AWS基盤の開発全般を担当。

会員向け動画閲覧Webアプリケーションを受託開発。Reactによる画面、外部動画APIと連携するバックエンド、AWS上の認証・配信環境まで開発全般を担当し、開発後も修正・運用・保守を行いました。

#### 動画閲覧・検索画面

React・Material UIでPC・スマートフォン対応の画面を実装。Vimeoの動画再生、タイトル・講師・カテゴリ・タグ検索、新着・おすすめ動画の表示に対応しました。

#### 外部API連携とAWS基盤

Amplify・Lambda・API Gatewayで動画情報取得APIを実装。Cognitoによるログイン、S3・CloudFrontによる配信環境、DynamoDBからの画面用パラメータ取得を構成しました。

#### 利用・管理上の改善

日本語検索の文字正規化、通信リトライ、読み込み中・エラー表示に対応。会員CSVからCognitoへ一括登録する処理も実装しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| フロントエンド | React / Material UI / JavaScript / TypeScript（一部） |
| 認証・API | AWS Amplify / Cognito / Lambda / API Gateway / Node.js / Vimeo API |
| 配信・データストア | S3 / CloudFront / DynamoDB |

使用技術：React / JavaScript / TypeScript（一部）/ Material UI / Node.js / AWS Amplify / Lambda / API Gateway / Cognito / S3 / CloudFront / DynamoDB / Vimeo API

### 決済プラットフォームのクラウド基盤設計・構築・IaC化

- 期間：2020/01 - 2023/06
- 役割：クラウドエンジニア / 業務委託
- 担当工程：基本設計・詳細設計・構築・設定・運用設計
- 体制・規模：インフラチーム3〜10名、全体約30名。1プロダクトを1名体制で担当。

QR決済・ウォレット基盤を提供するミッションクリティカルな決済プラットフォーム。Azureを主軸にAWSを併用し、アプリケーション開発チームと分担してクラウド基盤の設計・構築を担当しました。

#### 自動スケールを含む基盤設計

Azure Virtual Machine Scale Sets（VMSS）・App Serviceの自動スケール構成、Storage・Azure AD・DNS・Automationと、AWSを併用する基盤を設計・構築しました。

#### 環境構築のコード化とCI/CD

Terraformで開発・検証・本番のほぼ全環境をIaC化し、環境構築を数時間で実施できる状態に整備。GitHub ActionsによるCI/CDと組み合わせ、複数クラウド・複数環境を再現可能な形で管理しました。

#### コンテナ化・構成管理・監視設計

Docker・ECSによるコンテナ化、Ansibleによる構成管理を実施。Azure Monitor・Log Analytics・CloudWatchで監視とSlack・メール通知を設計しました。プロジェクトにより稼働率目標（SLA/SLO）の設定も担当しています。

#### 担当範囲

インフラチーム内で1プロダクトを1名で担当し、決済基盤に求められる信頼性と監視を設計しました。運用オンコールは担当範囲外です。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Linux (RHEL) / Ubuntu 18.04 LTS |
| データベース | Azure SQL Database / Amazon RDS |
| クラウド・ツール | Azure (VMSS / App Service / AD / Storage / DNS / Automation) / AWS (EC2 / ECS / S3 / ALB / CloudFront / API Gateway / Lambda) / Terraform / Ansible / Docker / GitHub Actions / Azure Monitor / Log Analytics / Amazon CloudWatch / PowerShell |

使用技術：Linux (RHEL) / Ubuntu 18.04 LTS / Azure SQL Database / Amazon RDS / Azure (VMSS / App Service / AD / Storage / DNS / Automation) / AWS (EC2 / ECS / S3 / ALB / CloudFront / API Gateway / Lambda) / Terraform / Ansible / Docker / GitHub Actions / Azure Monitor / Log Analytics / Amazon CloudWatch / PowerShell

### 公衆無線Wi-FiサービスのCMS基盤再構築・ログ調査改善

- 期間：2019/05 - 2019/12
- 役割：クラウドエンジニア / 業務委託
- 担当工程：基本設計・詳細設計・構築・設定・運用設計
- 体制・規模：チーム3〜10名（案件による）、全体約10名。

公衆無線Wi-Fi事業のCMS基盤の自社再構築と、肥大化した調査ログの分析基盤の改善を担当しました。

#### CMS基盤の再構築とIaC

他社ベンダーとの契約終了に伴い、CMS基盤を自社環境に再構築。CloudFormationでインフラをコード化し、同等の環境を短時間で再現できるようにしました。

#### ログ調査時間の短縮

2019/06からAmazon EMR・PySparkによるログ分析基盤を構築。生ログの解析に数日かかっていた調査を、数時間程度に短縮しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Amazon Linux / Linux (RHEL) |
| データベース | PostgreSQL |
| ミドルウェア | Apache Tomcat / Nginx / Apache HTTP Server |
| クラウド・ツール | Amazon EC2 / AWS CloudFormation / Docker / Ansible / Amazon EMR / PySpark / Python |

使用技術：Amazon Linux / Linux (RHEL) / PostgreSQL / Apache Tomcat / Nginx / Apache HTTP Server / Amazon EC2 / AWS CloudFormation / Docker / Ansible / Amazon EMR / PySpark / Python

### 公衆無線Wi-FiサービスのAWSコスト最適化

- 期間：2018/01 - 2019/04
- 役割：クラウドエンジニア / 業務委託
- 担当工程：基本設計・詳細設計・構築・設定・運用設計・保守・運用
- 体制・規模：チーム・全体3名。対象サーバ約10台。担当領域の設計〜構築〜運用は単独で遂行。

AWS上のサーバ群を対象に、リソースと構成の見直し、自動スケール、購入オプションの最適化を担当しました。

#### 時間帯別のリソース最適化

Auto Scalingで夜間は台数を縮小し、日中は拡張する構成を導入。過剰なリソースの削減とシステム構成の見直しを行いました。

#### AWSコストを3〜4割削減

スポットインスタンス・リザーブドインスタンスの活用と、時間帯別の台数調整を組み合わせ、AWSコストを3〜4割削減しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Amazon Linux / Linux (RHEL) / Windows Server |
| クラウド・ツール | Amazon EC2 / (Auto Scaling / Spot / RI) / Ansible / Jenkins |

使用技術：Amazon Linux / Linux (RHEL) / Windows Server / Amazon EC2 / (Auto Scaling / Spot / RI) / Ansible / Jenkins

### 公衆無線Wi-Fi基盤のAWS移行・新規構築・認証連携

- 期間：2014/12 - 2016/07
- 役割：クラウドエンジニア / 派遣
- 担当工程：基本設計・詳細設計・構築・設定・運用設計・保守・運用・障害対応
- 体制・規模：チーム20名、全体約20名。システム全体のサーバ規模は約1,000台。

公衆無線Wi-Fiシステムの設計・構築・運用と、オンプレミス環境の老朽化に伴うAWSへの移行を担当しました。

#### オンプレミスからAWSへの移行

公衆無線Wi-Fi基盤のクラウド移行を担当。基盤の設計・構築・運用を通じ、AWS環境とZabbixによる監視、構築自動化を整備しました。

#### 訪日外国人向けWi-Fiシステムの構築

2016/01〜07に約100台のサーバを含むシステムを構築。短い日程の中でAnsible・Jenkins・Gitによる自動構築を進め、拡張性と耐障害性を考慮した構成で、大きな問題なくサービスインしました。ベンダー調整も担当しました。

#### 海外ローミングの認証連携

FreeRADIUSによる海外ローミングサービス用の端末認証サーバを構築し、海外通信事業者との仕様調整を担当しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Amazon Linux / Linux (RHEL) / KVM |
| データベース | Amazon RDS / Amazon DynamoDB / Amazon ElastiCache / Amazon Redshift |
| ミドルウェア | Apache HTTP Server / BIND / Nginx / Apache Tomcat / FreeRADIUS / Zabbix |
| クラウド・ツール | Amazon EC2 / Ansible / Jenkins / Apache JMeter / F5 BIG-IP |

使用技術：Amazon Linux / Linux (RHEL) / KVM / Amazon RDS / Amazon DynamoDB / Amazon ElastiCache / Amazon Redshift / Apache HTTP Server / BIND / Nginx / Apache Tomcat / FreeRADIUS / Zabbix / Amazon EC2 / Ansible / Jenkins / Apache JMeter / F5 BIG-IP

### 通信キャリア向けシステムの保守・認証DB基盤構築

- 期間：2013/09 - 2014/11
- 役割：カスタマーエンジニア / 派遣（認証DB構築ではPM兼任）
- 担当工程：構築・設定・保守・運用
- 体制・規模：チーム10〜30名、全体約30名。システム全体約500台。認証DB構築は約30台・メンバー約10名。

携帯キャリア向け端末認証システムのサーバ・ネットワーク保守と、認証データベース基盤の新規構築を担当しました。

#### 大規模システムの保守・運用

約500台規模のシステムでサーバ・ネットワーク保守・運用と、保守業務のためのユーザー・ベンダー調整を担当。リソース分析や正常性確認を経験しました。

#### 認証DB基盤の構築とPM兼任

2014/01〜06に約30台の認証DBシステムを構築。約10名のメンバーの進捗管理・作業割り振り・品質管理を行い、Linux系サーバとCisco機器によるネットワーク構築、構築手順書の作成も担当しました。

#### 変更への対応と品質管理

リスケジュールや急な設計変更の際も、メンバーとの密なコミュニケーションで作業漏れと遅延を防ぎ、品質を担保しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Linux (RHEL) / Oracle Linux / Solaris / VMware ESXi |
| データベース | Oracle Database |
| クラウド・ツール | Cisco |

使用技術：Linux (RHEL) / Oracle Linux / Solaris / VMware ESXi / Oracle Database / Cisco

### 社内基幹ネットワークのリプレイス

- 期間：2010/01 - 2013/01
- 役割：社内SE
- 担当工程：基本設計・詳細設計・構築・設定・運用設計・保守・運用・障害対応
- 体制・規模：チーム・全体3名。L3スイッチ4台、L2スイッチ20台、クライアント約1,500台規模。

社内基幹ネットワークの更新に際し、設計・構築から運用までを担当。社内インフラ業務と並行して取り組みました。

#### 設計から機器実装・運用まで

ネットワーク設計、コンフィグ作成、機器の実装・配線、運用を一貫して担当。社内調整とドキュメント作成も行いました。

#### 冗長化・通信制御

GSRPによる冗長化、スタティックルーティング、QoS、タグVLAN、L2ループ検知を扱い、約1,500台のクライアントを支えるネットワークを構成しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| クラウド・ツール | Cisco / Allied Telesis / HP ProCurve / ALAXALA |

使用技術：Cisco / Allied Telesis / HP ProCurve / ALAXALA

### 社内インフラの設計・構築・運用

- 期間：2008/04 - 2013/01
- 役割：社内SE
- 担当工程：基本設計・詳細設計・構築・設定・運用設計・保守・運用・障害対応
- 体制・規模：チーム10名、全体約10名。サーバ約100台、クライアント約1,500台規模。

社内のLinux・Windowsサーバとネットワークを対象に、設計・構築・運用から障害対応、利用者支援まで担当しました。

#### Linux・Windowsサーバの設計・構築・運用

Linux系のWeb・メール・DNSサーバ、Windows系のWeb・ファイルサーバ、Active Directoryの設計・構築・運用を担当しました。

#### 障害対応・セキュリティ設定・利用者支援

ネットワーク・サーバの障害対応、ファイアウォールのセキュリティポリシー設定・運用、ヘルプデスクを担当。物理基盤の構築から運用・障害対応までの基礎と、部署間調整を経験しました。

#### 開発・運用環境

| 分類 | 環境 |
| --- | --- |
| OS・仮想化 | Linux (RHEL) / FreeBSD / Windows 2000 Server / Windows Server 2003 / Windows Server 2008 |
| データベース | Oracle Database / MySQL |
| ミドルウェア | Active Directory / Apache HTTP Server / IIS / BIND / Postfix / Squid |

使用技術：Linux (RHEL) / FreeBSD / Windows 2000 Server / Windows Server 2003 / Windows Server 2008 / Oracle Database / MySQL / Active Directory / Apache HTTP Server / IIS / BIND / Postfix / Squid

## 資格・仕事の進め方

基本情報技術者。LPIC-3・CCNAは取得歴あり（現在は失効）。

クラウド基盤の専門性を軸に、必要に応じてアプリケーションやSaaS連携まで担当します。IaCと設計ドキュメントで再現・引き継ぎができる状態をつくり、繰り返し作業は手順化・自動化して改善を続けます。
