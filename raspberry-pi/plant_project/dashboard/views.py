from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import PlantMaster, MyPlant, Device, SensorLog

# ==========================================
# ダッシュボード画面表示
# ==========================================
def index(request):

    # データベースから最新のセンサーログ1件だけ取得
    latest_log = SensorLog.objects.order_by('-id').first()

    # 履歴グラフ・テーブル用に、直近の20件六を取得
    history_logs = list(SensorLog.objects.order_by('-id')[:20])
    history_logs.reverse()

    # 画面表示用の計測間隔(秒)を取得
    # 細心のログがあればそのデバイスの設定値、なければデフォルト(300秒)にする
    if latest_log:
        interval_seconds = latest_log.device.interval_seconds
    else:
        interval_seconds = 300

    context = {
        'latest': latest_log,
        'history': history_logs,
        'interval': interval_seconds,
    }

    return render(request, 'dashboard/index.html', context)


# ==========================================
# ESP32からのデータ受信用API
# ==========================================
@csrf_exempt    # ESP32からの通信にはセキュリティトークンがないため、例外設定にする
def api_receive_data(request):
    if request.method == 'POST':
        try:
            # 1. ESP32から送られてきたJSONをPythonの辞書に変換
            data = json.loads(request.body)

            # 2. データの取り出し
            # デバイス識別名を受け取る
            device_name = data.get('deviceName', 'ESP_UNKNOWN')
            temp = data.get('temperature')
            hum = data.get('humidity')
            soil_raw = data.get('soilRaw')
            light_raw = data.get('lightRaw')

            # 3. デバイスの自動判定と新規登録
            # DBから指定された device_name を探す。なければ計測時間のデフォルト300秒で新規登録
            # 植物（my_plant）はNULL（未設定 = 不明な植物）になる
            device_instance, created = Device.objects.get_or_create(
                device_name=device_name,
                defaults={'interval_seconds': 300}
            )

            # 4. データの変形と整形（ESP32の12ビットADC: 0 ~ 4095に対応）
            # 【土壌水分】 ％に変換
            DRY_VALUE = 3500    # 乾いているとき
            WET_VALUE = 1500    # 湿っているとき
            moisture_pct = 0.0
            if soil_raw is not None:
                moisture_pct = (soil_raw - DRY_VALUE) / (WET_VALUE - DRY_VALUE) * 100
                moisture_pct = round(max(0, min(100, moisture_pct)), 1)

            # 【光量】 1日の累計計算用に 0 ~ 100 のスコアに変換
            DARK_VALUE = 4095   # 暗いとき → スコア 0
            BRIGHT_VALUE = 0    # 明るいとき → スコア 100
            light_score = 0.0
            if light_raw is not None:
                light_score = (light_raw - DARK_VALUE) / (BRIGHT_VALUE - DARK_VALUE) * 100
                light_score = round(max(0, min(100, light_score)), 1)

            # 5. DBへ保存
            SensorLog.objects.create(
                device=device_instance,
                soil_raw=soil_raw,
                light_raw=light_raw,
                moisture=moisture_pct,
                light=light_score,
                temperature=temp,
                humidity=hum
            )

            # 6. そのESP32単体専用に設定されている計測間隔を返す
            current_interval = device_instance.interval_seconds

            return JsonResponse({"status": "success", "next_interval": current_interval})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        
    return JsonResponse({"status": "invalid_method"}, status=405)