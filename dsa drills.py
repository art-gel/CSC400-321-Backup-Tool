# sets/lists
def chunk_image(data:set, size:int):
    return [data[i:i+size] for i in range(0, len(data), size)]

#string
def is_valid_key(key):
    if not key or len(key) > 200:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_./")
    return all (c in allowed for c in key) and not key.startswith("/")

#hashmaps
def count_chunks_uses(hashes:list[str]) -> dict[str,int]:
    count = {}
    for i in hashes:
        count[i] = count.get(i,0)+1
    return count
    
    
    
# sets
old = {"f1", "f2", "f3"}
new = {"f2", "f3", "f4"}
new - old # -> {"f4"} (added)
old & new # -> {"f2","f3"} (unchanged)
#removed = f1 | shared = f2,f3,| added = f4
def diff_backups(old:list[str], new:list[str]) -> dict[str,set]:
   old = {"f1", "f2", "f3"} 
   new = {"f2", "f3", "f4"}
   return {f"removed: {old - new}" , f"added: {new - old}", f"unchanged: {old & new}"}
   
   


