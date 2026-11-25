# テスト対象：デバイス設定・計測データ受信・グラフデータ取得API
# 確認すること
# - 希望設定の取得と、適用済み設定バージョンの記録
# - 未登録デバイスや不正なリクエストに対するHTTPステータス
# - 計測データの保存と、グラフ用の直近20件の取得

from datetime import datetime, timedelta, timezone as datetime_timezone
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from dashboard.models import Device, SensorLog


class DeviceConfigAPITests(TestCase):

    mac_address = "AA:BB:CC:DD:EE:FF"
    unknown_mac_address = "00:11:22:33:44:55"

    def setUp(self):
        self.device = Device.objects.create(
            device_name="config-api-device",
            mac_address=self.mac_address,
            config_version=3,
            applied_config_version=2,
            interval_seconds=120,
            desired_dht_enabled=True,
            desired_soil_enabled=False,
            desired_light_enabled=True,
        )

    def _report(self, version, mac_address=None):
        return self.client.post(
            reverse("api_report_applied_config"),
            {
                "macAddress": mac_address or self.mac_address,
                "applied_config_version": version,
            },
            content_type="application/json",
        )

    # 設定取得APIは、希望設定とそのバージョンを返す。
    def test_get_returns_desired_config(self):
        response = self.client.get(
            reverse("api_device_config"), {"macAddress": self.mac_address}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "config_version": 3,
                "interval_seconds": 120,
                "sensors": {"dht": True, "soil": False, "light": True},
            },
        )

    # 未登録のMACアドレスで設定を取得すると、404を返す。
    def test_get_returns_404_for_unknown_device(self):
        response = self.client.get(
            reverse("api_device_config"), {"macAddress": self.unknown_mac_address}
        )

        self.assertEqual(response.status_code, 404)

    # 希望バージョンと一致する報告を保存し、同期済みとして返す。
    def test_report_records_desired_version_as_up_to_date(self):
        response = self._report(3)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "recorded",
                "applied_config_version": 3,
                "config_version": 3,
                "up_to_date": True,
            },
        )
        self.device.refresh_from_db()
        self.assertEqual(self.device.applied_config_version, 3)

    # 古い報告を受け取っても、保存済みの適用バージョンを維持する。
    def test_report_does_not_roll_back_applied_version(self):
        response = self._report(1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["applied_config_version"], 2)
        self.assertIs(response.json()["up_to_date"], False)
        self.device.refresh_from_db()
        self.assertEqual(self.device.applied_config_version, 2)

    # 希望バージョンを超える報告には409を返し、保存済みの値を維持する。
    def test_report_returns_409_for_version_newer_than_desired(self):
        response = self._report(4)

        self.assertEqual(response.status_code, 409)
        self.device.refresh_from_db()
        self.assertEqual(self.device.applied_config_version, 2)

    # 未登録のMACアドレスから適用済み設定を報告すると、404を返す。
    def test_report_returns_404_for_unknown_device(self):
        self.assertEqual(self._report(3, self.unknown_mac_address).status_code, 404)


class SensorReceiveAPITests(TestCase):

    url_name = "api_receive_data"

    # 正常な計測データを受信すると、ログを保存して次回の計測間隔を返す。
    def test_post_accepts_valid_measurement(self):
        response = self.client.post(
            reverse(self.url_name),
            {
                "deviceName": "receive-api-device",
                "macAddress": "AA:BB:CC:DD:EE:FF",
                "ipAddress": "192.168.1.10",
                "firmwareVersion": "test",
                "timestamp": 1_790_000_000,
                "dhtEnabled": True,
                "soilEnabled": False,
                "lightEnabled": False,
                "temperature": 22.0,
                "humidity": 45.0,
                "soilRaw": None,
                "lightRaw": None,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "next_interval": 300})
        self.assertEqual(SensorLog.objects.get().temperature, 22.0)

    # 必須項目が欠けている場合は400を返し、ログは作成されない。
    def test_post_rejects_missing_required_fields(self):
        response = self.client.post(
            reverse(self.url_name), {}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertFalse(SensorLog.objects.exists())

    # 計測データ受信APIにGETでアクセスすると、405を返す。
    def test_get_returns_405(self):
        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["status"], "invalid_method")


class ChartDataAPITests(TestCase):

    # 直近20件を計測日時の昇順で返し、温度・湿度の欠損は null のまま返す。
    def test_returns_latest_twenty_in_measurement_order_with_nulls(self):
        device = Device.objects.create(device_name="chart-api-device")
        start = datetime(2026, 11, 13, tzinfo=datetime_timezone.utc)

        # ログの作成順と計測日時の順序が異なるデータを用意する。
        SensorLog.objects.bulk_create(
            SensorLog(
                device=device,
                measured_at=start + timedelta(minutes=minute),
                temperature=None if minute == 10 else minute,
                humidity=None if minute == 10 else 40 + minute,
                moisture=60 + minute,
            )
            for minute in reversed(range(22))
        )

        with timezone.override(ZoneInfo("Asia/Tokyo")):
            response = self.client.get(reverse("api_chart_data"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "labels": [f"09:{minute:02}:00" for minute in range(2, 22)],
                "temperature": [None if n == 10 else n for n in range(2, 22)],
                "humidity": [None if n == 10 else 40 + n for n in range(2, 22)],
                "moisture": list(range(62, 82)),
            },
        )