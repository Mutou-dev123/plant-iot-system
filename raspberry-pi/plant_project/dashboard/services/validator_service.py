# ==========================================
# バリデーションサービス
# ==========================================

# ESP32から受信したJSONデータを検証する
#
# ・JSON形式の検証
# ・必須項目の確認
# ・データ型の確認

class ValidatorService:

    REQUIRED_FIELDS = [
        "deviceName",
        "timestamp",
        "temperature",
        "humidity",
        "soilRaw",
        "lightRaw"
    ]

    @staticmethod
    def validate(data):

        for field in ValidatorService.REQUIRED_FIELDS:

            if field not in data:
                raise ValueError(
                    f"Missing required field: {field}"
                )