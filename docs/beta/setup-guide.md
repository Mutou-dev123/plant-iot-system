> 📂 **docs > beta > setup-guide.md**

# セットアップ・運用手順（β版）

ここでは、ObserLeaf（β版）の環境構築手順と、日常的な運用操作についてまとめている。


## 1. 概要

β版の環境構築は、Raspberry Pi 5上のサーバー（Djangoアプリケーション）のセットアップと、ESP32へのファームウェア書き込みの2つからなる。

構築の前提は以下のとおりである。

- ESP32とRaspberry Pi 5が、同じローカルネットワークに接続できること
- Raspberry Pi 5に、Raspberry Pi OS等のLinux環境とPython 3が用意されていること
- 開発用PCに、ESP32のファームウェアをビルド・書き込みできる環境（PlatformIO）があること

各コンポーネントの仕様は、[ESP32仕様](esp32-spec.md)および[サーバー仕様](server-spec.md)を参照すること。


## 2. 必要なもの

| 区分 | 内容 |
| --- | --- |
| ハードウェア | Raspberry Pi 5、ESP32開発ボード（esp32dev）、センサー類（配線はESP32仕様の3章を参照） |
| サーバー側ソフトウェア | Python 3、Django、Gunicorn、WhiteNoise（バージョンはサーバー仕様の2章を参照） |
| 開発用ソフトウェア | PlatformIO（VS Code拡張機能）、Git |
| ネットワーク | Wi-Fiアクセスポイント（ESP32とRaspberry Pi 5が接続するもの） |


## 3. サーバー側セットアップ（Raspberry Pi 5）

### 3.1 リポジトリの取得

```bash
git clone https://github.com/Mutou-dev123/plant-iot-system.git
```

以降の手順では、リポジトリを取得した場所を `<リポジトリ>` と表記する。Djangoプロジェクトは `<リポジトリ>/raspberry-pi/plant_project` にある。手順にある `<リポジトリ>`、`<仮想環境>`、`<ユーザー名>`、`<Raspberry PiのIPアドレス>` は、実際の値に置き換えること。

### 3.2 Pythonパッケージの導入

仮想環境を作成し、有効化する（※1）。

```bash
cd <リポジトリ>/raspberry-pi/plant_project
python3 -m venv <仮想環境>
source <仮想環境>/bin/activate
```

必要なパッケージを導入する。

```bash
pip install -r requirements.txt
```

`requirements.txt` には、Django、Gunicorn、WhiteNoiseを記載する（※2）。

### 3.3 Djangoの環境設定

Djangoの秘密鍵と運用設定は、Raspberry Pi上の `/etc/obserleaf/django.env` に保存する。`DJANGO_SECRET_KEY` が未設定または空欄の場合、Djangoは起動しない。

初回セットアップ時に、次のコマンドで新しい鍵を生成する。鍵は画面に表示されず、ファイルはrootのみ読み書きできる権限（`0600`）で作成される。すでに環境ファイルがある場合は、鍵の生成をスキップして既存のファイルを使う。

```bash
sudo install -d -m 0700 /etc/obserleaf

sudo python3 - <<'PY'
import os
import secrets

# 新しいファイルを、所有者だけが読み書きできる権限で作成する。
os.umask(0o077)
with open("/etc/obserleaf/django.env", "x", encoding="utf-8") as env_file:
    env_file.write(f"DJANGO_SECRET_KEY={secrets.token_hex(32)}\n")
PY
```

`sudoedit /etc/obserleaf/django.env` でファイルを開き、生成済みの `DJANGO_SECRET_KEY` の行を残して、次の設定を追加する。すでに同じ項目がある場合は、既存の行を更新する。

```dotenv
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=<Raspberry PiのIPアドレス>
```

`DJANGO_ALLOWED_HOSTS` には、ブラウザやESP32が接続先URLで使うIPアドレスまたはホスト名を指定する。`http://`、ポート番号、末尾の `/` は省く。IPアドレスとホスト名の両方を使う場合は、カンマで区切る。

