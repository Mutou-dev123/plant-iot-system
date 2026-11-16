# ==========================================
# 日別集計ビュー
# ==========================================

from django.shortcuts import render
from django.utils import timezone

from dashboard.forms import DailySummaryFilterForm
from dashboard.models import DailySensorSummary


def daily_summary_list(request):
    latest_date = (
        DailySensorSummary.objects
        .order_by("-summary_date")
        .values_list("summary_date", flat=True)
        .first()
    )
    default_date = latest_date or timezone.localdate()

    form = DailySummaryFilterForm(
        request.GET or None,
        initial={"summary_date": default_date},
    )

    if form.is_bound:
        if form.is_valid():
            selected_date = form.cleaned_data["summary_date"] or default_date
        else:

            selected_date = None
    else:
        selected_date = default_date

    summaries = DailySensorSummary.objects.none()

    if selected_date is not None:
        summaries = (
            DailySensorSummary.objects
            .filter(summary_date=selected_date)
            .select_related("device", "plant")
            .order_by("device__device_name", "plant__custom_name")
        )

    return render(
        request,
        "daily_summaries/daily_summary_list.html",
        {
            "form": form,
            "selected_date": selected_date,
            "summaries": summaries,
        },
    )