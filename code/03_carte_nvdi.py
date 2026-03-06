import ee
import geemap
import os
from dotenv import load_dotenv

load_dotenv()
ee.Authenticate()
ee.Initialize(project=os.getenv("GEE_PROJECT"))

dakar = ee.Geometry.Rectangle([-17.6, 14.6, -17.1, 15.0])

# Charger et calculer NDVI
image = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
         .filterBounds(dakar)
         .filterDate("2024-11-01", "2024-12-31")
         .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
         .median()
         .clip(dakar))

ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

# Créer la carte interactive
carte = geemap.Map(center=[14.73, -17.35], zoom=11)

# Palette : rouge = sol nu → vert = végétation dense
palette_ndvi = {
    "min": -0.1,
    "max": 0.6,
    "palette": ["#d73027", "#fc8d59", "#fee08b", "#d9ef8b", "#91cf60", "#1a9850"]
}

carte.addLayer(ndvi, palette_ndvi, "NDVI Dakar 2024")
carte.addLayerControl()

# Sauvegarder en HTML (s'ouvre dans le navigateur)
carte.save("carte_ndvi_dakar.html")
print("✅ Carte sauvegardée → ouvre carte_ndvi_dakar.html dans ton navigateur !")