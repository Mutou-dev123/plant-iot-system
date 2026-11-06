> 📂 **docs > beta > setup-guide.md**

# セットアップ・運用手順（β版）

ここでは、ObserLeaf（β版）の環境構築手順と、日常的な運用操作についてまとめている。



## 1. 概要

β版の環境構築は、Raspberry Pi 5上のサーバー（Djangoアプリケーション）のセットアップと、ESP32へのファームウェア書き込みの2つからなる。

構築の前提は以下のとおりである。

- ESP32とRaspberry Pi 5が、同じローカルネットワークに接続できること
- Raspberry Pi 5に、Raspberry Pi OS等のLinux環境とPython 3が用意されていること
- 開発用PCに、ESP32のファームウェアをビルド・書き込みできる環境（PlatformIO）があること

各コンポーネントの仕様そのものは、ESP32仕様（esp32-spec.md）およびサーバー仕様（server-spec.md）を参照すること。本書は手順のみを扱う。



## 2. 必要なもの

| 区分 | 内容 |
| --- | --- |
| ハードウェア | Raspberry Pi 5、ESP32開発ボード（esp32dev）、センサー類（配線はESP32仕様の3章を参照） |
| サーバー側ソフトウェア | Python 3、Django、Gunicorn、WhiteNoise（バージョンはサーバー仕様の2章を参照） |
| 開発用ソフトウェア | PlatformIO（VS Code拡張機能）、Git |
| ネットワーク | Wi-Fiアクセスポイント（ESP32とRaspberry Pi 5が接続するもの） |



## 3. サーバー側セットアップ（Raspberry Pi 5）

### 3.1 リポジトリの取得

```
git clone https://github.com/Mutou-dev123/plant-iot-system.git
```

以降の手順では、リポジトリを取得した場所を `<リポジトリ>` と表記する。Djangoプロジェクトは `<リポジトリ>/raspberry-pi/plant_project` にある。

### 3.2 Pythonパッケージの導入

仮想環境を作成し、有効化する（※1）。

```
cd <リポジトリ>/raspberry-pi/plant_project
python -m venv <仮想環境>
source <仮想環境>/bin/activate
```

必要なパッケージを導入する。

```
pip install -r requirements.txt
```

`requirements.txt` には、Django、Gunicorn、WhiteNoiseを記載する（※2）。

### 3.3 データベースの初期化

```
python manage.py migrate
```

データベースファイル `sensor_data.db` が、プロジェクトフォルダ（`plant_project`）の直下に作成される。

### 3.4 静的ファイルの収集

```
python manage.py collectstatic
```

本システムではWhiteNoiseが静的ファイルを配信し、収集先（`staticfiles` フォルダ）から読み込む設定になっているため、初回構築時と静的ファイルの変更時に実行が必要である。

### 3.5 管理ユーザーの作成

管理画面（`/admin/`）を利用する場合は、管理ユーザーを作成する。

```
python manage.py createsuperuser
```

### 3.6 systemdへのサービス登録

Gunicornをsystemdのサービスとして登録する。ユニットファイル `/etc/systemd/system/obserleaf.service` を、以下の内容で作成する（※3）。

```ini
[Unit]
Description=ObserLeaf (Django + Gunicorn)
After=network.target

[Service]
User=<ユーザー名>
WorkingDirectory=<リポジトリ>/raspberry-pi/plant_project
ExecStart=<仮想環境>/bin/gunicorn plant_project.wsgi:application --bind 0.0.0.0:8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

サービスを有効化し、起動する。

```
sudo systemctl daemon-reload
sudo systemctl enable obserleaf
sudo systemctl start obserleaf
```

### 3.7 動作確認

サービスの状態を確認する。

```
sudo systemctl status obserleaf
```

Webブラウザから `http://<Raspberry PiのIPアドレス>:8000/` にアクセスし、ダッシュボードが表示されればサーバー側の構築は完了である。



## 4. ESP32側セットアップ

### 4.1 プロジェクトを開く

開発用PCで、PlatformIO（VS Code拡張機能）から `esp32-sensor` フォルダを開く。ボードやライブラリ等のビルド設定は `platformio.ini` に定義されている。

### 4.2 設定ファイルの作成

`esp32-sensor/src/config/config.h.example` をコピーし、`config.h` を作成する。

作成した `config.h` に、環境に合わせた値を設定する。

