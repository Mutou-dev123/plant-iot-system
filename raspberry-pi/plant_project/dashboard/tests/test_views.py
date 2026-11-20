# テスト対象：植物のアーカイブ・復元画面
# 確認すること
# - アーカイブ前後の一覧表示、デバイスの割当、過去ログの保持
# - 復元時のデバイスの割当と、アーカイブ・復元のHTTPメソッド

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from dashboard.models import Device, Plant, SensorLog


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

    # アーカイブすると植物は専用一覧に移り、デバイスの割当は解除され、過去ログは残る。
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

    # 植物を復元するとアーカイブ状態は解除され、デバイスは未割当のままになる。
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

    # アーカイブと復元のURLにGETでアクセスすると、どちらも405を返す。
    def test_archive_and_restore_require_post(self):
        archive_response = self.client.get(
            reverse("plant_archive", args=[self.plant.pk])
        )
        restore_response = self.client.get(
            reverse("plant_restore", args=[self.plant.pk])
        )

        self.assertEqual(archive_response.status_code, 405)
        self.assertEqual(restore_response.status_code, 405)