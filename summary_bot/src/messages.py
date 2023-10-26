from collections import deque
import datetime as dt
from discord import DeletedReferencedMessage, User
from discord.channel import TextChannel
from discord.enums import MessageType


class TimeRange:
    def __init__(self, start_time, end_time):
        if not start_time < end_time:
            raise Exception("TimeRange has to be forward ordered")
        self.start_time = start_time
        self.end_time = end_time

    def __contains__(self, time):
        return self.start_time <= time <= self.end_time


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


class MessagesFetcher:
    SEARCH_LIMIT = 300
    ALLOWED_MESG_TYPES = [MessageType.default, MessageType.reply]

    def __init__(self, channel: TextChannel, exclude_predicate):
        self.channel = channel
        self.exclude_predicate = exclude_predicate

    async def init_message_queue(self):
        self.messages_queue = deque()

        async for mesg in self.channel.history(limit=300):
            should_ignore = any(
                [
                    mesg.type not in self.ALLOWED_MESG_TYPES,
                    self.exclude_predicate(mesg),
                ]
            )
            # ignore any messages that dont match this condition
            if should_ignore:
                continue

            self.messages_queue.appendleft(mesg)

    def update_message_queue(self, mesg):
        if self.messages_queue is None:
            raise Exception("message queue has to be initialized first")
        if self.exclude_predicate(mesg):
            return

        self.messages_queue.append(mesg)
        self.messages_queue.popleft()

    @staticmethod
    def __time_range(queue):
        return TimeRange(queue[0].created_at, queue[-1].created_at)

    def get_summary_messages(self, query_user: User):
        if self.messages_queue is None:
            raise Exception("message queue has to be initialized first")
        messages_queue = self.messages_queue.copy()
        result_list = deque()
        time_range = self.__time_range(messages_queue)
        earl_reply_time = dt.datetime.now(dt.timezone.utc)  # max value for now
        earl_reply_id = None

        for back_index, mesg in enumerate(reversed(messages_queue), start=1):
            if mesg.author == query_user:
                author_last_mesg_ind = len(messages_queue) - back_index
                break

            if (
                mesg.reference is not None
                and (ref_mesg := mesg.reference.resolved)
                is not DeletedReferencedMessage
            ):
                if ref_mesg.created_at not in time_range:
                    raise Exception("Summary Limit Exceeded")

                if ref_mesg.created_at < earl_reply_time:
                    earl_reply_time = ref_mesg.created_at
                    earl_reply_id = ref_mesg.id

            result_list.appendleft(mesg)
        else:
            raise Exception("Summary Limit Exceeded")

        if earl_reply_id is None:
            return result_list

        for index in reversed(range(author_last_mesg_ind + 1)):
            mesg = messages_queue[index]
            result_list.appendleft(mesg)
            if mesg.id == earl_reply_id:
                break

        return result_list
