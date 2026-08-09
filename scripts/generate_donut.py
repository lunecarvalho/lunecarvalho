import os
import requests
import matplotlib.pyplot as plt

USERNAME = "lunecarvalho"
TOP_N = 8
OUT_FILE = "assets/languages-bar.svg"

# Paleta
PURPLE_BG = "#4A148C"   # fundo roxo
YELLOW_BAR = "#FFD600"  # barras amarelas
WHITE = "#FFFFFF"

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
                # remove somente Jupyter Notebook
                if lang == "Jupyter Notebook":
                    continue
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

    fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=180)

    fig.patch.set_facecolor(PURPLE_BG)
    ax.set_facecolor(PURPLE_BG)

    bars = ax.barh(labels, perc, color=YELLOW_BAR, edgecolor="none", linewidth=0)

    ax.set_xlabel("Percentage (%)", color=WHITE, fontsize=9)
    ax.tick_params(axis="x", colors=WHITE, labelsize=8)
    ax.tick_params(axis="y", colors=WHITE, labelsize=9)

    for bar, p in zip(bars, perc):
        ax.text(
            bar.get_width() + 0.6,
            bar.get_y() + bar.get_height() / 2,
            f"{p:.1f}%",
            va="center",
            ha="left",
            fontsize=8.5,
            color=WHITE,
            weight="bold"
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(WHITE)
    ax.spines["bottom"].set_color(WHITE)
    ax.grid(axis="x", linestyle="--", alpha=0.25, color=WHITE)

    max_p = max(perc) if perc else 100
    ax.set_xlim(0, max_p + 8)

    plt.tight_layout(pad=1.0)

    plt.savefig(
        OUT_FILE,
        format="svg",
        facecolor=PURPLE_BG,
        edgecolor=PURPLE_BG,
        transparent=False,
        bbox_inches="tight",
        pad_inches=0.15
    )
    plt.close()

if __name__ == "__main__":
    token = os.getenv("GH_TOKEN")
    repos = fetch_repos(USERNAME, token)
    totals = aggregate_languages(repos, token)
    build_bar_chart(totals)
