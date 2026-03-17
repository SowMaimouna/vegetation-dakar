import ee
import geemap
import pandas as pd
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────
# 0. INITIALISATION
# ─────────────────────────────────────────
load_dotenv()
ee.Initialize(project=os.getenv("GEE_PROJECT"))
print("✅ GEE initialisé")

# ─────────────────────────────────────────
# 1. ZONE D'INTÉRÊT
# ─────────────────────────────────────────
dakar = ee.Geometry.Rectangle([-17.6, 14.6, -17.1, 15.0])

# ─────────────────────────────────────────
# 2. FONCTION NDVI (identique au script 04)
# ─────────────────────────────────────────
def get_ndvi(year):
    image = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
             .filterBounds(dakar)
             .filterDate(f"{year}-11-01", f"{year}-12-31")
             .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
             .median()
             .clip(dakar))
    return image.normalizedDifference(["B8", "B4"]).rename("NDVI")

# ─────────────────────────────────────────
# 3. FONCTION : CALCULER LA SURFACE (en ha)
# ─────────────────────────────────────────
def surface_vegetation_ha(ndvi_image, seuil=0.2):
    """
    Calcule la surface en hectares où NDVI > seuil.
    seuil=0.2 → on considère comme végétation tout ce qui
    dépasse cette valeur (arbres, jardins, herbe dense).
    """
    masque   = ndvi_image.gt(seuil)
    surface  = masque.multiply(ee.Image.pixelArea())  # surface en m²

    stats = surface.reduceRegion(
        reducer    = ee.Reducer.sum(),
        geometry   = dakar,
        scale      = 10,          # résolution Sentinel-2 = 10m
        maxPixels  = 1e10
    )

    m2 = stats.getInfo().get("NDVI", 0)
    ha = m2 / 10_000
    return round(ha, 1)

# ─────────────────────────────────────────
# 4. ANALYSE SUR PLUSIEURS ANNÉES
# ─────────────────────────────────────────
# Sentinel-2 disponible depuis 2019 → on couvre 2019 à 2024
annees = [2019, 2020, 2021, 2022, 2023, 2024]
resultats = []

for annee in annees:
    print(f"⏳ Calcul {annee}...")
    ndvi  = get_ndvi(annee)

    surf_haute   = surface_vegetation_ha(ndvi, seuil=0.3)   # végétation dense
    surf_moyenne = surface_vegetation_ha(ndvi, seuil=0.2)   # végétation modérée
    surf_faible  = surface_vegetation_ha(ndvi, seuil=0.1)   # végétation faible

    resultats.append({
        "Année"                   : annee,
        "Végétation dense (ha)"   : surf_haute,
        "Végétation modérée (ha)" : surf_moyenne,
        "Végétation faible (ha)"  : surf_faible,
    })
    print(f"   ✅ Dense: {surf_haute} ha | Modérée: {surf_moyenne} ha | Faible: {surf_faible} ha")

# ─────────────────────────────────────────
# 5. CRÉER UN DATAFRAME PANDAS
# ─────────────────────────────────────────
df = pd.DataFrame(resultats)

# Calcul de la perte cumulée par rapport à 2019
ref_dense   = df.loc[df["Année"] == 2019, "Végétation dense (ha)"].values[0]
ref_moderee = df.loc[df["Année"] == 2019, "Végétation modérée (ha)"].values[0]

df["Perte dense (ha)"]    = ref_dense   - df["Végétation dense (ha)"]
df["Perte modérée (ha)"]  = ref_moderee - df["Végétation modérée (ha)"]
df["Perte dense (%)"]     = ((df["Perte dense (ha)"]   / ref_dense)   * 100).round(1)
df["Perte modérée (%)"]   = ((df["Perte modérée (ha)"] / ref_moderee) * 100).round(1)

# ─────────────────────────────────────────
# 6. AFFICHER LE TABLEAU
# ─────────────────────────────────────────
print("\n" + "="*65)
print("📊 TABLEAU D'ANALYSE — COUVERTURE VÉGÉTALE DAKAR")
print("="*65)
print(df.to_string(index=False))
print("="*65)

# Résumé
perte_totale_ha = df.loc[df["Année"] == 2024, "Perte dense (ha)"].values[0]
perte_totale_pc = df.loc[df["Année"] == 2024, "Perte dense (%)"].values[0]
print(f"\n🔴 Perte totale de végétation dense (2019→2024) :")
print(f"   {perte_totale_ha} hectares perdus soit -{perte_totale_pc}%")
print(f"   ≈ {round(perte_totale_ha / 90, 1)} fois la superficie du Parc de Hann\n")

# ─────────────────────────────────────────
# 7. EXPORTER EN CSV
# ─────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
chemin_csv = "outputs/analyse_surface_dakar.csv"
df.to_csv(chemin_csv, index=False)
print(f"💾 Données exportées → {chemin_csv}")
print("🎉 Analyse terminée ! Lance maintenant 06_graphiques.py")