`DEBUG` は既定で無効であり、`DJANGO_DEBUG=1` を指定した場合のみ有効になる。本番運用では `DJANGO_DEBUG=0` を使う。環境ファイルと秘密鍵はリポジトリに含めない。

続けて、`obserleaf` を実行する一般ユーザーで、仮想環境を有効にし、`manage.py` があるディレクトリに移動する。次の関数をターミナルに入力すると、systemdが環境ファイルを読み込んだ状態で `manage.py` を実行できる。新しいターミナルを開いた場合は、同じ場所で仮想環境を有効にして関数を再定義する。

```bash
obserleaf_manage() {
    sudo systemd-run --wait --pty --collect \
        --uid="$(id -un)" \
        --working-directory="$PWD" \
        --property=EnvironmentFile=/etc/obserleaf/django.env \
        "$(command -v python)" manage.py "$@"
}
```

### 3.4 データベースの初期化

```bash
obserleaf_manage migrate
```

データベースファイル `sensor_data.db` が、プロジェクトフォルダ（`plant_project`）の直下に作成される。

### 3.5 静的ファイルの収集

```bash
obserleaf_manage collectstatic --noinput
```

WhiteNoiseは収集先の `staticfiles` フォルダからCSSやJavaScriptを配信する。初回構築時と静的ファイルの更新時に `collectstatic` を実行する。

### 3.6 管理ユーザーの作成

管理画面（`/admin/`）を利用する場合は、管理ユーザーを作成する。

```bash
obserleaf_manage createsuperuser
```

### 3.7 systemdへのサービス登録

Gunicornをsystemdのサービスとして登録する。新規登録時は、ユニットファイル `/etc/systemd/system/obserleaf.service` を以下の内容で作成する（※3）。

```ini
[Unit]
Description=ObserLeaf (Django + Gunicorn)
After=network.target

[Service]
User=<ユーザー名>
WorkingDirectory=<リポジトリ>/raspberry-pi/plant_project
EnvironmentFile=/etc/obserleaf/django.env
ExecStart=<仮想環境>/bin/gunicorn plant_project.wsgi:application --bind 0.0.0.0:8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`WorkingDirectory` と `ExecStart` のパスは絶対パスで指定する。新規登録後は、サービスを有効化して起動する。

```bash
sudo systemctl daemon-reload
sudo systemctl enable obserleaf.service
sudo systemctl start obserleaf.service
```

既存の `obserleaf.service` に環境ファイルの指定を追加する場合は、次のコマンドで追加設定ファイルを作成する。

```bash
sudo mkdir -p /etc/systemd/system/obserleaf.service.d
sudo tee /etc/systemd/system/obserleaf.service.d/django-env.conf >/dev/null <<'EOF'
[Service]
EnvironmentFile=/etc/obserleaf/django.env
EOF
sudo systemctl daemon-reload
sudo systemctl restart obserleaf.service
```

### 3.8 動作確認

サービスの状態と、読み込む環境ファイルのパスを確認する。

```bash
sudo systemctl status obserleaf.service --no-pager
sudo systemctl show obserleaf.service -p EnvironmentFiles
```

サービスが `active (running)` であり、`EnvironmentFiles` に `/etc/obserleaf/django.env` が含まれることを確認する。

Webブラウザで `http://<Raspberry PiのIPアドレス>:8000/` を開き、ダッシュボードが表示され、スタイルが適用されていることを確認する。


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

各URLに指定したIPアドレスまたはホスト名が、サーバー側の `DJANGO_ALLOWED_HOSTS` に含まれていることを確認する。

`config.h` にはWi-Fiのパスワード等の秘匿情報を含むため、リポジトリには含めない（`.gitignore` で除外されている）。

### 4.3 配線

センサーとLEDを接続する。ピン配置は[ESP32仕様](esp32-spec.md)の3章を参照すること。

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
| 起動 | `sudo systemctl start obserleaf.service` |
| 停止 | `sudo systemctl stop obserleaf.service` |
| 再起動 | `sudo systemctl restart obserleaf.service` |
| 状態確認 | `sudo systemctl status obserleaf.service --no-pager` |
| 直近のログ確認 | `sudo journalctl -u obserleaf.service -n 40 --no-pager` |

