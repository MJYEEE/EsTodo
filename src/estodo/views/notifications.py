"""Cross-platform notifications"""

import sys
from typing import Optional


class Notification:
    """Notification handler with fallback"""

    def __init__(self):
        self._plyer_available = False
        self._try_import_plyer()

    def _try_import_plyer(self):
        """Try to import plyer"""
        try:
            from plyer import notification
            self._plyer_notification = notification
            self._plyer_available = True
        except ImportError:
            self._plyer_available = False

    def notify(self, title: str, message: str, app_name: str = "EsTodo"):
        """Show a notification"""
        if self._plyer_available:
            self._notify_plyer(title, message, app_name)
        else:
            self._notify_print(title, message)

    def _notify_plyer(self, title: str, message: str, app_name: str):
        """Notify using plyer"""
        try:
            self._plyer_notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=10
            )
        except Exception:
            # Fallback to print
            self._notify_print(title, message)

    def _notify_print(self, title: str, message: str):
        """Fallback notification: print to console"""
        print(f"\n🔔 {title}")
        print(f"   {message}\n")


# Singleton instance
_notification: Optional[Notification] = None


def get_notifier() -> Notification:
    """Get the notification singleton"""
    global _notification
    if _notification is None:
        _notification = Notification()
    return _notification


def notify(title: str, message: str, app_name: str = "EsTodo"):
    """Show a notification"""
    get_notifier().notify(title, message, app_name)
