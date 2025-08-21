import re
from datetime import datetime

def is_time(s: str) -> bool:
    s = s.strip()
    if re.fullmatch(r'([01]?\d|2[0-3])', s):  # только час: "12", "9", "23"
        return True
    if re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d', s):  # час:минуты: "12:00", "09:30"
        return True
    return False

def norm_time(s: str) -> str:
    s = s.strip()
    if ':' in s:
        return s  # уже в правильном формате
    # Если только час, добавляем ":00"
    hour = int(s)
    return f"{hour:02d}:00"

def is_date(s: str) -> bool:
    s = s.replace("/", ".").replace("-", ".")
    try:
        p = s.split(".")
        if len(p) == 2:
            s += f".{datetime.now().year}"
        datetime.strptime(s, "%d.%m.%Y")
        return True
    except:
        return False

def norm_date(s: str) -> str:
    s = s.replace("/", ".").replace("-", ".")
    if len(s.split(".")) == 2:
        s += f".{datetime.now().year}"
    return datetime.strptime(s, "%d.%m.%Y").strftime("%d.%m.%Y")