### 6.2 サーバーの更新

1. リポジトリの最新コードを取得する（`git pull`）。
2. Djangoプロジェクトのディレクトリに移動し、仮想環境を有効化する。依存パッケージに変更がある場合は `pip install -r requirements.txt` を実行する。
3. 3.3節の `obserleaf_manage` を定義し、`obserleaf_manage migrate` を実行する。
4. `obserleaf_manage collectstatic --noinput` で、WhiteNoiseが配信するCSSやJavaScriptを `staticfiles` に収集する。
5. `sudo systemctl restart obserleaf.service` で再起動し、ブラウザでダッシュボードとスタイルの表示を確認する。

環境変数化する前の版から更新する場合は、`migrate` の前に3.3節の手順で新しい鍵を生成する。公開済みの旧鍵は再利用しない。サービスを再起動する段階で、3.7節の既存サービス向け手順に従い `EnvironmentFile=` の追加設定を反映する。

### 6.3 ESP32の更新

ファームウェアを変更した場合は、開発用PCから再度ビルドと書き込みを行う。あわせて `config.h` の `FIRMWARE_VERSION` を更新する。

### 6.4 バックアップ

計測データは、データベースファイル `sensor_data.db`（プロジェクトフォルダ直下）に保存されている。定期的にこのファイルを別の場所へコピーすることで、バックアップとなる。コピーは、サービス停止中に行うことが望ましい。

ESP32の `config.h` は、環境を再構築できるよう別途控えを保管しておく。

### 6.5 設定変更

植物の登録やデバイス設定（計測間隔、各センサーの有効・無効）の変更は、Web画面および管理画面から行う。デバイス設定を変更すると設定バージョンが上がり、ESP32が次回の設定確認時に新しい設定を取得して反映する（仕組みはサーバー仕様の4.3を参照）。

Raspberry PiのIPアドレスや接続用ホスト名が変わった場合は、`sudoedit /etc/obserleaf/django.env` で `DJANGO_ALLOWED_HOSTS` を更新し、`sudo systemctl restart obserleaf.service` を実行する。ESP32の接続先URLが変わる場合は、`config.h` も更新して書き込み直す。

### 6.6 トラブルシューティング

| 症状 | 確認・対処 |
| --- | --- |
| サービスが起動せず、ログに `DJANGO_SECRET_KEY must be set.` と出る | `/etc/obserleaf/django.env` に `DJANGO_SECRET_KEY` が設定されていることを確認する。`sudo systemctl show obserleaf.service -p EnvironmentFiles` で、サービスがそのファイルを参照しているか確認する。 |
| ブラウザに `Bad Request (400)` が表示される | ブラウザのURLで使っているIPアドレスまたはホスト名が `DJANGO_ALLOWED_HOSTS` に含まれているか確認する。環境ファイルを修正したらサービスを再起動する。 |
| ダッシュボードは表示されるが、CSSが適用されない | 3.3節の `obserleaf_manage` を定義し、`obserleaf_manage collectstatic --noinput` を実行する。サービスを再起動してからページを再読み込みする。 |

直近のサービスログは `sudo journalctl -u obserleaf.service -n 40 --no-pager` で確認できる。


## 7. 関連ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [overview.md](overview.md) | システム概要、主な機能、動作環境 |
| [architecture.md](architecture.md) | システム構成、コンポーネントの役割 |
| [esp32-spec.md](esp32-spec.md) | ESP32の仕様（ピン配置、処理フロー、通信・時刻仕様等） |
| [server-spec.md](server-spec.md) | サーバーの仕様（内部構成、処理仕様、起動・運用） |
| [data-flow.md](data-flow.md) | データの流れと、APIごとのデータ項目 |
| [data-management.md](data-management.md) | データの保存・管理方針 |
| [er-diagram.md](er-diagram.md) | データベースのER図 |

---

※1 仮想環境のパスは、現在の環境に合わせて読み替えること。  
※2 GunicornとWhiteNoiseのバージョンは、仮想環境で `pip freeze` を実行して確認すること。  
※3 ユニットファイルの内容は構成例であり、実際の登録内容に合わせて調整すること。