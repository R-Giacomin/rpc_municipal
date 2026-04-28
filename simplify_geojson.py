"""Simplifica agressivamente o GeoJSON para ficar < 2MB."""
import json, os

input_path = os.path.join("assets", "municipios_br.geojson")
output_path = os.path.join("assets", "municipios_br_simpl.geojson")

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Original: {len(data['features'])} features")

def simplify_ring(coords, tolerance=0.08):
    if len(coords) <= 4:
        return coords
    result = [coords[0]]
    for pt in coords[1:]:
        dx = pt[0] - result[-1][0]
        dy = pt[1] - result[-1][1]
        if dx*dx + dy*dy > tolerance*tolerance:
            result.append(pt)
    if result[-1] != coords[-1]:
        result.append(coords[-1])
    return result

def process_geom(geom):
    if geom['type'] == 'Polygon':
        geom['coordinates'] = [simplify_ring(r) for r in geom['coordinates']]
    elif geom['type'] == 'MultiPolygon':
        new_polys = []
        for poly in geom['coordinates']:
            new_poly = [simplify_ring(r) for r in poly]
            if len(new_poly[0]) >= 4:
                new_polys.append(new_poly)
        if new_polys:
            geom['coordinates'] = new_polys
    # Arredondar para 2 casas decimais
    def rnd(c):
        if isinstance(c[0], (int, float)):
            return [round(x, 2) for x in c]
        return [rnd(x) for x in c]
    geom['coordinates'] = rnd(geom['coordinates'])
    return geom

for feat in data['features']:
    feat['geometry'] = process_geom(feat['geometry'])
    cod = feat['properties'].get('codarea') or feat['properties'].get('id', '')
    feat['properties'] = {'codarea': str(cod)}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

size_mb = os.path.getsize(output_path) / 1e6
print(f"Resultado: {size_mb:.1f} MB")
