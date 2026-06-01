# 🪴植物環境可視化システム
# テスト

### 植物の状態をリアルタイムで可視化し、環境変化を判断できるIoTモニタリングシステム

### 📌 概要

- 植物の生育に影響する環境データ（気温・湿度・土壌水分）をセンサーで取得し、データの保存・可視化（数値・グラ  フ・メッセージ表示）を行うIoTシステム。

- ユーザーはブラウザからリアルタイムで環境状態を確認でき、植物の状態を直感的に把握することができる。

***

### 🎯 作成目的

- IoTシステム（センサー・エッジ処理・Web可視化）の一連のデータフローを実装するため

- 植物の生育と環境データの関係を定量的に観測するため

- データ可視化による意思決定支援の仕組みを構築するため

***

### 🚀 主な機能

#### ■ データ取得
- 温湿度・土壌水分センサーによるデータ取得
- Raspberry Piによる定期収集

#### ■ データ処理
- しきい値判定ロジックによる状態分類
- リアルタイムデータ処理

#### ■ データ保存
- CSV / SQLiteによる履歴管理

#### ■ 可視化
- StreamlitによるWeb表示
- matplotlibによるグラフ描画 

#### ■ 状態フィードバック
- 環境状態に応じたメッセージ表示
- UI色変化による直感的可視化

***

### ⚙️ 使用技術

- Python  
  センサーデータ取得、しきい値判定、保存処理、Web表示処理を実装

- Streamlit  
  センサーデータのリアルタイム可視化用Webアプリとして使用

- matplotlib  
  環境データのグラフ描画に使用

- SQLite / CSV  
  センサーデータの保存および履歴管理に使用

***

### 🔌 使用デバイス

- Raspberry Pi 5  
  センサーデータ取得及びシステム全体の制御用デバイスとして使用

- DHT11  
  温度・湿度データ取得用センサーとして使用
  
- ADC0834-N  
  土壌水分センサーのアナログ値をデジタル変換するために使用
  
- 静電容量式土壌水分センサー v1.2  
  植物周辺の土壌水分量測定用センサーとして使用

***

### 📁 フォルダ構成と各バージョンの役割

```mermaid
graph LR
    Root["📁 plant-iot-system"]
    
    Root --> Alpha["🟢 alpha_app.py <br>(アルファ版: 基本/CSV保存)"]
    Root --> Beta["🟠 beta_app.py <br>(ベータ版: しきい値機能)"]
    
    %% プロダクション版を1つのノードでまとめてから枝分かれさせる
    Root --> Prod["🟣 プロダクション版 (最終版)"]
    Prod --> Logger["📄 sensor_logger.py (BEロガー)"]
    Prod --> App["📄 sensor_app.py (FE表示)"]
    Prod --> DB["🗄️ sensor_data.db (SQLite)"]
    
    Root --> RM["📄 README.md"]

    %% スタイル設定
    classDef root fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    classDef alpha fill:#e8f5e9,stroke:#388e3c,1px,color:#000
    classDef beta fill:#fff3e0,stroke:#f57c00,1px,color:#000
    classDef prod fill:#ede7f6,stroke:#5e35b1,2px,color:#000
    classDef common fill:#f5f5f5,stroke:#616161,1px,color:#000

    class Root root
    class Alpha alpha
    class Beta beta
    class Prod,Logger,App,DB prod
    class RM common
```

***

### 🧩 システム構成図

#### 1. 🟢 アルファ版のシステム構成図（前期成果物）

すべての処理（データ取得・保存・画面表示）が、1つのプログラム（alpha_app.py）の中で完結し、CSVへ保存するシンプルなプロトタイプ構成です。

