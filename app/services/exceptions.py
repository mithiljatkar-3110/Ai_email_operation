class DuplicateMessageError(Exception):
    def __init__(self, message_id: str) -> None:
        self.message_id = message_id
        super().__init__(f"Email with message_id '{message_id}' already exists")


class ThreadNotFoundError(Exception):
    def __init__(self, thread_id: str) -> None:
        self.thread_id = thread_id
        super().__init__(f"Thread '{thread_id}' not found")


class EmailNotFoundError(Exception):
    def __init__(self, email_id: str) -> None:
        self.email_id = email_id
        super().__init__(f"Email '{email_id}' not found")
