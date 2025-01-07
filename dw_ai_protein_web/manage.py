#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import signal
from myapp.services import cleanup_container

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dw_ai_protein_web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # 기본 명령어 추가
    if len(sys.argv) == 1:  # 추가 명령어가 없으면 runserver 기본값 설정
        sys.argv += ["runserver", "0.0.0.0:8504"]

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, cleanup_container)
    signal.signal(signal.SIGTERM, cleanup_container)
    main()