| 項目 | 設定内容 |
| --- | --- |
| `DEVICE_NAME` | デバイスの表示名 |
| `FIRMWARE_VERSION` | ファームウェアのバージョン |
| `SENSOR_DHT_ENABLED` / `SENSOR_SOIL_ENABLED` / `SENSOR_LIGHT_ENABLED` | 各センサーの有効・無効の初期値 |
| `WIFI_LIST` | 接続先Wi-FiのSSIDとパスワード（複数登録可） |
| `API_URL` | 計測データ送信用URL。Raspberry PiのIPアドレスとポート8000で指定する |
| `DEVICE_CONFIG_API_URL` | デバイス設定取得用URL。同上 |
| `DEVICE_CONFIG_APPLIED_API_URL` | 適用済み設定報告用URL。同上 |

`config.h` にはWi-Fiのパスワード等の秘匿情報を含むため、リポジトリには含めない（`.gitignore` で除外されている）。

### 4.3 配線

センサーとLEDを接続する。ピン配置はESP32仕様（esp32-spec.md）の3章を参照すること。

### 4.4 ビルドと書き込み

ESP32を開発用PCにUSB接続し、PlatformIOからビルドと書き込み（Upload）を実行する。

書き込み後、シリアルモニタ（115200bps）で以下のログを確認する。

- Wi-Fiへの接続
- NTPによる時刻同期
- サーバーへの計測データ送信



## 5. 疎通確認

サーバーとESP32の両方が起動した状態で、以下を確認する。

1. Webブラウザでダッシュボードを開き、接続したデバイスが表示されること（初回送信時にデバイスは自動登録される。仕組みはサーバー仕様の4.1を参照）
2. 計測間隔ごとに、新しい計測データがダッシュボードへ反映されること
3. ESP32のシリアルログに、送信エラーが出ていないこと



## 6. 運用

### 6.1 サービスの操作

| 操作 | コマンド |
| --- | --- |
| 起動 | `sudo systemctl start obserleaf` |
| 停止 | `sudo systemctl stop obserleaf` |
| 再起動 | `sudo systemctl restart obserleaf` |
| 状態確認 | `sudo systemctl status obserleaf` |
| ログ確認 | `sudo journalctl -u obserleaf` |

### 6.2 サーバーの更新

コードを更新した場合は、以下の手順で反映する。

1. リポジトリの最新コードを取得する（`git pull`）
2. 依存パッケージに変更がある場合は、導入し直す（`pip install -r requirements.txt`）
3. データベースの変更を反映する（`python manage.py migrate`）
4. 静的ファイルを収集し直す（`python manage.py collectstatic`）
5. サービスを再起動する（`sudo systemctl restart obserleaf`）

### 6.3 ESP32の更新

ファームウェアを変更した場合は、開発用PCから再度ビルドと書き込みを行う。あわせて `config.h` の `FIRMWARE_VERSION` を更新する。

### 6.4 バックアップ

計測データは、データベースファイル `sensor_data.db`（プロジェクトフォルダ直下）にすべて保存されている。定期的にこのファイルを別の場所へコピーすることで、バックアップとなる。コピーは、サービス停止中に行うことが望ましい。

ESP32の `config.h` はリポジトリに含まれないため、環境を再構築できるよう、別途控えを保管しておく。

### 6.5 設定変更

植物の登録やデバイス設定（計測間隔、各センサーの有効・無効）の変更は、Web画面および管理画面から行う。デバイス設定を変更すると設定バージョンが上がり、ESP32が次回の設定確認時に新しい設定を取得して反映する（仕組みはサーバー仕様の4.3を参照）。



## 7. 関連ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| overview.md | システム概要、主な機能、動作環境 |
| architecture.md | システム構成、コンポーネントの役割 |
| esp32-spec.md | ESP32の仕様（ピン配置、処理フロー、通信・時刻仕様等） |
| server-spec.md | サーバーの仕様（内部構成、処理仕様、起動・運用） |
| data-flow.md | データの流れと、APIごとのデータ項目 |
| data-management.md | データの保存・管理方針 |
| er-diagram.md | データベースのER図 |



---

※1 仮想環境の利用有無と、そのパスは、現在の環境に合わせて読み替えること。
※2 GunicornとWhiteNoiseのバージョンは、現在の環境で `pip freeze` を実行して確定させること。
※3 ユニットファイルの内容は構成例であり、実際の登録内容と異なる場合は実態に合わせて修正すること。
