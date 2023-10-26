from transformers import pipeline


class Summarizer:
    MODEL = "Azma-AI/bart-conversation-summarizer"

    def __init__(self):
        self.pipeline = pipeline("summarization", model=self.MODEL)

    def summarize(self, text):
        return self.pipeline(text, min_length=25)[0]["summary_text"]


if __name__ == "__main__":
    summarizer = Summarizer()

    summarized_text = summarizer.summarize(
        """Laurie: So, what are your plans for this weekend?
Christie: I don’t know. Do you want to get together or something?
Sarah: How about going to see a movie? Cinemax 26 on Carson Boulevard is showing Enchanted. Laurie: That sounds like a good idea. Maybe we should go out to eat beforehand.
Sarah: It is fine with me. Where do you want to meet?
Christie: Let’s meet at Summer Pizza House. I have not gone there for a long time.
Laurie: Good idea again. I heard they just came up with a new pizza. It should be good because Summer Pizza House always has the best pizza in town.
Sarah: When should we meet?"""
    )

    print(summarized_text)
