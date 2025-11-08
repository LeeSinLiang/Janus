# create a debug print wrapper that prints === DEBUG === before the message and === END DEBUG === after the message
def debug_print(message: str, *args, **kwargs):
	print("================================= DEBUG ================================")
	print(message, *args, **kwargs)
	print("================================= END DEBUG ================================")