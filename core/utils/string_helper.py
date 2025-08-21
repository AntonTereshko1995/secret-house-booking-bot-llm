def parse_yes_no(s: str) -> bool | None:
    t = s.lower().strip()
    if t in {"да", "ага", "ok", "ок", "yes", "y", "true", "1"}:
        return True
    if t in {"нет", "не", "no", "n", "false", "0"}:
        return False
    return None
