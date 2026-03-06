import ee
import geemap
import os
from dotenv import load_dotenv

load_dotenv()
ee.Authenticate()
ee.Initialize(project=os.getenv("GEE_PROJECT"))

# 1. Définir la zone : Dakar
dakar = ee.Geometry.Rectangle([-17.6, 14.6, -17.1, 15.0])

# 2. Charger une image Sentinel-2 (saison sèche 2024, peu de nuages)
image = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
         .filterBounds(dakar)
         .filterDate("2024-11-01", "2024-12-31")
         .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
         .median()
         .clip(dakar))

# 3. Calculer le NDVI
ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

# 4. Afficher les stats pour vérifier que ça marche
stats = ndvi.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=dakar,
    scale=100
)

print("📊 NDVI moyen sur Dakar :", stats.getInfo())
print("✅ Image chargée et NDVI calculé !")