# -*- coding: utf-8 -*-
import sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=== Python Environment Check ===")
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Encoding: {sys.getdefaultencoding()}")
print(f"stdout encoding: {sys.stdout.encoding}")
print()

errors = []
# Core packages
pkgs = {
    'pandas': 'pd', 'numpy': 'np', 'matplotlib': 'matplotlib',
    'openpyxl': 'openpyxl', 'scipy': 'scipy', 'sklearn': 'sklearn',
    'geopandas': 'gpd', 'shapely': 'shapely', 'bs4': 'bs4',
    'lxml': 'lxml', 'pdfplumber': 'pdfplumber', 'docx': 'docx',
    'PIL': 'PIL', 'httpx': 'httpx', 'tabulate': 'tabulate',
}

for pkg, alias in pkgs.items():
    try:
        mod = __import__(pkg)
        ver = getattr(mod, '__version__', 'OK')
        print(f"  [OK] {pkg:20s} {ver}")
    except Exception as e:
        errors.append(pkg)
        print(f"  [FAIL] {pkg:20s} {e}")

print()

# Matplotlib font test
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    
    korean_fonts = [f.name for f in fm.fontManager.ttflist if 'Malgun' in f.name or 'Gothic' in f.name or 'Gulim' in f.name or 'Batang' in f.name]
    korean_fonts = list(set(korean_fonts))
    if korean_fonts:
        print(f"  Korean fonts found: {korean_fonts[:5]}")
    else:
        print("  [WARN] No Korean fonts detected")
    
    # Quick plot test
    fig, ax = plt.subplots()
    ax.plot([1,2,3], [1,4,9])
    plt.close()
    print("  [OK] Matplotlib rendering works")
except Exception as e:
    errors.append('matplotlib-render')
    print(f"  [FAIL] Matplotlib rendering: {e}")

# Pandas read/write test
try:
    import pandas as pd
    df = pd.DataFrame({'A': [1,2,3], 'B': ['x','y','z']})
    df.to_csv('_test_env.csv', index=False, encoding='utf-8-sig')
    df2 = pd.read_csv('_test_env.csv', encoding='utf-8-sig')
    os.remove('_test_env.csv')
    print("  [OK] Pandas CSV read/write works")
except Exception as e:
    errors.append('pandas-io')
    print(f"  [FAIL] Pandas IO: {e}")

print()
if errors:
    print(f"=== ISSUES FOUND: {errors} ===")
else:
    print("=== ALL CHECKS PASSED ===")
