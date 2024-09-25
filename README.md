# ProcessingJob Sample

## 概要

SageMakerでProcessingJobを使用するためのサンプルです。

## 環境構築

次の環境が必要です。

- AWS
- Linux

### S3のセットアップ

入出力先となるS3のパスとサンプルデータを設定します。

#### 1. バケットを作成する

任意のバケット名でS3バケットを作成してください。

#### 2. フォルダを作成する

作成したバケットの下に次の構成でフォルダを作成してください。

```
bucket-root/
  └──processing-job-sample/
       ├──input/
       ├──output/
       ├──package/
       └──workflow/
```

#### 3. サンプル入力ファイルを配置する

リポジトリの `input/sample_msg.txt` をS3上の `input/` に配置してください。

### ローカル側セットアップ

#### 1. 環境変数の設定

```bash
export BUCKET_NAME="xxx"  # 任意のS3バケット名
WORK_DIR=/path/to/workdir  # 任意のディレクトリ
```

#### 2. リポジトリのクローン

```bash
cd $WORK_DIR
```

```bash
git clone https://github.com/shohei-iida/processing-job-sample
```

#### 3. poetryによる仮想環境の有効化

```bash
sudo apt update
sudo apt install pipx
```

```bash
pipx install poetry
```

```bash
cd processing-job-sample/
```

```bash
poetry shell
poetry install
```

## つかいかた

### 1. ローカルで実行する

```bash
cd $WORK_DIR/processing-job-sample
python main_routine_local.py --input-dir input/ --out-dir output/
```

まずはProcessingJobに投げる前に、ローカルでコードの疎通を確認します。
エラーが発生しなければ次のステップに進みます。

### 2. ProcessingJobに投げる

```bash
cd $WORK_DIR/processing-job-sample
python trigger.py --job-name sample-job-1
```

実行に成功すれば、S3の `workflow` フォルダの下に結果が出力されます。
実行時のログはAWSコンソールからCloudWatchで確認できます。
