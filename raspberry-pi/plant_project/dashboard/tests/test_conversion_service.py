# テスト対象：センサーデータ変換サービス
# 確認すること
# - 土壌水分率と光量スコアの換算
# - キャリブレーション値、範囲外、nullの境界

from django.test import SimpleTestCase

from dashboard.services.conversion_service import ConversionService


class ConversionServiceTests(SimpleTestCase):

    # 乾燥値と湿潤値のキャリブレーション値を、それぞれ0%と100%に変換する。
    def test_calculates_moisture_at_calibration_values(self):
        self.assertEqual(
            ConversionService.calculate_moisture(2550),
            0.0,
        )
        self.assertEqual(
            ConversionService.calculate_moisture(500),
            100.0,
        )

    # キャリブレーション範囲外の土壌値は、0～100%に丸められる。
    def test_clamps_moisture_to_zero_and_one_hundred(self):
        self.assertEqual(
            ConversionService.calculate_moisture(3000),
            0.0,
        )
        self.assertEqual(
            ConversionService.calculate_moisture(0),
            100.0,
        )

    # 暗い時と明るい時のキャリブレーション値を、それぞれ0と100に変換する。
    def test_calculates_light_score_at_calibration_values(self):
        self.assertEqual(
            ConversionService.calculate_light_score(4095),
            0.0,
        )
        self.assertEqual(
            ConversionService.calculate_light_score(0),
            100.0,
        )

    # キャリブレーション範囲外の光センサー値は、0～100に丸められる。
    def test_clamps_light_score_to_zero_and_one_hundred(self):
        self.assertEqual(
            ConversionService.calculate_light_score(5000),
            0.0,
        )
        self.assertEqual(
            ConversionService.calculate_light_score(-1),
            100.0,
        )

    # 生データがnullの場合、変換サービスは0.0を返す。
    def test_returns_zero_for_null_raw_values(self):
        self.assertEqual(
            ConversionService.calculate_moisture(None),
            0.0,
        )
        self.assertEqual(
            ConversionService.calculate_light_score(None),
            0.0,
        )