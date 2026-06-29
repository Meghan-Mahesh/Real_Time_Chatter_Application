from datetime import datetime

# ===============================
# CURRENT DATE & TIME (LOCAL)
# ===============================
def current_time() -> str:
    """
    Returns ISO formatted local time (server time)
    Example: 2026-02-13 14:32:10
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
