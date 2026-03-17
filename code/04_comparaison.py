import ee
import geemap
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────
# 0. INITIALISATION
# ─────────────────────────────────────────
load_dotenv()
ee.Initialize(project=os.getenv("GEE_PROJECT"))
print("✅ GEE initialisé")

# ─────────────────────────────────────────
# 1. ZONE D'INTÉRÊT : DAKAR
# ─────────────────────────────────────────
dakar = ee.Geometry.Rectangle([-17.6, 14.6, -17.1, 15.0])

# ─────────────────────────────────────────
# 2. FONCTION : CHARGER UNE IMAGE + NDVI
# ─────────────────────────────────────────
def get_ndvi(year):
    """
    Charge une image Sentinel-2 en saison sèche
    et retourne le NDVI calculé pour cette année.
    """
    image = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
             .filterBounds(dakar)
             .filterDate(f"{year}-11-01", f"{year}-12-31")
             .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
             .median()
             .clip(dakar))

    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return ndvi

# ─────────────────────────────────────────
# 3. CALCUL NDVI POUR 2019 ET 2024
# ─────────────────────────────────────────
print("⏳ Chargement NDVI 2019...")
ndvi_2019 = get_ndvi(2019)

print("⏳ Chargement NDVI 2024...")
ndvi_2024 = get_ndvi(2024)

# ─────────────────────────────────────────
# 4. CALCUL DE LA DIFFÉRENCE
# ─────────────────────────────────────────
# Valeur positive = gain de végétation
# Valeur négative = perte de végétation
difference = ndvi_2024.subtract(ndvi_2019).rename("Difference")

# Isoler uniquement les zones de perte significative (baisse > 0.1)
zones_perte = difference.lt(-0.1)
zones_gain  = difference.gt(0.1)

print("✅ Différence calculée")

# ─────────────────────────────────────────
# 5. STATS : NDVI MOYEN PAR ANNÉE
# ─────────────────────────────────────────
def get_stats(ndvi_image, label):
    stats = ndvi_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=dakar,
        scale=100,
        maxPixels=1e9
    )
    valeur = stats.getInfo().get("NDVI", None)
    print(f"📊 NDVI moyen {label} : {valeur:.4f}")
    return valeur

ndvi_moy_2019 = get_stats(ndvi_2019, "2019")
ndvi_moy_2024 = get_stats(ndvi_2024, "2024")

evolution = ((ndvi_moy_2024 - ndvi_moy_2019) / ndvi_moy_2019) * 100
print(f"📉 Évolution : {evolution:.2f}%")

# ─────────────────────────────────────────
# 6. CARTE INTERACTIVE AVEC 4 COUCHES
# ─────────────────────────────────────────
print("🗺️  Génération de la carte...")

carte = geemap.Map(center=[14.73, -17.35], zoom=11)

# Couche 1 : NDVI 2019
palette_ndvi = {
    "min": -0.1, "max": 0.6,
    "palette": ["#d73027","#fc8d59","#fee08b","#d9ef8b","#91cf60","#1a9850"]
}
carte.addLayer(ndvi_2019, palette_ndvi, "NDVI 2019")

# Couche 2 : NDVI 2024
carte.addLayer(ndvi_2024, palette_ndvi, "NDVI 2024")

# Couche 3 : Différence (rouge = perte, vert = gain)
palette_diff = {
    "min": -0.4, "max": 0.4,
    "palette": ["#d7191c","#fdae61","#ffffbf","#a6d96a","#1a9641"]
}
carte.addLayer(difference, palette_diff, "Changement 2019→2024")

# Couche 4 : Zones de perte uniquement (en rouge vif)
carte.addLayer(
    zones_perte.selfMask(),
    {"palette": ["#ff0000"]},
    "⚠️ Zones de perte végétale"
)

carte.addLayerControl()  # cases à cocher pour activer/désactiver les couches

# ─────────────────────────────────────────
# 7. EXPORT HTML
# ─────────────────────────────────────────
import os
os.makedirs("outputs/cartes", exist_ok=True)

carte.save("outputs/cartes/carte_comparaison_2019_2024.html")
print("✅ Carte sauvegardée → outputs/cartes/carte_comparaison_2019_2024.html")
print("Script terminé ! Ouvre la carte dans ton navigateur.")