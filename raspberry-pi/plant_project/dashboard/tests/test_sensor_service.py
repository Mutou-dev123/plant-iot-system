# テスト対象：センサーデータの受信サービス
# 確認すること
# - 受信時の植物の割当ログに記録し、割当変更後も過去のログを保持する
# - 計測日ごとの集計タスクを作成し、再受信時は既存タスクを再処理できる状態に戻す

import json
from datetime import date, datetime, timezone as datetime_timezone

from django.test import TestCase

from dashboard.models import DailySensorAggregationTask, Device, Plant, SensorLog
from dashboard.services.sensor_service import SensorService


class SensorLogPlantTests(TestCase):

    def _create_device(self, plant=None):
        return Device.objects.create(
            device_name="test-device",
            mac_address="AA:BB:CC:DD:EE:FF",
            plant=plant,
        )

    def _receive_sensor_data(self, timestamp=1):
        payload = {
            "deviceName": "test-device",
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "ipAddress": "192.168.1.10",
            "firmwareVersion": "test",
            "timestamp": timestamp,
            "dhtEnabled": False,
            "soilEnabled": False,
            "lightEnabled": False,
            "temperature": None,
            "humidity": None,
            "soilRaw": None,
            "lightRaw": None,
        }
        SensorService.receive(json.dumps(payload))

    # デバイスに植物が割り当てられていれば、受信したログにも同じ植物を記録する。
    def test_receive_records_device_plant_on_sensor_log(self):
        plant = Plant.objects.create(custom_name="テスト植物")
        self._create_device(plant=plant)

        self._receive_sensor_data()

        log = SensorLog.objects.get()
        self.assertEqual(log.plant, plant)

    # 植物が未割当のデバイスから受信したログは、植物を空欄のまま保存する。
    def test_receive_leaves_plant_unset_when_device_has_no_plant(self):
        self._create_device()

        self._receive_sensor_data()

        log = SensorLog.objects.get()
        self.assertIsNone(log.plant)

    # 割当先を変更した後も、変更前後のログにはそれぞれ受信時点の植物が残る。
    def test_changing_device_plant_does_not_change_existing_logs(self):
        original_plant = Plant.objects.create(custom_name="変更前の植物")
        new_plant = Plant.objects.create(custom_name="変更後の植物")
        device = self._create_device(plant=original_plant)

        self._receive_sensor_data()

        device.plant = new_plant
        device.save(update_fields=["plant"])
        self._receive_sensor_data()

        logs = list(SensorLog.objects.order_by("id"))
        self.assertEqual(
            [log.plant_id for log in logs],
            [original_plant.id, new_plant.id],
        )

    # UTCと日本時間で日付が異なる計測では、日本時間の日付に未処理タスクを作る。
    def test_receive_creates_pending_task_for_japan_date(self):
        plant = Plant.objects.create(custom_name="タスク対象植物")
        device = self._create_device(plant=plant)

        # 2026-11-12 15:00 UTC は、日本時間の11月13日 00:00
        timestamp = int(
            datetime(
                2026, 11, 12, 15, 0,
                tzinfo=datetime_timezone.utc,
            ).timestamp()
        )
        self._receive_sensor_data(timestamp=timestamp)

        task = DailySensorAggregationTask.objects.get()
        self.assertEqual(task.device, device)
        self.assertEqual(task.plant, plant)
        self.assertEqual(task.summary_date, date(2026, 11, 13))
        self.assertEqual(task.status, DailySensorAggregationTask.Status.PENDING)
        self.assertEqual(SensorLog.objects.count(), 1)

    # 植物が未割当でも、植物なしの未処理タスクを作る。
    def test_receive_creates_unassigned_task_when_device_has_no_plant(self):
        self._create_device()

        self._receive_sensor_data()

        task = DailySensorAggregationTask.objects.get()
        self.assertIsNone(task.plant)
        self.assertEqual(task.status, DailySensorAggregationTask.Status.PENDING)

    # 同じ集計対象を再受信すると、試行回数を残して既存タスクを未処理に戻す。
    def test_receive_requeues_existing_task_without_creating_duplicate(self):
        plant = Plant.objects.create(custom_name="再試行対象植物")
        self._create_device(plant=plant)
        self._receive_sensor_data()

        task = DailySensorAggregationTask.objects.get()
        task.status = DailySensorAggregationTask.Status.FAILED
        task.attempt_count = 2
        task.last_error = "一時的なエラー"
        task.save(update_fields=["status", "attempt_count", "last_error"])

        self._receive_sensor_data()

        task.refresh_from_db()
        self.assertEqual(DailySensorAggregationTask.objects.count(), 1)
        self.assertEqual(task.status, DailySensorAggregationTask.Status.PENDING)
        self.assertEqual(task.last_error, "")
        self.assertEqual(task.attempt_count, 2)
        self.assertEqual(SensorLog.objects.count(), 2)