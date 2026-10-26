# ==========================================
# バリデーションサービス
# ==========================================

# ESP32から受信したJSONデータを検証する
#
# ・必須項目の確認
# ・データ型の確認
# ・センサー有効設定と計測値の整合性確認

import math

import ipaddress
import math
import re

# re ... 正規表現（Regular Expression）を用いた文字列の
#        検索、抽出、置換、分割を行うための標準ライブラリ

class ValidatorService:

    # 常に必要な項目
    REQUIRED_FIELDS = [
        "deviceName",
        "macAddress",
        "ipAddress",
        "firmwareVersion",
        "timestamp",
        "dhtEnabled",
        "soilEnabled",
        "lightEnabled",
        "temperature",
        "humidity",
        "soilRaw",
        "lightRaw"
    ]

    # センサーごとの計測値
    SENSOR_FIELDS = {
        "dht": ["temperature", "humidity"],
        "soil": ["soilRaw"],
        "light": ["lightRaw"],
    }

    @staticmethod
    def validate(data):
        
        # JSONのトップレベルがオブジェクトか確認
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")

        # 必須項目の確認
        for field in ValidatorService.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # 文字列項目の確認
        for field in ("deviceName", "firmwareVersion"):
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")

        # MACアドレス形式の確認（例: AA:BB:CC:DD:EE:FF）
        mac_address = data["macAddress"]
        if (
            not isinstance(mac_address, str)
            or re.fullmatch(
                r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}",
                mac_address,
            ) is None
        ):
            raise ValueError("macAddress must be in XX:XX:XX:XX:XX:XX format")

        # IPアドレスの確認
        ip_address = data["ipAddress"]
        if not isinstance(ip_address, str):
            raise ValueError("ipAddress must be a string")

        try:
            ipaddress.ip_address(ip_address)
        except ValueError as error:
            raise ValueError("ipAddress must be a valid IP address") from error

        # timestampは正の整数とする
        timestamp = data["timestamp"]
        if type(timestamp) is not int or timestamp <= 0:
            raise ValueError("timestamp must be a positive integer")

        # センサー有効状態は真偽値とする
        enabled_fields = (
            "dhtEnabled",
            "soilEnabled",
            "lightEnabled",
        )
        for field in enabled_fields:
            if type(data[field]) is not bool:
                raise ValueError(f"{field} must be a boolean")

        # 温度・湿度は有限数値、またはnullを許可
        for field in ("temperature", "humidity"):
            value = data[field]
            if value is not None and (
                type(value) not in (int, float)
                or not math.isfinite(value)
            ):
                raise ValueError(f"{field} must be a finite number or null")

        # 土壌・光センサーの生データは0〜4095の整数、またはnull
        for field in ("soilRaw", "lightRaw"):
            value = data[field]
            if value is not None and (
                type(value) is not int
                or not 0 <= value <= 4095
            ):
                raise ValueError(f"{field} must be an integer from 0 to 4095 or null")

        # DHTでは温度・湿度が両方とも値、または両方ともnullであること
        if (data["temperature"] is None) != (data["humidity"] is None):
            raise ValueError(
                "temperature and humidity must both be values or both be null"
            )

        # 無効なセンサーの値はnullであること
        if not data["dhtEnabled"] and (
            data["temperature"] is not None
            or data["humidity"] is not None
        ):
            raise ValueError("Disabled DHT sensor values must be null")

        if not data["soilEnabled"] and data["soilRaw"] is not None:
            raise ValueError("Disabled soil sensor value must be null")

        if not data["lightEnabled"] and data["lightRaw"] is not None:
            raise ValueError("Disabled light sensor value must be null")