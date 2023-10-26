from transformers import pipeline


class Conversation:
    def __init__(self, messages):
        self.messages = messages

    @staticmethod
    def _sanitize(string: str):
        return string.replace("\n", " ")

    def __str__(self):
        convo_lines = []
        for mesg in self.messages:
            sanitized_content = self._sanitize(str(mesg.content))
            convo_lines.append(f"{mesg.author.global_name}: {sanitized_content}")
        return "\n".join(convo_lines)


class Summarizer:
    MODEL = "Azma-AI/bart-conversation-summarizer"

    def __init__(self):
        self.pipeline = pipeline("summarizer", model=self.MODEL)

    def summarize(self, text):
        len_bounds = {
            "min_length": round(0.2 * len(text)),
            "max_length": round(0.8 * len(text)),
        }
        return self.pipeline(text, **len_bounds)
