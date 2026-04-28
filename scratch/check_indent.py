with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[115:130]):
        print(f"{i+116}: {repr(line[:12])}")
