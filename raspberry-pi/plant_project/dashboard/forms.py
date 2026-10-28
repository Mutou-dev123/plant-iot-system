from django import forms

from dashboard.models import Plant, Device


# ==========================================
# 植物管理フォーム
# ==========================================
class PlantForm(forms.ModelForm):

    class Meta:
        model = Plant

        fields = [
            "custom_name",
            "plant_master",
            "start_date",
        ]

        labels = {
            "custom_name": "植物名",
            "plant_master": "種類",
            "start_date": "栽培開始日",
        }

        widgets = {
            "custom_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "例：窓際のバジル",
                }
            ),
        }


# ==========================================
# デバイス管理フォーム
# ==========================================
class DeviceForm(forms.ModelForm):

    class Meta:
        model = Device

        fields = [
            "plant",
            "device_name",
            "wifi_ssid",
            "interval_seconds",
            "desired_dht_enabled",
            "desired_soil_enabled",
            "desired_light_enabled",
        ]

        labels = {
            "plant": "観測対象の植物",
            "device_name": "デバイス名",
            "wifi_ssid": "Wi-Fi SSID",
            "interval_seconds": "測定間隔（秒）",
            "desired_dht_enabled": "温湿度センサー（DHT）を使用する",
            "desired_soil_enabled": "土壌水分センサーを使用する",
            "desired_light_enabled": "光センサーを使用する",
        }

        widgets = {
            "device_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "例：リビングESP32",
                }
            ),
            "wifi_ssid": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "例：Home_WiFi",
                }
            ),
            "interval_seconds": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "min": 10,
                }
            ),
        }

    # ラズパイ側で希望設定を保存する関数
    def save(self, commit=True):
        instance = super().save(commit=False)

        config_fields = {
            "interval_seconds",
            "desired_dht_enabled",
            "desired_soil_enabled",
            "desired_light_enabled",
        }

        # 設定バージョンを更新
        if instance.pk and config_fields.intersection(self.changed_data):
            instance.config_version += 1

        if commit:
            instance.save()
            self.save_m2m()
        
        return instance