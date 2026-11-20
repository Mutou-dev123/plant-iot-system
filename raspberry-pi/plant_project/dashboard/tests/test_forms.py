# テスト対象：デバイス編集フォーム
# 確認すること
# - 観測対象として選択できる植物の絞り込み

from django.test import TestCase

from dashboard.forms import DeviceForm
from dashboard.models import Plant


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