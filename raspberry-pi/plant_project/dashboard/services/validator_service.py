# ==========================================
# バリデーションサービス
# ==========================================

# ESP32から受信したJSONデータを検証する
#
# ・必須項目の確認
# ・データ型の確認
# ・センサー有効設定と計測値の整合性確認

import math

class ValidatorService:

    # 常に必要な項目
    REQUIRED_FIELDS = [
        "deviceName",
        "timestamp",
        "dhtEnabled",
        "soilEnabled",
        "lightEnabled",
    ]

    # センサーごとの計測値
    SENSOR_FIELDS = {
        "dht": ["temperature", "humidity"],
        "soil": ["soilRaw"],
        "light": ["lightRaw"],
    }

    @staticmethod
    def validate(data):

        # JSONのルートがオブジェクトか確認
        if not isinstance(data, dict):
            raise ValueError("JSON data must be an object.")

        # 必須項目の確認
        for field in ValidatorService.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(
                    f"Missing required field: {field}"
                )
        
        # デバイス名の確認
        if (
            not isinstance(data["deviceName"], str)
            or not data["deviceName"].strip()
        ):
            raise ValueError(
                "deviceName must be a non empty string."
        )

        # タイムスタンプの確認
        timestamp = data["timestamp"]

        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
        ):
            raise ValueError(
                "timestamp must be a finite number."
            )

        # センサー有効設定の確認
        enabled_fields = [
            "dhtEnabled",
            "soilEnabled",
            "lightEnabled",
        ]

        for field in enabled_fields:
            if not isinstance(data[field], bool):
                raise ValueError(
                    f"{field} must be a boolean."
                )

        # 有効なセンサーの計測値を検証
        for sensor, fields in ValidatorService.SENSOR_FIELDS.items():

            enabled = data[f"{sensor}Enabled"]

            if not enabled:
                continue

            for field in fields:

                # 計測値のキー自体は必須
                if field not in data:
                    raise ValueError(
                        f"Missing required field: {field}"
                    )

                value = data[field]

                # nullは読み取り失敗として許可
                if value is None:
                    continue

                # 数値型の確認
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                ):
                    raise ValueError(
                        f"{field} must be a number or null."
                    )

                # NaN・Infinityの確認
                if not math.isfinite(value):
                    raise ValueError(
                        f"{field} must be finite."
                    )
                
        # 土壌水分・光量の生データは整数であることを確認
        for sensor, field in [
            ("soil", "soilRaw"),
            ("light", "lightRaw"),
        ]:
            if not data[f"{sensor}Enabled"]:
                continue
            
            value = data[field]

            # nullは読み取り失敗として許可
            if value is None:
                continue

            if isinstance(value, bool) or isinstance(value, int):
                raise ValueError(
                    f"{field} must be an integer or null."
                )

            if not 0 <= value <= 4095:
                raise ValueError(
                    f"{field} must be between 0 and 4095."
                )