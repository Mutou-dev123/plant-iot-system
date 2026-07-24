from django import forms

from dashboard.models import Plant

class PlantForm(forms.ModelForm):

    class Meta:
        model = Plant

        fields = [
            "custom_name",
            "plant_master",
            "start_date",
        ]

        labels = {
            "custom_name": "植物名",
            "plant_master": "種類",
            "start_date": "栽培開始日",
        }

        widgets = {
            "custom_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "例：窓際のバジル",
                }
            ),
        }