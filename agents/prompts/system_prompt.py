from pathlib import Path


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent / "system_prompt.md"
    return prompt_path.read_text(encoding="utf-8")