"""
流程步骤的边

1. 顺序边 --  next: str
2. 条件边 --  if "表达式"   then str
3. 兜底边  -- else    str
"""

from  dataclasses  import  dataclass


@dataclass(slots=True)
class   FlowStepLink:
    """
    抽象基类(边)
    """
    target: str   # 下一个节点的ID


@dataclass(slots=True)
class FlowStepStaticLink(FlowStepLink):
    pass



@dataclass(slots=True)
class FlowStepConditionLink(FlowStepLink):

    condition: str    # 条件是在运行时候 自己去利用python中自带的eval函数来计算。 ("context.get('reason') == 'clarification_rejected'")



@dataclass(slots=True)
class FlowStepFallbackLink(FlowStepLink):
    pass



