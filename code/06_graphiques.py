import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────
# 0. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────
load_dotenv()
csv_path = os.getenv("CSV_PATH")
df = pd.read_csv(csv_path)
annees = df["Année"].tolist()

dense   = df["Végétation dense (ha)"].tolist()
moderee = df["Végétation modérée (ha)"].tolist()
faible  = df["Végétation faible (ha)"].tolist()

perte_ha = df["Perte dense (ha)"].tolist()
perte_pc = df["Perte dense (%)"].tolist()

os.makedirs("outputs/graphiques", exist_ok=True)
print("✅ Données chargées")

# ─────────────────────────────────────────
# STYLE GLOBAL
# ─────────────────────────────────────────
plt.rcParams.update({
    "font.family"  : "DejaVu Sans",
    "font.size"    : 11,
    "axes.spines.top"   : False,
    "axes.spines.right" : False,
    "figure.facecolor"  : "#f9f9f9",
    "axes.facecolor"    : "#f9f9f9",
})

VERT_DENSE   = "#1a9850"
VERT_MOD     = "#91cf60"
VERT_FAIBLE  = "#d9ef8b"
ROUGE        = "#d73027"
ORANGE       = "#fc8d59"

# ═════════════════════════════════════════
# GRAPHIQUE 1 — Évolution des 3 niveaux
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 5))

ax.fill_between(annees, faible,  alpha=0.25, color=VERT_FAIBLE)
ax.fill_between(annees, moderee, alpha=0.35, color=VERT_MOD)
ax.fill_between(annees, dense,   alpha=0.6,  color=VERT_DENSE)

ax.plot(annees, faible,  "o--", color=VERT_FAIBLE, linewidth=1.5, markersize=6)
ax.plot(annees, moderee, "o--", color=VERT_MOD,    linewidth=1.5, markersize=6)
ax.plot(annees, dense,   "o-",  color=VERT_DENSE,  linewidth=2.5, markersize=8)

# Annotations sur la courbe dense
for x, y in zip(annees, dense):
    ax.annotate(f"{y} ha", (x, y),
                textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=9, color=VERT_DENSE, fontweight="bold")

ax.set_title("Évolution de la couverture végétale à Dakar (2019–2024)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Année", fontsize=11)
ax.set_ylabel("Surface (hectares)", fontsize=11)
ax.set_xticks(annees)
ax.grid(True, alpha=0.3, axis="y")

legende = [
    mpatches.Patch(color=VERT_DENSE,  label="Végétation dense  (NDVI > 0.3)"),
    mpatches.Patch(color=VERT_MOD,    label="Végétation modérée (NDVI > 0.2)"),
    mpatches.Patch(color=VERT_FAIBLE, label="Végétation faible  (NDVI > 0.1)"),
]
ax.legend(handles=legende, loc="upper right", framealpha=0.7)

plt.tight_layout()
plt.savefig("outputs/graphiques/01_evolution_vegetation.png", dpi=150)
plt.show()
print("✅ Graphique 1 sauvegardé")

# ═════════════════════════════════════════
# GRAPHIQUE 2 — Perte cumulée en barres
# ═════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

couleurs = [VERT_DENSE if p <= 0 else ROUGE for p in perte_ha]
barres   = ax.bar(annees, perte_ha, color=couleurs, width=0.5, edgecolor="white")