```mermaid
graph TD
    subgraph Sensors ["Sensors"]
        DHT11["温湿度センサー DHT11"]
        Soil["静電容量式土壌水分センサー v1.2"]
    end

    subgraph Edge_Device ["Edgeデバイス"]
        ADC["ADC0834-N ADコンバータ"]
        RPI["Raspberry Pi 5"]
    end

    subgraph Python_System ["単一システム: alpha_app.py"]
        Collect["センサーデータ取得"]
        Logic["しきい値判定"]
        Save["データ保存処理"]
        Web["Streamlit Web表示"]
    end

    subgraph Storage ["Storage"]
        DB["📁 CSVファイル (sensor_data.csv)"]
    end

    subgraph Client ["Client"]
        Browser["PCブラウザ"]
    end

    %% 接続関係
    DHT11 --> RPI
    Soil --> ADC
    ADC --> RPI

    RPI --> Collect
    Collect --> Logic
    Logic --> Save
    Save --> DB
    
    DB --> Web
    Web --> Browser

    %% 色設定
    classDef sensor fill:#dff5df,color:#000,stroke:#333,stroke-width:2px
    classDef edge fill:#ffe8cc,color:#000,stroke:#333,stroke-width:2px
    classDef python fill:#fff4cc,color:#000,stroke:#333,stroke-width:2px
    classDef storage fill:#dbe9ff,color:#000,stroke:#333,stroke-width:2px
    classDef client fill:#f2f2f2,color:#000,stroke:#333,stroke-width:2px

    class DHT11,Soil sensor
    class ADC,RPI edge
    class Collect,Logic,Save,Web python
    class DB storage
    class Browser client
```

#### 2. 🟣 プロダクション版のシステム構成図（最終版）

アルファ版の「Sensors」「Edgeデバイス」の基盤はそのままに、Pythonシステムを**常時稼働のバックエンド（ロガー）**と、**いつでも起動できるフロントエンド（表示画面）**に完全分離。保存先も堅牢な**SQLite**へと進化させた構成です。


```mermaid
graph TD
    subgraph Sensors ["Sensors"]
        DHT11["温湿度センサー DHT11"]
        Soil["静電容量式土壌水分センサー v1.2"]
    end

    subgraph Edge_Device ["Edgeデバイス"]
        ADC["ADC0834-N ADコンバータ"]
        RPI["Raspberry Pi 5"]
    end

    %% アルファ版のひとまとめから、バックエンドとフロントエンドに分離
    subgraph Backend ["バックエンド: sensor_logger.py"]
        Collect["センサーデータ取得"]
        Logic["しきい値判定"]
        Save["SQLite保存処理"]
    end

    subgraph Storage ["Storage"]
        DB[("🗄️ SQLite (sensor_data.db)")]
    end

    subgraph Frontend ["フロントエンド: sensor_app.py"]
        Load["データ読み込み / 期間抽出"]
        Web["Streamlit Web表示"]
    end

    subgraph Client ["Client"]
        Browser["PCブラウザ"]
    end

    %% 接続関係（物理層はアルファ版と共通）
    DHT11 --> RPI
    Soil --> ADC
    ADC --> RPI

    %% バックエンド側の独立したデータフロー
    RPI --> Collect
    Collect --> Logic
    Logic --> Save
    Save --> DB

    %% フロントエンド側の独立したデータフロー
    DB --> Load
    Load --> Web
    Web --> Browser

    %% 色設定（アルファ版のトーン＆マナーを完全継承）
    classDef sensor fill:#dff5df,color:#000,stroke:#333,stroke-width:2px
    classDef edge fill:#ffe8cc,color:#000,stroke:#333,stroke-width:2px
    classDef python fill:#fff4cc,color:#000,stroke:#333,stroke-width:2px
    classDef storage fill:#dbe9ff,color:#000,stroke:#333,stroke-width:2px
    classDef client fill:#f2f2f2,color:#000,stroke:#333,stroke-width:2px

    class DHT11,Soil sensor
    class ADC,RPI edge
    class Collect,Logic,Save,Load,Web python
    class DB storage
    class Browser client
```

***

### 🚧 開発状況

- Raspberry Piセットアップ完了
- センサー（温湿度・土壌水分）によるデータ取得完了
- リアルタイムグラフ表示機能実装済み
- CSV保存機能実装済み
- しきい値判定による状態分類ロジック実装済み
- StreamlitによるWeb可視化実装済み
- SSH接続環境構築完了

***

### 🔮 今後の実装予定

- SQLiteによる永続データ管理への移行
- UI改善（視認性・色設計の最適化）
- データ履歴の長期トレンド分析機能
- 異常検知アラート機能の追加
