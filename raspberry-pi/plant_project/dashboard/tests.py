import json

from django.test import TestCase

from dashboard.models import Device, Plant, SensorLog
from dashboard.services.sensor_service import SensorService


class SensorLogPlantTests(TestCase):
    def _create_device(self, plant=None):
        return Device.objects.create(
            device_name="test-device",
            mac_address="AA:BB:CC:DD:EE:FF",
            plant=plant,
        )

    def _receive_sensor_data(self):
        payload = {
            "deviceName": "test-device",
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "ipAddress": "192.168.1.10",
            "firmwareVersion": "test",
            "timestamp": 1,
            "dhtEnabled": False,
            "soilEnabled": False,
            "lightEnabled": False,
            "temperature": None,
            "humidity": None,
            "soilRaw": None,
            "lightRaw": None,
        }
        SensorService.receive(json.dumps(payload))

    def test_receive_records_device_plant_on_sensor_log(self):
        plant = Plant.objects.create(custom_name="テスト植物")
        self._create_device(plant=plant)

        self._receive_sensor_data()

        log = SensorLog.objects.get()
        self.assertEqual(log.plant, plant)

    def test_receive_leaves_plant_unset_when_device_has_no_plant(self):
        self._create_device()

        self._receive_sensor_data()

        log = SensorLog.objects.get()
        self.assertIsNone(log.plant)

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