# Étiquettes sur les barres
for barre, val, pct in zip(barres, perte_ha, perte_pc):
    if val > 0:
        ax.text(barre.get_x() + barre.get_width()/2,
                barre.get_height() + 15,
                f"-{pct}%", ha="center", fontsize=10,
                color=ROUGE, fontweight="bold")

ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
ax.set_title("Perte cumulée de végétation dense depuis 2019",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Année")
ax.set_ylabel("Hectares perdus")
ax.set_xticks(annees)
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("outputs/graphiques/02_perte_cumulee.png", dpi=150)
plt.show()
print("✅ Graphique 2 sauvegardé")

# ═════════════════════════════════════════
# GRAPHIQUE 3 — Camembert 2019 vs 2024
# ═════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

def parts(dense_v, moderee_v, faible_v, total):
    """Calcule les parts en s'assurant qu'elles sont toutes positives"""
    veg   = max(dense_v, 0)
    inter = max(moderee_v - dense_v, 0)
    low   = max(faible_v  - moderee_v, 0)
    nonv  = max(total     - faible_v, 0)

    # Si tout est à 0, éviter une erreur matplotlib
    parts_list = [veg, inter, low, nonv]
    if sum(parts_list) == 0:
        parts_list = [1, 1, 1, 1]
    return parts_list

labels  = ["Dense", "Modérée", "Faible", "Non-végétalisé"]
colors  = [VERT_DENSE, VERT_MOD, VERT_FAIBLE, "#cccccc"]
explode = (0.05, 0, 0, 0)

surf_totale = max(faible[0], faible[-1])  # référence = le plus grand des deux

for ax, idx, titre in [(ax1, 0, "2019"), (ax2, -1, "2024")]:
    data = parts(dense[idx], moderee[idx], faible[idx], surf_totale)
    print(f"  📊 Parts {titre} : {data}")  # debug : voir les valeurs
    ax.pie(data, labels=labels, colors=colors, explode=explode,
           autopct="%1.1f%%", startangle=140,
           wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax.set_title(f"Répartition végétale — {titre}",
                 fontsize=13, fontweight="bold")

plt.suptitle("Comparaison de la couverture végétale à Dakar",
             fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("outputs/graphiques/03_camembert_comparaison.png",
            dpi=150, bbox_inches="tight")
plt.show()
print("✅ Graphique 3 sauvegardé")

# ═════════════════════════════════════════
# GRAPHIQUE 4 — Dashboard résumé (4 panels)
# ═════════════════════════════════════════
fig = plt.figure(figsize=(14, 8))
fig.suptitle("🌍 Couverture végétale à Dakar — Synthèse 2019–2024",
             fontsize=15, fontweight="bold", y=1.01)

# Panel 1 : courbe principale
ax1 = fig.add_subplot(2, 2, 1)
ax1.fill_between(annees, dense, alpha=0.4, color=VERT_DENSE)
ax1.plot(annees, dense, "o-", color=VERT_DENSE, linewidth=2)
ax1.set_title("Végétation dense (ha)", fontweight="bold")
ax1.set_xticks(annees)
ax1.grid(True, alpha=0.3, axis="y")

# Panel 2 : % de perte
ax2 = fig.add_subplot(2, 2, 2)
ax2.plot(annees, perte_pc, "s-", color=ROUGE, linewidth=2, markersize=8)
ax2.fill_between(annees, perte_pc, alpha=0.2, color=ROUGE)
ax2.set_title("Perte cumulée (%)", fontweight="bold")
ax2.set_xticks(annees)
ax2.grid(True, alpha=0.3, axis="y")

# Panel 3 : barres empilées
ax3 = fig.add_subplot(2, 2, 3)
b1 = np.array(dense)
b2 = np.array(moderee) - b1
b3 = np.array(faible)  - np.array(moderee)
ax3.bar(annees, b1, color=VERT_DENSE,  label="Dense",   width=0.5)
ax3.bar(annees, b2, bottom=b1,         color=VERT_MOD,  label="Modérée", width=0.5)
ax3.bar(annees, b3, bottom=b1+b2,      color=VERT_FAIBLE, label="Faible", width=0.5)
ax3.set_title("Surface par niveau (ha)", fontweight="bold")
ax3.legend(fontsize=8)
ax3.set_xticks(annees)
ax3.grid(True, alpha=0.3, axis="y")

# Panel 4 : métriques texte
ax4 = fig.add_subplot(2, 2, 4)
ax4.axis("off")

perte_finale_ha = perte_ha[-1]
perte_finale_pc = perte_pc[-1]
annee_debut     = annees[0]
annee_fin       = annees[-1]

texte = (
    f"📍 Zone analysée : Dakar & périphérie\n\n"
    f"📅 Période : {annee_debut} → {annee_fin}\n\n"
    f"🛰️  Source : Sentinel-2 (ESA, 10m)\n\n"
    f"🌿 Végétation 2019 : {dense[0]:,} ha\n\n"
    f"🌿 Végétation 2024 : {dense[-1]:,} ha\n\n"
    f"📉 Perte totale    : {perte_finale_ha:,} ha\n\n"
    f"📉 Soit            : -{perte_finale_pc}%\n\n"
    f"⚙️  Seuil NDVI     : > 0.3 (dense)"
)
ax4.text(0.05, 0.95, texte, transform=ax4.transAxes,
         fontsize=11, verticalalignment="top",
         bbox=dict(boxstyle="round", facecolor="#e8f5e9", alpha=0.8))

plt.tight_layout()
plt.savefig("outputs/graphiques/04_dashboard_resume.png",
            dpi=150, bbox_inches="tight")
plt.show()
print("✅ Graphique 4 sauvegardé")

# ─────────────────────────────────────────
# RÉCAP FINAL
# ─────────────────────────────────────────
print("\n" + "="*50)
print("🎉 Tous les graphiques sont générés !")
print("="*50)
print("📁 outputs/graphiques/")
print("   ├── 01_evolution_vegetation.png")
print("   ├── 02_perte_cumulee.png")
print("   ├── 03_camembert_comparaison.png")
print("   └── 04_dashboard_resume.png")
