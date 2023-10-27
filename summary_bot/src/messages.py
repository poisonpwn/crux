from collections import deque
import datetime as dt
from discord import DeletedReferencedMessage, User
from discord.channel import TextChannel
from discord.enums import MessageType

from exceptions import (
    MessageQueueNotInitialized,
    MessageFetchError,
)


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

    def __str__(self):
        convo_lines = []
        for mesg in self.messages:
            message_content = str(mesg.content)
            convo_lines.append(f"{mesg.author.global_name}: {message_content}")
        return "\n".join(convo_lines)


class MessagesFetcher:
    SEARCH_LIMIT = 300
    ALLOWED_MESG_TYPES = [MessageType.default, MessageType.reply]

    def __init__(self, channel: TextChannel, exclude_predicate):
        """controls the operations for the message queue window
          for a specific channel

        Args:
            channel (TextChannel): the channel from which the messages are to be fetched
            exclude_predicate: func which acts on a message to return True if it is to
              be excluded from the queue
        """
        self.channel = channel
        self.should_exclude = lambda mesg: any(
            [
                mesg.type not in self.ALLOWED_MESG_TYPES,
                exclude_predicate(mesg),
            ]
        )
        self.messages_queue = None

    async def init_message_queue(self):
        """initialize the queue with SEARCH_LIMIT number of messages
        from history, excluding the ones which pass the exclude_predicate
        """
        self.messages_queue = deque()

        async for mesg in self.channel.history(limit=self.SEARCH_LIMIT):
            # ignore any messages that dont match this condition
            if self.should_exclude(mesg):
                continue

            self.messages_queue.appendleft(mesg)

    def update_message_queue(self, mesg):
        """append the new_message to message queue
        and pop off the oldest one


        Args:
          message(Message): the newest message in the channel

        Raises:
          MessageQueueNotInitialized,
            if init_message_queue was not previously ran (it checks if message queue is None)

        """
        if self.messages_queue is None:
            raise MessageQueueNotInitialized(
                "message queue has to be initialized first"
            )
        if self.should_exclude(mesg):
            return

        self.messages_queue.append(mesg)
        self.messages_queue.popleft()

    @staticmethod
    def __messages_time_range(messages_queue) -> TimeRange:
        """returns TimeRange between which the messaage queue spans
        Args:

          messages_queue: the messages queue for which the time range
            is to be calculated.
        """
        return TimeRange(
            messages_queue[0].created_at,
            messages_queue[-1].created_at,
        )

    def get_message_range(self, *args) -> deque:
        """
        get last messages from the channel

        Args:
          *args: stop_num; or start_num, stop_num (1 based indexing from the end)

        Returns:
        last stop_num messages if only stop_num is given as args is [stop_num]
        range of messagesstart_num to stop_num in 1 based indexing if args is [start_num, stop_num]
        """
        if self.messages_queue is None:
            raise Exception("message queue has to be initialized first")

        start = 1
        match (len(args)):
            case 1:
                stop = args[0]
            case 2:
                start, stop = args
            case _:
                raise (Exception("function only takes 1 or 2 arguments"))

        in_bounds = lambda index: 1 <= index <= len(self.messages_queue)
        if not all([in_bounds(start), in_bounds(stop), start < stop]):
            raise MessageFetchError(f"{start} to {stop}, not a valid message range,")

        messages_queue = self.messages_queue.copy()
        result_list = deque()
        for i in range(start, stop + 1):
            result_list.appendleft(messages_queue[-i])

        return result_list

    def get_till_last_message(self, query_user: User) -> deque:
        """
        returns the subsequence of the message queue which are to be processed
        i.e
        the messages till the users's last message (exclusive),
        OR
        if there are replies within that region to messages outside that region,
        all the messages till the earliest message that was replied to are returned
        which are to be processed for summarization

        Raises:
          SearchLimitExceeded:
            if user's last message was not found in message queue
            if earliest reply message was created before the time range of the message queue
        """
        if self.messages_queue is None:
            raise Exception("message queue has to be initialized first")

        messages_queue = self.messages_queue.copy()
        result_list = deque()
        time_range = self.__messages_time_range(messages_queue)
        earl_reply_time = dt.datetime.now(dt.timezone.utc)  # max value for now
        earl_reply_id = None

        for back_index, mesg in enumerate(reversed(messages_queue), start=1):
            if mesg.author == query_user:
                author_last_mesg_ind = len(messages_queue) - back_index
                break

            if mesg.reference is not None:
                if isinstance(
                    ref_mesg := mesg.reference.resolved, DeletedReferencedMessage
                ):
                    continue

                if ref_mesg.created_at not in time_range:
                    raise MessageFetchError(
                        "region contains references to messages are outside search scope"
                    )

                if ref_mesg.created_at < earl_reply_time:
                    earl_reply_time = ref_mesg.created_at
                    earl_reply_id = ref_mesg.id

            result_list.appendleft(mesg)
        else:
            raise MessageFetchError(
                f"{query_user.global_name}'s last message outside search scope."
            )

        if earl_reply_id is None:
            return result_list

        for index in reversed(range(author_last_mesg_ind + 1)):
            mesg = messages_queue[index]
            result_list.appendleft(mesg)
            if mesg.id == earl_reply_id:
                break

        return result_list
