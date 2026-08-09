import matplotlib.pyplot as plt

labels = ["Python", "NLP", "ML", "Web"]
sizes = [40, 25, 20, 15]
colors = ["#4A148C", "#FFD600", "#6A1B9A", "#8E24AA"]

fig, ax = plt.subplots(figsize=(4,4), dpi=160)
ax.pie(
    sizes,
    labels=labels,
    colors=colors,
    startangle=90,
    wedgeprops=dict(width=0.35, edgecolor="#FFFFFF")
)
ax.text(0, 0, "Lune", ha="center", va="center", color="#4A148C", weight="bold")
ax.set(aspect="equal")
plt.tight_layout()
plt.savefig("assets/donut.svg", format="svg", transparent=True)
