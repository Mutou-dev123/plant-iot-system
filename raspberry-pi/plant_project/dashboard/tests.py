import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from dashboard.models import Device, Plant, SensorLog
from dashboard.services.sensor_service import SensorService
from dashboard.forms import DeviceForm


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


class PlantArchiveTests(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create(custom_name="テスト植物")
        self.device = Device.objects.create(
            device_name="test_device",
            plant=self.plant,
        )
        self.log = SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.now(),
        )

    def test_archive_hides_plant_and_unassigns_device_but_keeps_log(self):
        response = self.client.post(
            reverse("plant_archive", args=[self.plant.pk])
        )

        self.assertRedirects(response, reverse("plant_list"))

        self.plant.refresh_from_db()
        self.device.refresh_from_db()
        self.log.refresh_from_db()

        self.assertTrue(self.plant.is_archived)
        self.assertIsNone(self.device.plant_id)
        self.assertEqual(self.log.plant_id, self.plant.pk)

        active_response = self.client.get(reverse("plant_list"))
        archived_response = self.client.get(
            reverse("plant_archived_list")
        )

        self.assertNotContains(active_response, "テスト植物")
        self.assertContains(archived_response, "テスト植物")

    def test_restore_does_not_reassign_device(self):
        self.plant.is_archived = True
        self.plant.save(update_fields=["is_archived"])
        self.device.plant = None
        self.device.save(update_fields=["plant"])

        response = self.client.post(
            reverse("plant_restore", args=[self.plant.pk])
        )

        self.assertRedirects(response, reverse("plant_archived_list"))

        self.plant.refresh_from_db()
        self.device.refresh_from_db()

        self.assertFalse(self.plant.is_archived)
        self.assertIsNone(self.device.plant_id)

    def test_archive_and_restore_require_post(self):
        archive_response = self.client.get(
            reverse("plant_archive", args=[self.plant.pk])
        )
        restore_response = self.client.get(
            reverse("plant_restore", args=[self.plant.pk])
        )

        self.assertEqual(archive_response.status_code, 405)
        self.assertEqual(restore_response.status_code, 405)

    def test_device_form_excludes_archived_plants(self):
        self.plant.is_archived = True
        self.plant.save(update_fields=["is_archived"])

        form = DeviceForm()

        self.assertNotIn(
            self.plant,
            form.fields["plant"].queryset,
        )