import importlib
import inspect
import pkgutil

from atguigu.task.action.base import Action
from atguigu.task.action.builtin.listener import ActionListener
from atguigu.task.action.builtin.response import ActionResponse
from atguigu.task.action.register import ActionRegister
from atguigu.task.action.runner import ActionRunner


def _register_builtin_actions(action_runner: ActionRunner):
    action_register = action_runner.action_register

    action_register.register_action(ActionResponse())
    action_register.register_action(ActionListener())


def _register_customer_actions(action_runner: ActionRunner):
    package = importlib.import_module("atguigu.task.action.customer")

    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        if is_pkg:
            continue

        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):  # _类的字符串名字
            if not issubclass(obj, Action) or obj is Action:
                continue
            action_runner.action_register.register_action(obj())


def build_action_runner() -> ActionRunner:
    action_runner = ActionRunner(ActionRegister())

    _register_builtin_actions(action_runner)

    _register_customer_actions(action_runner)
    return action_runner


if __name__ == '__main__':
    action_runner = build_action_runner()
    print(action_runner)
