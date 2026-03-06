import ee
import os
from dotenv import load_dotenv

load_dotenv()
ee.Authenticate()
ee.Initialize(project=os.getenv("GEE_PROJECT"))

print("✅ Google Earth Engine connecté avec succès !")