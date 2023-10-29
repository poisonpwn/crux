# Crux Round 3 Tasks
## Extending Chronoscript
1) make the usage of chronoscript interactive from the 
commandline
2) Add the ability to exclude certain sections of courses from the created timetable
3) Add exam schedule fit feature where a user can specify
what kind of exam schedule they desire.

it is mentioned this should be done in a seperate fork of the main repository.
repo link: https://github.com/poisonpwn/chronoscript

### Features
1) choice of courses, choice of lite order, exam schedule fit etc are now prompted to the user from the command line
2) users is now prompted to exclude certain courses of their choice
3) User can choose if they want their exam schedule Spread out or Close Together.
4) the user is asked if  they prefer not to have two exams on same day.

### Note: 
* the last two only apply if the user has chosen electives.

## TL;DR Discord Bot
1) Build a Telegram or Discord Bot which Summarizes the conversation upto the last message of the user.

2) Send the summarization result to the user's DM.

3) It should not have to parse the entire conversation again to find the user's last message (i.e it should have immediate lookups)

4) if there are replies within the summary region to messages outside the summary region, the older messages must be included in the summary to preserve context.

5) No Online APIs can be used, as this violates the user's privacy.

Bonus Tasks:
	a) include media files if possible.
	b) caching of messages using a ctx and tolerance parameter provided by user.

### Features
1) summary till the users's last message by using
   ```
   !sum
   ```
   and a range summary using
   ```
   !sum <from> <to>
   ```
   where \<from> and \<to> are 1 based indexes counted backwards from the the command message.
   if the region includes replies to messages outside the region, then all messages until the older
   messages form the messages to be summarized.

   ### Note: the index skips over messages which were excluded for processing (the bot's messages itself, deleted replies, bots own commands etc).

3) the summarization results are sent to the user's dm,
	if there are any errors regarding invoking the bot etc.
	it is sent to the channel.

4) all messages are summarized using the huggingface 
summarizer pipeline using the model at Azma-AI/bart-conversation-summarizer
ran using pytorch build with cuda enabled.
	


