import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import folium
from streamlit_folium import st_folium
import numpy as np
import os 
from dotenv import load_dotenv

# ─────────────────────────────────────────
# 0. CONFIG DE LA PAGE
# ─────────────────────────────────────────
st.set_page_config(
    page_title = "Végétation Dakar",
    page_icon  = "🌍",
    layout     = "wide"
)

# ─────────────────────────────────────────
# STYLE CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f9f9f9; }
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .titre-section {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2d6a4f;
        border-left: 4px solid #52b788;
        padding-left: 10px;
        margin: 20px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 1. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────
load_dotenv()
csv_path = os.getenv("CSV_PATH")
@st.cache_data
def load_data():
    return pd.read_csv(csv_path)

df = load_data()

VERT_DENSE  = "#1a9850"
VERT_MOD    = "#91cf60"
VERT_FAIBLE = "#d9ef8b"
ROUGE       = "#d73027"

# ─────────────────────────────────────────
# 2. EN-TÊTE
# ─────────────────────────────────────────
st.title("🌍 Évolution de la couverture végétale à Dakar")
st.markdown("**Analyse par télédétection satellitaire · Sentinel-2 (ESA) · Indices NDVI · 2019–2024**")
st.divider()

# ─────────────────────────────────────────
# 3. SIDEBAR — Filtres
# ─────────────────────────────────────────
with st.sidebar:
    st.image("C:/Users/sowmo/Desktop/cours_licence/codePY/vegetation-dakar/outputs/flag.webp", width=100)
    st.title("⚙️ Paramètres")

    annees_dispo = df["Année"].tolist()
    annee_debut, annee_fin = st.select_slider(
        "Période d'analyse",
        options=annees_dispo,
        value=(annees_dispo[0], annees_dispo[-1])
    )

    niveau = st.radio(
        "Niveau de végétation affiché",
        ["Dense (NDVI > 0.3)", "Modérée (NDVI > 0.2)", "Faible (NDVI > 0.1)"],
        index=0
    )

    st.divider()
    st.markdown("**🛰️ Source des données**")
    st.markdown("- Sentinel-2 SR Harmonized")
    st.markdown("- Google Earth Engine")
    st.markdown("- Résolution : 10m/pixel")
    st.markdown("- Saison : Nov–Déc (sèche)")

# Filtrer le DataFrame selon la période choisie
df_filtre = df[(df["Année"] >= annee_debut) & (df["Année"] <= annee_fin)]

# Colonne à afficher selon le niveau choisi
col_map = {
    "Dense (NDVI > 0.3)"   : "Végétation dense (ha)",
    "Modérée (NDVI > 0.2)" : "Végétation modérée (ha)",
    "Faible (NDVI > 0.1)"  : "Végétation faible (ha)",
}
col_active = col_map[niveau]

# ─────────────────────────────────────────
# 4. MÉTRIQUES CLÉS
# ─────────────────────────────────────────
st.markdown('<div class="titre-section">📊 Indicateurs clés</div>',
            unsafe_allow_html=True)

val_debut = df_filtre[col_active].iloc[0]
val_fin   = df_filtre[col_active].iloc[-1]
perte_ha  = val_debut - val_fin
perte_pc  = round((perte_ha / val_debut) * 100, 1) if val_debut > 0 else 0
taux_annuel = round(perte_pc / max(len(df_filtre) - 1, 1), 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"🌿 Surface {annee_debut}", f"{val_debut:,.0f} ha")
c2.metric(f"🌿 Surface {annee_fin}",   f"{val_fin:,.0f} ha",
          delta=f"-{perte_ha:,.0f} ha", delta_color="inverse")
c3.metric("📉 Perte totale",  f"{perte_pc}%",
          delta=f"-{perte_pc}%", delta_color="inverse")
c4.metric("📅 Perte/an",      f"~{taux_annuel}%/an",
          delta=f"-{taux_annuel}%", delta_color="inverse")

st.divider()

# ─────────────────────────────────────────
# 5. GRAPHIQUES CÔTE À CÔTE
# ─────────────────────────────────────────
st.markdown('<div class="titre-section">📈 Évolution temporelle</div>',
            unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)

# Graphique 1 : Courbe d'évolution
with col_g1:
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#f9f9f9")
    ax.set_facecolor("#f9f9f9")

    ax.fill_between(df_filtre["Année"], df_filtre[col_active],
                    alpha=0.3, color=VERT_DENSE)
    ax.plot(df_filtre["Année"], df_filtre[col_active],
            "o-", color=VERT_DENSE, linewidth=2.5, markersize=8)

    for x, y in zip(df_filtre["Année"], df_filtre[col_active]):
        ax.annotate(f"{y:,.0f}", (x, y),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=8, color=VERT_DENSE, fontweight="bold")

    ax.set_title(f"Surface végétale — {niveau}", fontweight="bold", fontsize=11)
    ax.set_ylabel("Hectares")
    ax.set_xticks(df_filtre["Année"])
    ax.grid(True, alpha=0.3, axis="y")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

# Graphique 2 : Perte cumulée
with col_g2:
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#f9f9f9")
    ax.set_facecolor("#f9f9f9")

    pertes = [val_debut - v for v in df_filtre[col_active]]
    couleurs = [ROUGE if p > 0 else VERT_DENSE for p in pertes]

    barres = ax.bar(df_filtre["Année"], pertes,
                    color=couleurs, width=0.5, edgecolor="white")

    for barre, val in zip(barres, pertes):
        if val > 0:
            ax.text(barre.get_x() + barre.get_width()/2,
                    barre.get_height() + 5,
                    f"{val:,.0f} ha", ha="center",
                    fontsize=8, color=ROUGE, fontweight="bold")

    ax.set_title("Perte cumulée depuis le début de période",
                 fontweight="bold", fontsize=11)
    ax.set_ylabel("Hectares perdus")
    ax.set_xticks(df_filtre["Année"])
    ax.grid(True, alpha=0.3, axis="y")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# ─────────────────────────────────────────
# 6. COMPARAISON 3 NIVEAUX
# ─────────────────────────────────────────
st.markdown('<div class="titre-section">🌿 Comparaison des 3 niveaux de végétation</div>',
            unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(11, 4))
fig.patch.set_facecolor("#f9f9f9")
ax.set_facecolor("#f9f9f9")

for col, couleur, label in [
    ("Végétation faible (ha)",   VERT_FAIBLE, "Faible  (NDVI > 0.1)"),
    ("Végétation modérée (ha)",  VERT_MOD,    "Modérée (NDVI > 0.2)"),
    ("Végétation dense (ha)",    VERT_DENSE,  "Dense   (NDVI > 0.3)"),
]:
    ax.plot(df_filtre["Année"], df_filtre[col],
            "o-", color=couleur, linewidth=2, markersize=7, label=label)
    ax.fill_between(df_filtre["Année"], df_filtre[col], alpha=0.15, color=couleur)

ax.set_ylabel("Hectares")
ax.set_xticks(df_filtre["Année"])
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3, axis="y")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
st.pyplot(fig)

