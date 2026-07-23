# ==========================================
# 育成植物管理ビュー
# ==========================================

from django.shortcuts import render, redirect, get_object_or_404

from dashboard.models import MyPlant

from dashboard.forms import PlantForm


# ==========================================
# 1. 一覧
# ==========================================
def index(request):

    plants = MyPlant.objects.all()

    context = {
        "plants": plants,
    }

    return render(
        request,
        "plants/plant_list.html",
        context
    )


# ==========================================
# 2. 詳細
# ==========================================
def detail(request, plant_id):

    plant = get_object_or_404(
        MyPlant,
        pk=plant_id,
    )

    context = {
        "plant": plant,
    }

    return render(
        request,
        "plants/plant_detail.html",
        context,
    )


# ==========================================
# 3. 作成
# ==========================================
def create(request):

    if request.method == "POST":

        form = PlantForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("plant_list")

    else:
        form = PlantForm()

    context = {
        "title": "育成植物登録",
        "button": "登録",
        "form": form,
    }

    return render(
        request,
        "plants/plant_form.html",
        context,
    )

# ==========================================
# 4. 編集
# ==========================================
def edit(request, plant_id):

    plant = get_object_or_404(
        MyPlant,
        pk=plant_id,
    )

    if request.method == "POST":

        form = PlantForm(
            request.POST,
            instance=plant,
        )

        if form.is_valid():
            form.save()
            return redirect("plant_list")

    else:

        form = PlantForm(
            instance=plant,
        )

    context = {
        "title": "育成植物編集",
        "button": "更新",
        "form": form,
    }

    return render(
        request,
        "plants/plant_form.html",
        context,
    )

