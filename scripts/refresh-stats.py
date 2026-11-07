"""Fetch privately, publish aggregates only. Standard library + authenticated gh.

No raw API responses, repository identifiers or CLI stderr are logged or saved.
"""
import calendar
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER = 'Toji-ue'


def api(path, query=None):
    args = ['gh', 'api', path]
    if query:
        args += ['-f', 'query=' + query]
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('GitHub request failed; previous cards retained.')
    result = json.loads(result.stdout)
    if isinstance(result, dict) and result.get('errors'):
        raise RuntimeError('GitHub returned incomplete data; previous cards retained.')
    return result


def collect():
    user = api('user')
    if user['login'].lower() != USER.lower():
        raise RuntimeError('The statistics credential belongs to a different account.')
    repos = []
    page = 1
    while True:
        batch = api(f'user/repos?affiliation=owner&visibility=all&per_page=100&page={page}')
        repos.extend(r for r in batch if r['owner']['login'].lower() == USER.lower())
        if len(batch) < 100:
            break
        page += 1
    private_count = sum(r['private'] for r in repos)
    # Reject the common accidental fallback to a public-only or partial credential.
    # All-repository access is required; do not silently call a selected subset "all".
    expected = user.get('owned_private_repos')
    if expected is not None and private_count != expected:
        raise RuntimeError('Private repository coverage is incomplete.')
    minimum = int(os.environ.get('PROFILE_MIN_PRIVATE_REPOS', '18'))
    if private_count < minimum:
        raise RuntimeError('Repository coverage fell below the verified baseline; review credential coverage.')
    repos = [r for r in repos if not r['fork']]
    languages = Counter()
    for repo in repos:
        languages.update(api('repos/' + repo['full_name'] + '/languages'))
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start = now.replace(year=now.year-1, day=min(now.day, calendar.monthrange(now.year-1, now.month)[1]))
    query = '''query { viewer { contributionsCollection(from: "%s", to: "%s") {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount weekday } } }
    } } }''' % (start.isoformat(), now.isoformat())
    cal = api('graphql', query)['data']['viewer']['contributionsCollection']['contributionCalendar']
    days = [dict(date=d['date'], count=d['contributionCount'], weekday=d['weekday'])
            for w in cal['weeks'] for d in w['contributionDays']]
    if sum(d['count'] for d in days) != cal['totalContributions'] or len(days) < 365:
        raise RuntimeError('Calendar validation failed; previous cards retained.')
    verified=os.environ.get('PROFILE_PRIVATE_CALENDAR_VERIFIED') == 'true'
    return dict(updated=now.strftime('%Y-%m-%d UTC'), repositories=len(repos),
                stars=sum(r['stargazers_count'] for r in repos if not r['private']),
                followers=user['followers'], contributions=cal['totalContributions'],
                languages=dict(languages.most_common()), days=days,
                calendar_scope='GitHub contribution calendar; private counts verified' if verified else 'GitHub contribution calendar; private visibility not yet verified',
                private_calendar_verified=verified)


def save_batch(files):
    """Stage every output before replacing, restore previous files on I/O failure."""
    original = {name: (ROOT/name).read_bytes() if (ROOT/name).exists() else None for name in files}
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        for name, value in files.items():
            path = Path(temp)/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding='utf-8')
        try:
            for name in files:
                (ROOT/name).parent.mkdir(parents=True, exist_ok=True)
                os.replace(Path(temp)/name, ROOT/name)
        except OSError:
            for name, value in original.items():
                if value is None:
                    (ROOT/name).unlink(missing_ok=True)
                else:
                    (ROOT/name).write_bytes(value)
            raise


def main():
    from desktop_art import render_cards
    try:
        if os.environ.get('GITHUB_ACTIONS') and not os.environ.get('GH_TOKEN'):
            raise RuntimeError('PROFILE_STATS_TOKEN is required.')
        data = collect()
        files = render_cards(data)
        files['assets/aggregate.json'] = json.dumps(data, indent=2) + '\n'
        save_batch(files)
    except Exception:
        # Do not print exception text, request URLs, raw JSON, or tracebacks.
        print('Refresh failed validation or authentication. Previous assets were retained.', file=sys.stderr)
        return 1
    print('Validated and rendered aggregate profile cards.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
