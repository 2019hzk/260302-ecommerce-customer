"""
加载:由jinja2模版引擎管理的提示词模版
"""
from pathlib import Path


def load_prompt_template(prompt_template_suffix: str) -> str:
    prompt_template_ = Path(__file__).resolve().parents[0] / "jinja2" / f"{prompt_template_suffix}.jinja2"

    return prompt_template_.read_text(encoding="utf-8")
