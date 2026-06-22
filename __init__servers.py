"""HTTP endpoints, grouped by resource.

Each file here is an APIRouter that main.py mounts onto the app. Splitting by
resource (backups, restores, config, health) keeps each file small and makes it
obvious where a given endpoint lives.
"""
