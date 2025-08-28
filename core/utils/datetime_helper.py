import re
from datetime import datetime

def is_time(s: str) -> bool:
    s = s.strip()
    if re.fullmatch(r'([01]?\d|2[0-3])', s):  # hour only: "12", "9", "23"
        return True
    if re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d', s):  # hour:minutes: "12:00", "09:30"
        return True
    return False

def norm_time(s: str) -> str:
    s = s.strip()
    if ':' in s:
        return s  # already in correct format
    # If only hour, add ":00"
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

def extract_date_from_natural_language(text: str) -> str | None:
    """
    Extract date from natural language text in Russian.
    Returns date in DD.MM.YYYY format or None if not found.
    """
    # Russian month names
    months = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    
    low = text.lower()
    for month_name, month_num in months.items():
        if month_name in low:
            # Look for day number before month name
            day_match = re.search(r'(\d{1,2})\s*' + month_name, low)
            if day_match:
                day = int(day_match.group(1))
                year = datetime.now().year
                try:
                    date_str = f"{day:02d}.{month_num:02d}.{year}"
                    # Validate the date
                    datetime.strptime(date_str, "%d.%m.%Y")
                    return date_str
                except ValueError:
                    continue
    
    return None
