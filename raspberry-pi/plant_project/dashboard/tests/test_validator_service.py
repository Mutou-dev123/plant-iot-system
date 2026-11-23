# テスト対象：センサーデータのバリデーションサービス
# 確認すること
# - 必須項目、数値、null、センサー有効状態の検証

from copy import deepcopy

from django.test import SimpleTestCase

from dashboard.services.validator_service import ValidatorService


class ValidatorServiceTests(SimpleTestCase):

    def setUp(self):
        self.valid_data = {
            "deviceName": "test-device",
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "ipAddress": "192.168.1.10",
            "firmwareVersion": "test",
            "timestamp": 1,
            "dhtEnabled": True,
            "soilEnabled": True,
            "lightEnabled": True,
            "temperature": 20.0,
            "humidity": 50.0,
            "soilRaw": 2000,
            "lightRaw": 1000,
        }

    # すべての項目が正しいデータは検証を通過する。
    def test_accepts_valid_data(self):
        ValidatorService.validate(self.valid_data)

    # 必須項目が欠けている場合は検証に失敗する。
    def test_rejects_missing_required_field(self):
        data = deepcopy(self.valid_data)
        del data["deviceName"]

        with self.assertRaises(ValueError):
            ValidatorService.validate(data)

    # 温度と湿度が両方nullなら、DHTの未計測値として許可する。
    def test_accepts_null_temperature_and_humidity(self):
        data = deepcopy(self.valid_data)
        data["temperature"] = None
        data["humidity"] = None

        ValidatorService.validate(data)

    # 温度と湿度の片方だけがnullの場合は検証に失敗する。
    def test_rejects_temperature_and_humidity_with_mismatched_nulls(self):
        data = deepcopy(self.valid_data)
        data["temperature"] = None

        with self.assertRaises(ValueError):
            ValidatorService.validate(data)

    # 温度と湿度に数値以外または有限でない値が入ると検証に失敗する。
    def test_rejects_non_finite_temperature_and_humidity(self):
        invalid_values = ("20", float("nan"), float("inf"))

        for field in ("temperature", "humidity"):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    data = deepcopy(self.valid_data)
                    data[field] = value

                    with self.assertRaises(ValueError):
                        ValidatorService.validate(data)

    # 土壌・光量センサーの生データは、範囲の端の値も許可する。
    def test_accepts_sensor_raw_boundary_values(self):
        for field in ("soilRaw", "lightRaw"):
            for value in (0, 4095, None):
                with self.subTest(field=field, value=value):
                    data = deepcopy(self.valid_data)
                    data[field] = value

                    ValidatorService.validate(data)

    # 土壌・光量センサーの生データが整数の範囲外なら検証に失敗する。
    def test_rejects_sensor_raw_out_of_range_values(self):
        invalid_values = (-1, 4096, 1.5)

        for field in ("soilRaw", "lightRaw"):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    data = deepcopy(self.valid_data)
                    data[field] = value

                    with self.assertRaises(ValueError):
                        ValidatorService.validate(data)

    # 無効なセンサーに計測値が入っている場合は検証に失敗する。
    def test_rejects_values_for_disabled_sensors(self):
        cases = (
            ("dhtEnabled", "temperature", 20.0),
            ("soilEnabled", "soilRaw", 2000),
            ("lightEnabled", "lightRaw", 1000),
        )

        for enabled_field, value_field, value in cases:
            with self.subTest(enabled_field=enabled_field):
                data = deepcopy(self.valid_data)
                data[enabled_field] = False
                data[value_field] = value

                with self.assertRaises(ValueError):
                    ValidatorService.validate(data)