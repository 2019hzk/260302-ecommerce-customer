from typing import Any

import yaml

from pathlib import Path

from atguigu.task.flows.flows import FlowsList, FlowSlot, Flow
from atguigu.task.flows.steps import FlowStep, CollectFlowStep


class FlowLoader:
    """
    流程加载器
    职责：利用pyyaml包 将yaml文件解析成字对象并且在用解析后的字典实例化对应的数据模型 最后返回FlowList
    """

    def load_multi_yaml(self, paths: list[Path]) -> FlowsList:
        final_flows: list[Flow] = []
        final_slots: dict[str, FlowSlot] = {}
        for path in paths:
            flow_list = self._load_yaml(path)
            final_flows.extend(flow_list.flows)
            final_slots.update(flow_list.slots)
        return FlowsList(final_flows, final_slots)

    def _load_yaml(self, path: Path) -> FlowsList:
        """
        记载单个yaml文件
        Args:
            path:  yaml文件path

        Returns:
            FlowsList对象

        """

        # 1. 调用safe_load方法将yaml文件解析成字典结构
        with  open(path, 'r', encoding='utf-8') as f:
            yaml_dict: dict[str, Any] = yaml.safe_load(f.read())

        # 2. 加载slots
        loaded_slots = self._load_slots(yaml_dict.get('slots', {}))

        # 3. 加载flows
        loaded_flows = self._load_flows(yaml_dict['flows'], loaded_slots)

        # 4. 构建FlowsList

        return FlowsList(slots=loaded_slots, flows=loaded_flows)

    def _load_slots(self, slots: dict[str, Any]) -> dict[str, FlowSlot]:
        loaded_slots: dict[str, FlowSlot] = {}
        for slot_name, slot_dict in slots.items():
            loaded_slots[slot_name] = FlowSlot(
                slot_name=slot_name,
                type=slot_dict['type'],
                label=slot_dict['label'],
                description=slot_dict['description']
            )
        return loaded_slots

    def _load_flows(self, flows: dict[str, Any], loaded_slots: dict[str, FlowSlot]) -> list[Flow]:

        loaded_flows: list[Flow] = []
        for flow_id, flow_dict in flows.items():
            steps = [FlowStep.from_dict(step_dict) for step_dict in flow_dict['steps']]
            flow = Flow(
                flow_id=flow_id,
                flow_name=flow_dict['name'],
                description=flow_dict['description'],
                steps=steps,
                slots=self._build_flow_slots(steps, loaded_slots)
            )
            loaded_flows.append(flow)

        return loaded_flows

    def _build_flow_slots(self, steps: list[FlowStep], loaded_slots: dict[str, FlowSlot]) -> dict[str, FlowSlot]:
        """
        职责：获取到当前业务流程中要收集的槽位（1 or n）
        Args:
            steps:
            loaded_slots:

        Returns:


        """

        flow_slots: dict[str, FlowSlot] = {}

        for step in steps:
            # 1. 判断步骤类型
            if not isinstance(step, CollectFlowStep):
                continue

            # 2. 步骤类型是CollectFlowStep(需要收集槽位)
            slot_name = step.slot_name

            slot_definition = loaded_slots.get(slot_name)

            if slot_definition is not None:
                flow_slots[slot_name] = slot_definition

        return flow_slots


if __name__ == '__main__':
    flow_loader = FlowLoader()
    user_flows_path = Path("user_flows.yml")
    sys_flows_path = Path("system_flows.yml")
    final_flow_list = flow_loader.load_multi_yaml([user_flows_path,sys_flows_path])
    print(final_flow_list)
