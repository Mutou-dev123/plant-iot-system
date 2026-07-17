# ==========================================
# センサーデータ変換サービス
# ==========================================

# 生データを画面表示・保存用データへ変換する
#
# ・土壌水分の割合変換
# ・光量スコアの算出
# ・各種センサーデータの変換

class ConversionService:
    
    # 【土壌水分を％に変換】

    # キャリブレーション値
    DRY_VALUE = 3500    # 乾燥時
    WET_VALUE = 1500    # 湿潤時

    @staticmethod
    def calculate_moisture(raw):

        if raw is None:
            return 0.0
        
        # %変換式
        value = (
            (raw - ConversionService.DRY_VALUE)
            / (ConversionService.WET_VALUE - ConversionService.DRY_VALUE)
            * 100
        )

        return round(max(0, min(100, value)), 1)
    

    # 【光量をスコアに変換】

    # キャリブレーション値
    DARK_VALUE = 4095   # 暗い時
    BRIGHT_VALUE = 0    # 明るい時

    @staticmethod
    def calculate_light_score(raw):

        if raw in None:
            return 0.0

        # スコア変換式
        value = (
            (raw - ConversionService.DARK_VALUE)
            / (ConversionService.BRIGHT_VALUE - ConversionService.DARK_VALUE)
            * 100
        )

        return round(max(0, min(100, value)), 1)