# ==========================================
# デバイス管理サービス
# ==========================================

# ESP32デバイスの登録・取得を管理する
#
# ・deviceNameによるデバイス検索
# ・新規デバイス登録
# ・デバイス情報の取得

from dashboard.models import Device

class DeviceService:

    @staticmethod
    def get_or_create(data):
        mac_address = data["macAddress"].strip().upper()

        # 名前が同じESP32を区別できるよう、MACアドレスを名前に付ける
        mac_without_colons = mac_address.replace(":", "")
        name_prefix = data["deviceName"].strip()[:37]
        unique_device_name = f"{name_prefix}-{mac_without_colons}"

        device, created = Device.objects.get_or_create(
            mac_address=mac_address,
            defaults={
                "device_name": unique_device_name,
                "ip_address": data["ipAddress"],
                "firmware_version": data["firmwareVersion"],
                "reported_dht_enabled": data["dhtEnabled"],
                "reported_soil_enabled": data["soilEnabled"],
                "reported_light_enabled": data["lightEnabled"],
                "interval_seconds": 300,
            },
        )

        # デバイスの情報が存在しない場合
        if not created:
            device.ip_address = data["ipAddress"]
            device.firmware_version = data["firmwareVersion"]
            device.reported_dht_enabled = data["dhtEnabled"]
            device.reported_soil_enabled = data["soilEnabled"]
            device.reported_light_enabled = data["lightEnabled"]

            device.save(
                update_fields=[
                    "ip_address",
                    "firmware_version",
                    "reported_dht_enabled",
                    "reported_soil_enabled",
                    "reported_light_enabled",
                ]
            )

        return device