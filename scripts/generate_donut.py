import os
import requests
import matplotlib.pyplot as plt

USERNAME = "lunecarvalho"
TOP_N = 6
OUT_FILE = "assets/donut.svg"

# Cores já usadas no README
PURPLE = "#4A148C"
YELLOW = "#FFD600"
WHITE = "#FFFFFF"
PALETTE = [PURPLE, YELLOW, "#6A1B9A", "#7B1FA2", "#8E24AA", "#9C27B0", "#AB47BC"]

def github_get(url, token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json(), resp.links

def fetch_repos(username, token=None):
    repos = []
    url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner&sort=updated"
    while url:
        data, links = github_get(url, token)
        repos.extend(data)
        url = links.get("next", {}).get("url")
    return repos

def aggregate_languages(repos, token=None):
    totals = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        lang_url = repo.get("languages_url")
        if not lang_url:
            continue
        try:
            langs, _ = github_get(lang_url, token)
            for lang, byte_count in langs.items():
                totals[lang] = totals.get(lang, 0) + byte_count
        except Exception:
            pass
    return totals

def build_donut(totals):
    if not totals:
        labels, sizes = ["No data"], [1]
    else:
        ordered = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        top = ordered[:TOP_N]
        rest = ordered[TOP_N:]
        if rest:
            top.append(("Others", sum(v for _, v in rest)))
        labels = [k for k, _ in top]
        sizes = [v for _, v in top]

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=180)
    ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor=WHITE, linewidth=2),
        textprops=dict(color=WHITE, fontsize=9, weight="bold"),
    )
    ax.text(0, 0, "Lune\nLanguages", ha="center", va="center", color=PURPLE, fontsize=12, weight="bold")
    ax.set(aspect="equal")
    plt.tight_layout()

    os.makedirs("assets", exist_ok=True)
    plt.savefig(OUT_FILE, format="svg", transparent=True)
    plt.close()

if __name__ == "__main__":
    token = os.getenv("GH_TOKEN")
    repos = fetch_repos(USERNAME, token=token)
    totals = aggregate_languages(repos, token=token)
    build_donut(totals)
