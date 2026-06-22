"""The actual backup logic lives here.

Each module is intentionally a thin stub right now. The API layer (routers) does
NOT know how imaging works — it just calls these functions. That separation is
the whole point: Troy can build the real encryption in encryption.py while Angel
wires up the routes, and nothing breaks as long as the function signatures hold.
"""
