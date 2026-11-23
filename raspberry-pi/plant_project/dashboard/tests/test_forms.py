# テスト対象：デバイス編集フォーム
# 確認すること
# - 観測対象として選択できる植物の絞り込み

from django.test import TestCase

from dashboard.forms import DeviceForm

from dashboard.models import (
    Device,
    Plant,
)


class DeviceFormTests(TestCase):

    def setUp(self):
        self.plant = Plant.objects.create(custom_name="テスト植物")

    # アーカイブ済みの植物は、フォームの観測対象の選択肢に含まれない。
    def test_device_form_excludes_archived_plants(self):
        self.plant.is_archived = True
        self.plant.save(update_fields=["is_archived"])

        form = DeviceForm()

        self.assertNotIn(
            self.plant,
            form.fields["plant"].queryset,
        )

    # 計測間隔を変更して保存すると、設定バージョンが1加算される。
    def test_increments_config_version_when_interval_changes(self):
        device = Device.objects.create(
            device_name="form-version-device",
            interval_seconds=300,
        )
        form = DeviceForm(
            data={
                "plant": "",
                "device_name": device.device_name,
                "wifi_ssid": "",
                "interval_seconds": 600,
                "desired_dht_enabled": True,
                "desired_soil_enabled": True,
                "desired_light_enabled": True,
            },
            instance=device,
        )

        self.assertTrue(form.is_valid())
        updated_device = form.save()

        self.assertEqual(updated_device.config_version, 2)

    # 設定項目を変更せずに保存しても、設定バージョンは加算されない。
    def test_does_not_increment_config_version_without_config_changes(self):
        device = Device.objects.create(
            device_name="unchanged_version_device",
            interval_seconds=300,
        )
        form = DeviceForm(
            data={
                "plant": "",
                "device_name": device.device_name,
                "wifi_ssid": "",
                "interval_seconds": 300,
                "desired_dht_enabled": True,
                "desired_soil_enabled": True,
                "desired_light_enabled": True,
            },
            instance=device,
        )

        self.assertTrue(form.is_valid())
        updated_device = form.save()

        self.assertEqual(updated_device.config_version, 1)