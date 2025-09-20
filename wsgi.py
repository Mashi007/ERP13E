cd /c/Users/PORTATIL/Documents/GitHub/ERP7-Documentos/ERP13E

# Corregir la línea con error de sintaxis
sed -i 's/if \*\*name\*\* ==/if __name__ ==/' wsgi.py

# Verificar que se corrigió
tail -3 wsgi.py

# Verificar sintaxis Python
python -m py_compile wsgi.py
