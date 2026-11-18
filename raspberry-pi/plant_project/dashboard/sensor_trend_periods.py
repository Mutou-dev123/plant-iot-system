from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class CalendarMonths:
    """月ごとの日数が異なる歴月を表す。"""

    count: int

@dataclass(frozen=True)
class TrendPeriod:
    label: str
    duration: timedelta | CalendarMonths
    bucket_size: timedelta | CalendarMonths
    use_daily_summary: bool = False


DEFAULT_TREND_PERIOD = "24h"

# グループと期間の並び順をプルダウンにも使う。
PERIOD_GROUPS = {
    "時間": {
        "1h": TrendPeriod("1時間", timedelta(hours=1), timedelta(minutes=5)),
        "3h": TrendPeriod("3時間", timedelta(hours=3), timedelta(minutes=15)),
        "6h": TrendPeriod("6時間", timedelta(hours=6), timedelta(minutes=15)),
        "12h": TrendPeriod("12時間", timedelta(hours=12), timedelta(minutes=30)),
        "24h": TrendPeriod("24時間", timedelta(hours=24), timedelta(hours=1)),
    },
    "日・週": {
        "2d": TrendPeriod("2日間", timedelta(days=2), timedelta(hours=3)),
        "3d": TrendPeriod("3日間", timedelta(days=3), timedelta(hours=3)),
        "1w": TrendPeriod("1週間", timedelta(weeks=1), timedelta(days=1)),
        "2w": TrendPeriod("2週間", timedelta(weeks=2), timedelta(days=1)),
        "3w": TrendPeriod("3週間", timedelta(weeks=3), timedelta(days=1)),
    },
    "月・年": {
        "1m": TrendPeriod("1か月", CalendarMonths(1), timedelta(days=1)),
        "3m": TrendPeriod("3か月", CalendarMonths(3), timedelta(weeks=1)),
        "6m": TrendPeriod("6か月", CalendarMonths(6), CalendarMonths(1)),
        "1y": TrendPeriod("1年", CalendarMonths(12), CalendarMonths(1), use_daily_summary=True),
        "3y": TrendPeriod("3年", CalendarMonths(36), CalendarMonths(1), use_daily_summary=True),
        "5y": TrendPeriod("5年", CalendarMonths(60), CalendarMonths(1), use_daily_summary=True),
    },
}

# 集計処理は期間キーで設定を取得する。
TREND_PERIODS = {
    key: period
    for group in PERIOD_GROUPS.values()
    for key, period in group.items()
}

# Djangoのフォームでグループ付きの選択肢として使う。
TREND_PERIOD_CHOICES = [
    (group_label, [(key, period.label) for key, period in group.items()])
    for group_label, group in PERIOD_GROUPS.items()
]