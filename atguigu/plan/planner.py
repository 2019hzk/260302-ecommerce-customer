import json
from dataclasses import asdict
from typing import Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.prompt.loader import load_prompt_template
from atguigu.infrastructure.llm import llm_client
from atguigu.history.builder import ChatHistoryBuilder
from atguigu.task.flows.flows import FlowsList
from atguigu.plan.turn_plan import TurnPlan


class TurnPlanner:
    async def predict(self,
                      state: DialogueState,
                      flows_list: FlowsList,
                      knowledge_intents: dict[str, KnowledgeIntent]
                      ) -> TurnPlan:
        """
        职责：调用LLM做路由分析，判断当前任务该用哪一条轨道处理
        Args:
            state:  用户对话的完整状态

        Returns:
            TurnPlan:轮次结果的结构化对象
        """

        # 1. 准备提示词模版中的变量值
        prompt_inputs: dict[str, Any] = self._build_prompt_inputs(state, flows_list)

        # 2. 格式化模板以及调用LLM
        llm_result = await self._invoke(prompt_inputs)

        return llm_result

    def _build_prompt_inputs(self,
                             state: DialogueState,
                             flows_list: FlowsList,
                             knowledge_intents: dict[str, KnowledgeIntent]
                             ) -> dict[str, Any]:
        # 1. 会话相关
        user_message_str = ChatHistoryBuilder.build_user_message(state.pending_turn.user_message)
        current_conversation_str = ChatHistoryBuilder.build(state.current_session().turns[-10:])

        # 2. 任务相关
        active_task_json_str = json.dumps(state.activated_task.to_dict(),
                                          ensure_ascii=False) if state.activated_task is not None else "null"
        interrupted_tasks_json_str = json.dumps([paused_task.to_dict() for paused_task in state.paused_tasks],
                                                ensure_ascii=False)

        # 3. 卡片相关
        focused_object_json_str = json.dumps(state.focused_object.to_dict(),
                                             ensure_ascii=False) if state.focused_object is not None else "null"

        # 4. 清单相关
        available_flows_json_str = json.dumps({
            "flows": [
                {
                    k: v for k, v in asdict(flow_obj).items() if k != "steps"
                } for flow_obj in flows_list.flows if not flow_obj.flow_id.startswith("system_")
            ]
        }, ensure_ascii=False)
        knowledge_intents_json_str = json.dumps([
            {"id": intent.id, "description": intent.description} for intent in knowledge_intents.values()
        ], ensure_ascii=False)

        return {
            "user_message": user_message_str,
            "current_conversation": current_conversation_str,
            "active_task_json": active_task_json_str,
            "interrupted_tasks_json": interrupted_tasks_json_str,
            "focused_object_json": focused_object_json_str,
            "available_flows_json": available_flows_json_str,
            "knowledge_intents_json": knowledge_intents_json_str,
        }

    async def _invoke(self, prompt_inputs: dict[str, Any]) -> TurnPlan:
        # 1. 获取提示词模版中的内容
        prompt_template_str = load_prompt_template("turn_plan")

        # 2. 格式化提示词模版中的变量
        prompt_template = PromptTemplate.from_template(template=prompt_template_str, template_format="jinja2")

        # 3. LCEL方式通过链来定义
        # (json格式的字典对象)
        chain = prompt_template | llm_client | JsonOutputParser()

        # 4. 执行链   # 1.会依次执行三次invoke. prompt_template.invoke("")--->最终提示词 |   llm_client.invoke(最终提示词)--->json格式字符串  | JsonOutputParser().invoke(son格式字符串)----字典对象
        llm_result_dict = await chain.ainvoke(prompt_inputs)

        # 5. 返回
        return TurnPlan.from_dict(llm_result_dict)


if __name__ == '__main__':
    # dict_data = {"name": "zs", "address": "深圳市宝安区"}
    #
    # print(json.dumps(dict_data, indent=2, ensure_ascii=False))

    list_data = [{"name": "zs", "address": "深圳市宝安区"}, {"name": "ls", "address": "北京市昌平区"}]

    print(json.dumps(list_data, ensure_ascii=False, indent=2))
