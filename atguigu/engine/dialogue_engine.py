from atguigu.domain.messages import ProcessResult,BotMessage
from atguigu.domain.state import DialogueState


class DialogueEngine:
    async def process_message(self, dialogue_state:DialogueState) -> ProcessResult:
        """
        TODO(周六写)
        :param dialogue_state:
        :return:
        """

        return ProcessResult(
            message_id="abc123",
            messages=[BotMessage(text="你好，我是atguigu电商客服小助理")]
        )
