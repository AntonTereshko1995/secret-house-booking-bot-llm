"""
Модуль для работы со строками
"""

def parse_yes_no(s: str) -> bool | None:
    """
    Парсит строку и возвращает True/False для ответов да/нет.
    
    Поддерживаемые значения для "да":
    - "да", "ага", "ok", "ок", "yes", "y", "true", "1"
    
    Поддерживаемые значения для "нет":
    - "нет", "не", "no", "n", "false", "0"
    
    Args:
        s: Строка для парсинга
        
    Returns:
        True для положительного ответа, False для отрицательного, None если не распознано
        
    Examples:
        >>> parse_yes_no("да")
        True
        >>> parse_yes_no("нет")
        False
        >>> parse_yes_no("ok")
        True
        >>> parse_yes_no("неизвестно")
        None
    """
    t = s.lower().strip()
    if t in {"да", "ага", "ok", "ок", "yes", "y", "true", "1"}:
        return True
    if t in {"нет", "не", "no", "n", "false", "0"}:
        return False
    return None
