from django.shortcuts import render
from .models import SensorLogs, SystemSettings  # モデルインポート

# ダッシュボードのメイン画面表示
def index(request):

    # データベースから最新のセンサーログ1件だけ取得
    # idを最新順で並び替えて、その最初の1件を取得
    latest_log = SensorLogs.objects.order_by('-id').first()

    # 履歴グラフ・テーブル用に、直近20件のログを取得
    # 逆順に並び替えるため、一度リスト化
    history_logs = list(SensorLogs.objects.order_by('-id')[:20])
    # 画面のグラフや表は「古い順（左から右、上から下）」で見せるため、順序を反転
    history_logs.reverse()

    # 現在の計測間隔（秒）をDBから取得
    # system_settings テーブルの id=1 を取得
    settings = SystemSettings.objects.filter(id=1).first()
    # 設定がなければ、デフォルト「300秒（5分）」にする
    interval_seconds = settings.interval_seconds if settings else 300

    context = {
        'latest': latest_log,
        'history': history_logs,
        'interval': interval_seconds,
    }

    return render(request, 'dashboard/index.html', context)