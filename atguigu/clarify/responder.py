import json
from typing import Any

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.plan.turn_plan import TurnPlanValidatedResult, ClarifyReason
from atguigu.prompt.loader import load_prompt_template
from atguigu.infrastructure.llm import llm_client
from atguigu.history.builder import  ChatHistoryBuilder

from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ClarifyResponder:
    async def respond(self,
                      reason: ClarifyReason,
                      state: DialogueState) -> list[BotMessage]:
        """
        根据校验结果对象的原因码，利用LLM 来润色澄清回复
        Args:
            validated:
            state:

        Returns: list[BotMessage]

        """

        # 1. 构建澄清话术需要的提示词模版变量值
        prompt_inputs = self._build_responder_prompt_inputs(reason, state)

        # 2. 格式化模版，调用LLM
        bot_messages = await self._invoke(prompt_inputs)

        # 3. 返回
        return bot_messages

    def _build_responder_prompt_inputs(self,
                                       reason: ClarifyReason,
                                       state: DialogueState) -> dict[str, Any]:
        user_message_str = ChatHistoryBuilder.build_user_message(state.pending_turn.user_message)
        history_str = ChatHistoryBuilder.build(state.current_session().turns[-10:])
        focused_object_str = json.dumps(state.focused_object.to_dict(),
                                        ensure_ascii=False) if state.focused_object is not None else "null"
        reason_str = reason.value
        clarify_message_str =self._build_base_response(reason,state)

        return {
            "user_message": user_message_str,
            "history": history_str,
            "focused_object": focused_object_str,
            "clarify_message": clarify_message_str,
            "reason": reason_str,
        }

    async def _invoke(self, prompt_inputs: dict[str, Any]) -> list[BotMessage]:
        # 1. 加载提示词模版
        prompt_template_str = load_prompt_template("clarify_respond")

        # 2. 实例化提示词模版对象
        prompt_template = PromptTemplate.from_template(template=prompt_template_str, template_format="jinja2")

        # 3. 构建chain
        chain = prompt_template | llm_client | StrOutputParser()

        # 4. 执行链
        result = await  chain.ainvoke(prompt_inputs)

        # 5. 返回结果
        return [BotMessage(text=result)]



    def _build_base_response(self,
                             reason:ClarifyReason,
                             state:DialogueState)->str:

        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先发送你想咨询的对象，我再继续帮你看。"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解商品信息、订单信息，还是售后配送规则呢？"

        if reason is ClarifyReason.MISSING_TRACK:
            return "你是想先处理业务问题，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查订单、查物流，或者申请退款。"

        if reason is ClarifyReason.OBJECT_REQUIRES_INTENT:
            focused_object = state.focused_object
            if focused_object is not None and focused_object.type == "order":
                return "我已经收到这个订单了。你想查订单状态、查物流，还是申请退款呢？"
            if focused_object is not None and focused_object.type == "product":
                return "我已经收到这个商品了。你想了解它的商品信息、发货情况，还是售后相关问题呢？"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"

