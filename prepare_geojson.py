import requests
import json
import os

os.makedirs("assets", exist_ok=True)

url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json"
print("Baixando GeoJSON dos municipios brasileiros (~22MB)...")
r = requests.get(url, timeout=180)
r.raise_for_status()
data = r.json()

n_features = len(data["features"])
print(f"Features: {n_features}")

# Ajustar: garantir que properties.codarea existe com o codigo IBGE (7 digitos como string)
for f in data["features"]:
    props = f.get("properties", {})
    cod = props.get("id") or f.get("id")
    if cod:
        f["properties"]["codarea"] = str(cod)

output_path = "assets/municipios_br.geojson"
with open(output_path, "w", encoding="utf-8") as fp:
    json.dump(data, fp, ensure_ascii=False)

size_mb = os.path.getsize(output_path) / 1e6
print(f"Salvo em: {output_path} ({size_mb:.1f} MB)")

sample = data["features"][0]["properties"]
print("Exemplo de feature:", {k: sample[k] for k in list(sample.keys())[:4]})
