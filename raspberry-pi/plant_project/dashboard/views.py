# ==========================================
# ダッシュボードビュー
# ==========================================

# HTTPリクエストを受け付け、各サービスを呼び出してレスポンスを返却する 
#
# ・画面表示
# ・APIエンドポイント

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import PlantMaster, MyPlant, Device, SensorLog

from .services.sensor_service import SensorService

# ==========================================
# ダッシュボード画面表示
# ==========================================
def index(request):

    # データベースから最新のセンサーログ1件だけ取得
    latest_log = SensorLog.objects.order_by('-id').first()

    # 履歴グラフ・テーブル用に、直近20件を取得
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

    # POST以外は拒否
    if request.method != 'POST':
        return JsonResponse(
            {"status": "invalid_method"},
            status=405
        )

    try:

        # センサーデータ処理
        result = SensorService.receive(request.body)

        return JsonResponse(result)
    
    except Exception as e:

        return JsonResponse(
            {
                "status": "error",
                "message": str(e)
            },
            status=400
        )