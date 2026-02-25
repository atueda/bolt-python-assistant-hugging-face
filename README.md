# AI エージェントアプリテンプレート (Bolt for Python)

この Bolt for Python のテンプレートは、[OpenAI](https://openai.com) のモデルを使って Slack 上で [AI アプリ](https://docs.slack.dev/ai/) を構築する方法を示しています。

---
## アプリ概要

このアプリをセットアップすると、以下のようなフローをもつ AI エージェントが利用できます。

1. ユーザーが Slack のサイドパネルにあるアシスタントを開くと、候補プロンプトが表示されます。
2. ユーザーがプロンプトを選択するかメッセージを送信すると、アプリは OpenAI の API を呼び出します。
3. 応答はテキストとタスクを組み合わせた形でストリーミングされます。
4. ユーザーはボタンでフィードバックを送信できます。

**新機能**

- OpenAI API が利用できない場合に自動で Hugging Face API にフォールバックする仕組みを追加しました。これにより、API エラー時にも継続的に応答を生成できます。
- `requirements.txt` に Hugging Face 用のライブラリを追加し、`.env.sample` に `HUGGINGFACE_API_KEY` の例も記載されています。

---
## セットアップ

開始する前に、アプリをインストールする権限を持つ開発用ワークスペースがあることを確認してください。まだ持っていない場合は、[ワークスペースを作成](https://slack.com/create)してください。

### 開発者プログラム

[Slack Developer Program](https://api.slack.com/developer-program) に参加すると、サンドボックス環境や開発用ツール、リソースへのアクセスが得られます。

---
## インストール

Slack CLI または他の開発ツールを使ってこのアプリをワークスペースに追加し、その後 **[Providers](#providers)** セクションで LLM の応答設定を行ってください。

<details><summary><strong>Slack CLI の利用</strong></summary>

OS に対応した最新版の Slack CLI をインストールします。

- [macOS & Linux 用 Slack CLI](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-mac-and-linux/)
- [Windows 用 Slack CLI](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-windows/)

初めて使用する場合はログインが必要です。

```sh
slack login
```

#### プロジェクトの初期化

```sh
slack create my-bolt-python-assistant --template slack-samples/bolt-python-assistant-template
cd my-bolt-python-assistant
```

#### Slack アプリの作成

次のコマンドで開発用ワークスペースに新しい Slack アプリを追加します。開発中は「local」環境を選択してください。

```sh
slack install
```

アプリが作成されたら LLM プロバイダーの設定を行います。

</details>

<details><summary><strong>ターミナルからの手動設定</strong></summary>

#### Slack アプリの作成

1. [https://api.slack.com/apps/new](https://api.slack.com/apps/new) にアクセスし、「From an app manifest」を選択します。
2. アプリをインストールしたいワークスペースを選択します。
3. `manifest.json` の内容をコピーして、テキストボックスの `*Paste your manifest code here*` に貼り付け（JSON タブ）し、 _Next_ をクリックします。
4. 設定内容を確認し、 _Create_ をクリックします。
5. 表示される画面で _Install to Workspace_ をクリックし、許可を与えます。その後アプリ設定ダッシュボードにリダイレクトされます。

#### 環境変数

アプリを実行するためにいくつかの環境変数を設定する必要があります。

1. `.env.sample` を `.env` にリネームします。
2. [こちらのリスト](https://api.slack.com/apps)からアプリ設定ページを開き、左メニューの _OAuth & Permissions_ をクリックして、_Bot User OAuth Token_ を `.env` の `SLACK_BOT_TOKEN` にコピーします。

```sh
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN
```

3. 左メニューの _Basic Information_ をクリックし、`connections:write` スコープ付きのアプリレベルトークンを作成します。そのトークンを `.env` の `SLACK_APP_TOKEN` にコピーします。

```sh
SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN
```

4. さらに Hugging Face フォールバックを利用する場合は、`.env` に以下を追加します。

```sh
HUGGINGFACE_API_KEY=YOUR_HUGGINGFACE_API_KEY
```

#### プロジェクトの初期化

```sh
git clone https://github.com/slack-samples/bolt-python-assistant-template.git my-bolt-python-assistant
cd my-bolt-python-assistant
```

#### Python 仮想環境のセットアップ

```sh
python3 -m venv .venv
source .venv/bin/activate  # Windows の場合は .\.venv\Scripts\Activate
```

#### 依存関係のインストール

```sh
pip install -r requirements.txt
```

</details>

---
## Providers

### OpenAI 設定

OpenAI モデルを使うには、[OpenAI ダッシュボード](https://platform.openai.com/api-keys)でシークレットキーを作成し、`.env` に `OPENAI_API_KEY` として保存します。

```zsh
OPENAI_API_KEY=YOUR_OPEN_API_KEY
```

**Hugging Face フォールバック**

OpenAI 呼び出しが失敗した場合、環境変数 `HUGGINGFACE_API_KEY` が設定されていれば Hugging Face の Chat Completion API へ自動的に転送されます。ローカル推論や他社モデルの利用が可能です。

---
## 開発

### アプリの起動

#### Slack CLI

```sh
slack run
```

#### ターミナル

```sh
python3 app.py
```

ボットと会話を始め、応答後にフィードバックボタンをクリックしてください。

### リント

```sh
# ルートディレクトリで ruff チェックを実行
ruff check

# ルートディレクトリでコード整形
ruff format
```

---
## プロジェクト構造

### `manifest.json`

Slack アプリの設定を定義するマニフェストです。予め構成を組み込んだアプリを作成したり、既存アプリの設定を更新できます。

### `app.py`

アプリのエントリーポイント。サーバーを起動する際に実行します。主にリクエストのルーティングに専念し、ロジックは他のモジュールに委譲します。

### `/listeners`

受信したリクエストはすべて「リスナー」へ振り分けられます。このディレクトリは Slack プラットフォーム機能別にリスナーを分類しており、例えば `/listeners/events` はイベントを処理し、`/listeners/shortcuts` はショートカットリク

**`/listeners/assistant`**

Slack の新しいアシスタント機能を設定し、ユーザーが AI チャットボットと対話できる専用サイドパネル UI を提供します。このモジュールには:

- 新しいアプリスレッド開始時に候補プロンプトを返す `assistant_thread_started.py`
- アプリスレッドや **Chat**、**History** タブからのメッセージに対し LLM 応答を生成する `message.py`

### `/agent`

`llm_caller.py` が OpenAI API を呼び出し、生成された応答を Slack 会話にストリーミングします。

`tools` ディレクトリには、LLM が呼び出すアプリ固有の関数が含まれます。

---
## アプリ配布 / OAuth

複数のワークスペースへ配布する予定がある場合に OAuth を実装してください。関連設定は `app_oauth.py` に記載されています。

OAuth を使うと、Slack はリクエストを送信するためのパブリック URL を必要とします。このテンプレ
# bolt-python-assistant-template
# bolt-python-assistant-hugging-face
# bolt-python-assistant-hugging-face
