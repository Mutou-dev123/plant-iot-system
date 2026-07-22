# ==========================================
# 植物管理ビュー
# ==========================================

from django.shortcuts import render

from dashboard.models import MyPlant


# ==========================================
# 植物一覧
# ==========================================
def index(request):

    plants = MyPlant.objects.all()

    context = {
        "plants": plants,
    }

    return render(
        request,
        "plants/index.html",
        context
    )