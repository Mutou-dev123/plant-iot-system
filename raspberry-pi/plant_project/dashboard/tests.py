import json

from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from dashboard.models import Device, Plant, SensorLog, DailySensorSummary
from dashboard.services.sensor_service import SensorService
from dashboard.services.daily_sensor_summary_service import DailySensorSummaryService
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


class DailySensorSummaryModelTests(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create(custom_name="集計テスト植物")
        self.device = Device.objects.create(
            device_name="summary-test-device",
            plant=self.plant,
        )
        self.summary_date = date(2026, 11, 13)

    def _create_summary(self, **kwargs):
        return DailySensorSummary.objects.create(
            device=self.device,
            summary_date=self.summary_date,
            **kwargs,
        )

    def test_prevents_duplicate_summary_for_same_device_plant_and_date(self):
        self._create_summary(plant=self.plant)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_summary(plant=self.plant)

    def test_prevents_duplicate_unassigned_summary_for_same_device_and_date(self):
        self._create_summary()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_summary()

    def test_allows_unassigned_summaries_for_different_devices(self):
        self._create_summary()

        other_device = Device.objects.create(
            device_name="another-summary-device",
        )
        DailySensorSummary.objects.create(
            device=other_device,
            summary_date=self.summary_date,
        )

        self.assertEqual(DailySensorSummary.objects.count(), 2)

    def test_protects_device_and_plant_with_summary_from_delection(self):
        self._create_summary(plant=self.plant)

        with self.assertRaises(ProtectedError):
            self.device.delete()

        with self.assertRaises(ProtectedError):
            self.plant.delete()


class DailySensorSummaryServiceTests(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create(custom_name="集計対象植物")
        self.device = Device.objects.create(
            device_name="aggregation-test-device",
            plant=self.plant,
        )
        self.summary_date = date(2026, 11, 13)

    def test_aggregates_measurements_and_counts_non_null_values(self):
        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 1, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=20.0,
            humidity=50.0,
            moisture=None,
            light=100.0,
        )
        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 2, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=24.0,
            humidity=None,
            moisture=60.0,
            light=200.0,
        )

        summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        self.assertEqual(summary.log_count, 2)

        self.assertAlmostEqual(summary.temperature_avg, 22.0)
        self.assertEqual(summary.temperature_min, 20.0)
        self.assertEqual(summary.temperature_max, 24.0)
        self.assertEqual(summary.temperature_count, 2)

        self.assertEqual(summary.humidity_avg, 50.0)
        self.assertEqual(summary.humidity_count, 1)

        self.assertEqual(summary.moisture_avg, 60.0)
        self.assertEqual(summary.moisture_count, 1)

        self.assertAlmostEqual(summary.light_avg, 150.0)
        self.assertEqual(summary.light_count, 2)

    def test_recalculating_updates_existing_summary(self):
        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 1, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=20.0,
        )

        first_summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 2, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=24.0,
        )

        second_summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        self.assertEqual(first_summary.pk, second_summary.pk)
        self.assertEqual(DailySensorSummary.objects.count(), 1)
        self.assertAlmostEqual(second_summary.temperature_avg, 22.0)
        self.assertEqual(second_summary.temperature_count, 2)

    def test_returns_none_when_day_has_no_logs(self):
        summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        self.assertIsNone(summary)
        self.assertFalse(DailySensorSummary.objects.exists())