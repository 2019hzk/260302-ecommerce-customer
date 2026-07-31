from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from atguigu.history.builder import ChatHistoryBuilder
from atguigu.infrastructure.llm import llm_client
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.prompt.loader import load_prompt_template


class ChitChatResponder:

    async def respond_chat(self,
                           chat: str,
                           state: DialogueState) -> list[BotMessage]:
        # 1. 加载闲聊的提示词内容
        prompt_template_str = load_prompt_template("chitchat_respond")

        # 2. 实例化提示词模版对象
        prompt_template = PromptTemplate.from_template(template=prompt_template_str, template_format="jinja2")

        # 3. 构建链
        chain = prompt_template | llm_client | StrOutputParser()

        # 4. 执行返回
        result = await  chain.ainvoke({
            "user_message": chat,
            "history": ChatHistoryBuilder.build(state.current_session().turns[-10:])
        })

        return [BotMessage(text=result)]
