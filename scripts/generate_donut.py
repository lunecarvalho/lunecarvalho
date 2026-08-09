import os
import requests
import matplotlib.pyplot as plt

USERNAME = "lunecarvalho"
TOP_N = 8
OUT_FILE = "assets/languages-bar.svg"

PURPLE = "#4A148C"
YELLOW = "#FFD600"
PALETTE = [PURPLE, "#6A1B9A", "#7B1FA2", "#8E24AA", "#9C27B0", "#AB47BC", YELLOW, "#5E35B1"]

def github_get(url, token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json(), r.links

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
            for lang, n in langs.items():
                totals[lang] = totals.get(lang, 0) + n
        except Exception:
            pass
    return totals

def build_bar_chart(totals):
    os.makedirs("assets", exist_ok=True)

    if not totals:
        labels = ["No data"]
        values = [1]
    else:
        ordered = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
        labels = [k for k, _ in ordered][::-1]
        values = [v for _, v in ordered][::-1]

    total = sum(values) if sum(values) > 0 else 1
    perc = [(v / total) * 100 for v in values]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    bars = ax.barh(labels, perc, color=colors, edgecolor="none", linewidth=0)

    ax.set_title("Most used languages", color=PURPLE, fontsize=14, weight="bold", pad=12)
    ax.set_xlabel("Percentage (%)", color=PURPLE)
    ax.tick_params(axis="x", colors=PURPLE)
    ax.tick_params(axis="y", colors=PURPLE)

    for bar, p in zip(bars, perc):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{p:.1f}%",
            va="center",
            fontsize=9,
            color=PURPLE,
            weight="bold"
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(PURPLE)
    ax.spines["bottom"].set_color(PURPLE)
    ax.grid(axis="x", linestyle="--", alpha=0.25)

    plt.tight_layout()
    plt.savefig(OUT_FILE, format="svg", transparent=True, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    token = os.getenv("GH_TOKEN")
    repos = fetch_repos(USERNAME, token)
    totals = aggregate_languages(repos, token)
    build_bar_chart(totals)
