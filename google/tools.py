class ChatMessageProvider:
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            self.messages = [line.strip() for line in f if line.strip()]
        self.index = 0

    def get_chat_message(self):
        if self.index >= len(self.messages):
            self.index = 0            #wrap around to the beginning of messages
        message = self.messages[self.index]
        self.index += 1
        return message

class EmailMessageProvider:
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            self.messages = [line.strip() for line in f if line.strip()]
        self.index = 0

    def get_email_message(self):
        if self.index >= len(self.messages):
            self.index = 0            #wrap around to the beginning of messages
        message = self.messages[self.index]
        self.index += 1
        return message