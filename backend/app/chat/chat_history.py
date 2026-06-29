from ..models import Message, User


def get_recent_messages(db, limit=50):
	# Perform a join to fetch message data along with the sender's username
	results = (
		db.query(
			Message.timestamp,  # msg[0]
			Message.id,  # msg[1]
			Message.content,  # msg[2]
			Message.sender_id,  # msg[3]
			Message.receiver_id,  # msg[4]
			Message.room,  # msg[5]
			User.username.label('sender_name'),  # msg[6] - Joined username
		)
		.join(User, Message.sender_id == User.id)
		.order_by(Message.timestamp.asc())
		.limit(limit)
		.all()
	)

	return results
