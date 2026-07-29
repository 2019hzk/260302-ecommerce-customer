from dataclasses import dataclass
from typing import Any
from jinja2 import Template

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from atguigu.history.builder import ChatHistoryBuilder
from atguigu.infrastructure.llm import llm_client
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class ActionResponse(Action):
    name = "action_response"

    async def run(self,
                  action_kwargs: dict[str, Any],
                  state: DialogueState
                  ) -> ActionResult:
        """
        职责：负责将YAML中的响应内容，获取到返回
        响应内容：有占位。双花括号：交给jinja2模版引擎（渲染）
        Args:
            action_kwargs:

        Returns:

        """

        # 1. 获取响应的内容
        action_response_mode = action_kwargs.get('mode', 'static')

        # 2. 判断模式
        if action_response_mode == "rephrase":
            # a) 获取要响应的内容
            response_text = action_kwargs['text']

            # b) 渲染获取的响应内容
            rendered_text = self._render(response_text, state)

            # c) 获取提示词
            prompt = action_kwargs['prompt']

            # d) 调用llm
            rewritten = await self._call_llm(state, prompt, rendered_text)

            return ActionResult(messages=[BotMessage(text=rewritten)])
        elif action_response_mode == "generate":
            # a) 获取提示词
            prompt = action_kwargs['prompt']

            # b) 调用llm
            rewritten = await self._call_llm(state, prompt)

            return ActionResult(messages=[BotMessage(text=rewritten)])

        else:
            # "static"
            # a) 获取响应的内容
            response_text = action_kwargs['text']

            # b) 渲染获取的响应内容
            rendered_text = self._render(response_text, state)

            # c) 直接返回
            return ActionResult(messages=[BotMessage(text=rendered_text)])

    def _render(self, response_text: str, state: DialogueState) -> str:
        template = Template(response_text)

        render_str = template.render(slots=state.activated_task.slots, context=state.activated_system_task)

        return render_str

    async def _call_llm(self,
                        state: DialogueState,
                        prompt: str,
                        rendered_text: str = "") -> str:

        # 1. 实例化提示词模版对象
        prompt_template = PromptTemplate.from_template(template=prompt)

        # 2. 构建chain
        chain = prompt_template | llm_client | StrOutputParser()

        # 3. 调用chain
        rewritten = await chain.ainvoke({
            "history": ChatHistoryBuilder.build(state.current_session().turns[-5:]),
            "user_message": ChatHistoryBuilder.build_user_message(state.pending_turn.user_message),
            "current_response": rendered_text
        })

        # 4. 返回
        return rewritten
