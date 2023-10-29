# Summary Bot
## Usage
**Conversation Summarization**:
the summary of the conversation till the user's last message.
```
!sum
```
**Range Summarization**:
summarize a range of messages between two indices specified by `<from>` and `<to>`
```
!sum <from> <to>
```
Note: This skips over messages which are excluded from processing i.e (the bot's own messages, replies to deleted, messages, etc)

## Installation and Running
clone the repo and inside the folder with pyproject.toml file
```
poetry install
```

**Note:**
the model was run using CUDA framework for Graphics Acceleration

CUDA (12.1): https://developer.nvidia.com/cuda-12-1-0-download-archive

with the  addtional libraries:

CuDDN (v8.9.5): https://developer.nvidia.com/rdp/cudnn-download
NCCL (2.19.3): https://developer.nvidia.com/nccl/nccl-download

place the bot token in the .env file in the same folder as pyproject.toml
```
DISCORD_TOKEN=<value>
```
run the bot with (python version 3.11.5)
```
poetry run python src/main.py
```