st.divider()

# ─────────────────────────────────────────
# 7. CARTE INTERACTIVE FOLIUM
# ─────────────────────────────────────────
st.markdown('<div class="titre-section">🗺️ Zone d\'analyse — Dakar</div>',
            unsafe_allow_html=True)

m = folium.Map(location=[14.73, -17.35], zoom_start=11,
               tiles="CartoDB positron")

# Contour de la zone d'analyse
folium.Rectangle(
    bounds=[[14.6, -17.6], [15.0, -17.1]],
    color="#1a9850", weight=2,
    fill=True, fill_color="#1a9850", fill_opacity=0.08,
    tooltip="Zone d'analyse : Dakar & périphérie"
).add_to(m)

# Points d'intérêt
pois = [
    (14.6937, -17.4441, "🏙️ Centre-ville Dakar",    "Zone très urbanisée"),
    (14.7470, -17.4678, "🌳 Parc de Hann",           "Espace vert majeur"),
    (14.8156, -17.3403, "🏖️ Lac Rose",               "Zone périphérique"),
    (14.6722, -17.4391, "🏛️ Plateau",                "Quartier historique"),
    (14.7645, -17.3669, "🏘️ Pikine",                 "Expansion urbaine rapide"),
]

for lat, lon, nom, desc in pois:
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(f"<b>{nom}</b><br>{desc}", max_width=200),
        tooltip=nom,
        icon=folium.Icon(color="green", icon="leaf", prefix="fa")
    ).add_to(m)

st_folium(m, width=1100, height=420)

st.divider()

# ─────────────────────────────────────────
# 8. TABLEAU DE DONNÉES
# ─────────────────────────────────────────
st.markdown('<div class="titre-section">📋 Données brutes</div>',
            unsafe_allow_html=True)

with st.expander("Voir le tableau complet"):
    st.dataframe(
        df_filtre.style.background_gradient(
            subset=["Végétation dense (ha)"],
            cmap="Greens"
        ).format("{:,.1f}", subset=df.select_dtypes("float").columns),
        use_container_width=True
    )
    st.download_button(
        label     = "💾 Télécharger CSV",
        data      = df_filtre.to_csv(index=False),
        file_name = "vegetation_dakar.csv",
        mime      = "text/csv"
    )

# ─────────────────────────────────────────
# 9. FOOTER
# ─────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#888; font-size:0.85rem'>
    🌍 Maïmouna SOW · Projet Data Science · Télédétection · Dakar, Sénégal<br>
    Données : Sentinel-2 SR · Google Earth Engine · Python
</div>
""", unsafe_allow_html=True)