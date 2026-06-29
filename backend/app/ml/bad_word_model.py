from sqlalchemy.orm import Session
from ..models import User

# ===============================
# BAD WORD LIST (extendable)
# ===============================
BAD_WORDS = [
    "idiot",
    "stupid",
    "hate",
    "fool",
    "damn",
    "shit"
]


# ===============================
# CHECK BAD WORD
# ===============================
def contains_bad_word(message: str) -> bool:
    message = message.lower()
    for word in BAD_WORDS:
        if word in message:
            return True
    return False


# ===============================
# HANDLE WARNING & BLOCK LOGIC
# ===============================
def handle_bad_word(
    user: User,
    message: str,
    db: Session
):
    """
    Returns:
    - None → clean message
    - dict → warning or block response
    """

    if not contains_bad_word(message):
        return None

    user.warning_count += 1

    # 🚫 3rd violation → BLOCK
    if user.warning_count >= 3:
        user.is_blocked = True
        db.commit()
        return {
            "type": "block",
            "message": "🚫 You are blocked due to repeated policy violations."
        }

    db.commit()

    return {
        "type": "warning",
        "message": f"⚠ Warning {user.warning_count}/2: Bad language detected."
    }
