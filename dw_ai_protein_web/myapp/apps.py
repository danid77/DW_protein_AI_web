from django.apps import AppConfig


class MyappConfig(AppConfig): # 특별한 경우가 아니면 변경할 일 없음
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"
