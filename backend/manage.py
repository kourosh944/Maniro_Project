#!/usr/bin/env python
"""ابزار خط‌فرمان مدیریتی Django."""
import os
import sys


def main():
    """نقطهٔ ورود اصلی برای اجرای دستورات مدیریتی."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django را نمی‌توان import کرد. مطمئن شوید که نصب شده و در "
            "PYTHONPATH قرار دارد. آیا virtual environment را فعال کرده‌اید؟"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
