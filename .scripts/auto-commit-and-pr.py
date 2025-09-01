import subprocess as sp
import sys, os, json, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Install pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(sp.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip())
RULES_PATH = ROOT / ".claude" / "commit_rules.yml"

def sh(cmd, check=True, capture=False):
    if capture:
        return sp.check_output(cmd, text=True).strip()
    r = sp.run(cmd, check=check)
    return r.returncode

def git_changed_files():
    out = sh(["git", "status", "--porcelain"], capture=True)
    files = []
    for line in out.splitlines():
        status, path = line[:2], line[3:]
        if "->" in path:  # rename
            path = path.split("->", 1)[1].strip()
        path = path.strip('"')
        if not path or path == ".": 
            continue
        # игнор удалённых
        if status.strip().startswith("D"):
            continue
        files.append(path)
    return list(dict.fromkeys(files))

def match_group(path: str, rules: dict):
    from fnmatch import fnmatch
    for group in rules.get("groups", []):
        for pat in group.get("patterns", []):
            if fnmatch(path, pat):
                return group
    return rules.get("default", {"name": "misc", "type": "chore"})

def ensure_branch(base="main"):
    cur = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
    if cur == "HEAD":
        branch = f"auto/{sh(['date', '+%Y%m%d-%H%M%S'], capture=True)}"
        sh(["git", "fetch", "origin", base], check=False)
        sh(["git", "switch", "-c", branch, f"origin/{base}"], check=False)
        return branch
    return cur

def main():
    if not RULES_PATH.exists():
        print(f"Rules file not found: {RULES_PATH}", file=sys.stderr)
        sys.exit(2)
    rules = yaml.safe_load(RULES_PATH.read_text())

    changed = git_changed_files()
    if not changed:
        print("Нет изменений для коммита.")
        return

    branch = ensure_branch(os.getenv("BASE_BRANCH", "main"))

    buckets = {}  # {group_name: {"type":..., "files":[...]}}
    for f in changed:
        group = match_group(f, rules)
        name = group.get("name", "misc")
        typ = group.get("type", "chore")
        buckets.setdefault(name, {"type": typ, "files": []})
        buckets[name]["files"].append(f)

    order = [g["name"] for g in rules.get("groups", [])]
    ordered_names = [n for n in order if n in buckets] + [n for n in buckets if n not in order]

    for name in ordered_names:
        info = buckets[name]
        files = info["files"]
        ctype = info["type"]
        # формируем summary
        fmt = rules.get("commit_format", "{type}: {summary}")
        default_summary = rules.get("default_summary", "update {group}")
        summary = default_summary.format(group=name)
        msg = fmt.format(type=ctype, summary=summary)

        # stage только эти файлы
        sh(["git", "add"] + files)
        # если нечего коммитить (например, уже были в индексе) — пропускаем
        diff_cached = sh(["git", "diff", "--cached", "--name-only"], capture=True)
        if not diff_cached.strip():
            continue

        sh(["git", "commit", "-m", msg])
        print(f"✔ Commit: {msg} — {len(files)} file(s)")

    cur = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
    sh(["git", "push", "-u", "origin", cur])

    log = sh(["git", "log", "--pretty=%s", "-n", "2"], capture=True).splitlines()
    pr_title = log[0] if log else "chore: changes"
    pr_body = "\n".join("- " + l for l in sh(["git", "log", "--pretty=%s", "origin/"+os.getenv("BASE_BRANCH","main")+"..HEAD"], capture=True).splitlines())

    try:
        sh(["gh", "pr", "create", "--title", pr_title, "--body", pr_body, "--base", os.getenv("BASE_BRANCH","main"), "--head", cur], check=True)
        print("✅ PR создан")
    except sp.CalledProcessError:
        # возможно, PR уже есть — просто откроем в браузере
        print("ℹ️  Возможно, PR уже существует. Открою страницу…")
    try:
        sh(["gh", "pr", "view", "--web"], check=False)
    except Exception:
        pass

if __name__ == "__main__":
    main()
