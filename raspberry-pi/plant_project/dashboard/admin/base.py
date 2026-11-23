# ==========================================
# 管理者用画面共通テンプレート
# ==========================================

from django.contrib import admin


class DescriptiveModelAdmin(admin.ModelAdmin):
    # 各管理クラスで説明文を設定する
    changelist_description = ""

    # 共通の一覧テンプレートを使う
    change_list_template = "admin/dashboard/change_list_with_description.html"

    def changelist_view(self, request, extra_context=None):
        # 説明文をテンプレートに渡す
        context = {
            **(extra_context or {}),
            "changelist_description": self.changelist_description,
        }
        return super().changelist_view(request, extra_context=context)
        