"""Render public GitHub data locally; requires authenticated gh, no extra packages."""
import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER = "Toji-ue"


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True, encoding="utf-8"))


def paged(path, maximum=100):
    result = []
    for page in range(1, maximum + 1):
        rows = api(f"{path}?per_page=100&page={page}")
        result.extend(rows)
        if len(rows) < 100:
            break
    return result


def text(x, y, value, size=16, color="#fbf2ed"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(str(value))}</text>'


def svg(width, height, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title>'
            f'<rect width="{width}" height="{height}" rx="12" fill="#24181e"/>'
            f'<g font-family="DejaVu Sans,Arial,sans-serif">{body}</g></svg>')


def main():
    user = api(f"users/{USER}")
    repos = [r for r in paged(f"users/{USER}/repos") if not r["private"] and r["owner"]["login"].lower() == USER.lower()]
    languages = Counter()
    for repo in repos:
        if not repo["fork"]:
            languages.update(api(f'repos/{USER}/{repo["name"]}/languages'))
    events = paged(f"users/{USER}/events/public", maximum=3)
    now = datetime.now(timezone.utc)
    dates = [(now - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(30, -1, -1)]
    counts = Counter(event["created_at"][:10] for event in events)
    stamp = now.strftime("%Y-%m-%d UTC")
    body = text(24, 34, "PUBLIC GITHUB", 17, "#d7b5c5")
    for index, (label, value) in enumerate([
        ("Repositories", len(repos)), ("Stars received", sum(r["stargazers_count"] for r in repos)),
        ("Followers", user["followers"]), ("Following", user["following"]),
    ]):
        y = 67 + index * 27
        body += text(24, y, label, 15, "#c9b9c2") + text(330, y, value, 18)
    body += text(24, 206, f"Updated {stamp}", 11, "#bfa5b4")
    cards = {"stats.svg": svg(440, 224, "Public GitHub statistics", body)}
    body = text(24, 34, "LANGUAGES", 17, "#d7b5c5")
    total = sum(languages.values())
    palette = ["#c9c7e2", "#d19767", "#a08594", "#f2b493", "#8598c1"]
    top = languages.most_common(4)
    if len(languages) > 4:
        top.append(("Other", total - sum(n for _, n in top)))
    for index, (name, amount) in enumerate(top):
        y = 64 + index * 27
        color = palette[index]
        body += f'<circle cx="29" cy="{y - 5}" r="4" fill="{color}"/>'
        body += text(43, y, name, 14) + text(330, y, f"{amount / total:.1%}", 14, color)
    if not total:
        body += text(24, 80, "No public language data yet.", 14)
    body += text(24, 206, "By bytes · public non-fork repos", 11, "#bfa5b4")
    cards["languages.svg"] = svg(440, 224, "Public repository language distribution", body)
    body = text(24, 34, "RECENT PUBLIC ACTIVITY", 17, "#d7b5c5")
    peak = max(1, *(counts[d] for d in dates))
    body += text(24, 59, f"Last 31 days · up to 300 recent public events · peak {peak}/day", 12, "#bfa5b4")
    for index, day in enumerate(dates):
        x = 28 + index * 27
        h = 105 * counts[day] / peak
        body += f'<rect x="{x}" y="{184-h}" width="16" height="{max(2,h)}" rx="3" fill="{"#c9c7e2" if counts[day] else "#614653"}"><title>{day}: {counts[day]} events</title></rect>'
    body += text(24, 210, dates[0], 11, "#bfa5b4") + text(776, 210, dates[-1], 11, "#bfa5b4")
    body += text(24, 238, "Public events are not a commit count. Private activity is excluded.", 12, "#bfa5b4")
    cards["activity.svg"] = svg(900, 258, "Recent public events by day", body)
    for filename, content in cards.items():
        (ROOT / "assets" / filename).write_text(content, encoding="utf-8")
    print(f"Rendered {len(cards)} cards from public GitHub data ({stamp}).")


if __name__ == "__main__":
    main()
