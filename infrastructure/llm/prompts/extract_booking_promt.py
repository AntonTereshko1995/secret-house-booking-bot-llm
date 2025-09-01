SYSTEM_TMPL = """Ты извлекаешь параметры бронирования из русского текста.
Текущая дата: {TODAY} (текущий год: {YEAR}).
Форматы:
- Дата: ДД.ММ.ГГГГ (если год не указан — подставь {YEAR})
- Время: HH:MM (24 часа, ведущие нули обязательны)
- TARIFF: только  `12 часов`, `Суточно для пар`, `Суточно от 3-ех человек`, `Инконито 12 часов`, `Инкогнито на сутки`, `Рабочий`
- Да/нет → true/false
Если чего-то нет — верни null. Верни только JSON по схеме.
"""

from langchain.prompts import ChatPromptTemplate


def make_prompt(format_instructions: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [("system", SYSTEM_TMPL + "\n{format_instructions}"), ("user", "{text}")]
    ).partial(format_instructions=format_instructions)
