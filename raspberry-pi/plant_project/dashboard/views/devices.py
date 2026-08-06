# ==========================================
# デバイス管理ビュー
# ==========================================

from django.shortcuts import render, redirect, get_object_or_404

from dashboard.models import Device

from dashboard.forms import DeviceForm


# ==========================================
# 1. 一覧
# ==========================================
def device_list(request):

    devices = Device.objects.all()

    context = {
        "devices": devices,
    }

    return render(
        request,
        "devices/device_list.html",
        context,
    )


# ==========================================
# 2. 詳細
# ==========================================
def device_detail(request, device_id):

    device = get_object_or_404(
        Device,
        pk=device_id,
    )

    context = {
        "device": device,
    }

    return render(
        request,
        "devices/device_detail.html",
        context,
    )


# ==========================================
# 3. 作成
# ==========================================
def device_create(request):

    if request.method == "POST":

        form = DeviceForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("device_list")

    else:
        form = DeviceForm()

    context = {
        "title": "デバイス登録",
        "button": "登録",
        "form": form,
    }

    return render(
        request,
        "devices/device_form.html",
        context,
    )


# ==========================================
# 4. 編集
# ==========================================
def device_edit(request, device_id):

    device = get_object_or_404(
        Device,
        pk=device_id,
    )

    if request.method == "POST":

        form = DeviceForm(
            request.POST,
            instance=device,
        )

        if form.is_valid():
            form.save()
            return redirect("device_list")

    else:

        form = DeviceForm(
            instance=device,
        )

        context = {
            "title": "デバイス編集",
            "button": "更新",
            "form": form,
        }

        return render(
            request,
            "devices/device_form.html",
            context,
        )


# ==========================================
# 5. 削除
# ==========================================
def device_delete(request, device_id):

    device = get_object_or_404(
        Device,
        pk=device_id,
    )

    if request.method == "POST":
        device.delete()

    return redirect("device_list")