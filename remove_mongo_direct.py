#!/usr/bin/env python
# Script untuk menghapus kode MongoDB dari main.py dan menggantinya dengan fungsi-fungsi kompatibel

try:
    print("Membuka file main.py...")
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pola kode terkait MongoDB yang akan dihapus dan diganti
    mongo_patterns = [
        "from pymongo import",
        "import pymongo",
        "from motor",
        "import motor",
        "MongoClient",
        "AsyncIOMotorClient",
        "mongodb+srv://",
        "db.command_stats", 
        "db.update_", 
        "db.get_user_data",
        "db.set_user_data",
        "db.get_guild_data",
        "db.set_guild_data",
        "database.connect",
        "mongodb://",
        "mongo_db",
        "mongo_client",
        "client.database"
    ]
    
    print("Mencari kode terkait MongoDB...")
    
    # Menghitung referensi MongoDB sebelum dibersihkan
    original_references = 0
    for pattern in mongo_patterns:
        count = content.count(pattern)
        if count > 0:
            original_references += count
            print(f"Ditemukan {count} referensi '{pattern}'")
    
    if original_references == 0:
        print("Tidak ditemukan referensi MongoDB di main.py!")
    else:
        print(f"Ditemukan total {original_references} referensi MongoDB untuk dihapus")
    
    # Fungsi pengganti untuk database
    replacement_code = """
# Fungsi pengganti untuk operasi database yang dihapus
class MemoryDB:
    def __init__(self):
        self.user_data = {}
        self.guild_data = {}
        print("[INFO] MemoryDB initialized")
    
    def connect(self):
        return True
    
    def get_user_data(self, user_id):
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {"user_id": user_id}
        return self.user_data[user_id]
    
    def set_user_data(self, user_id, data):
        user_id = str(user_id)
        self.user_data[user_id] = data
        return True
    
    def get_guild_data(self, guild_id):
        guild_id = str(guild_id)
        if guild_id not in self.guild_data:
            self.guild_data[guild_id] = {"guild_id": guild_id}
        return self.guild_data[guild_id]
    
    def set_guild_data(self, guild_id, data):
        guild_id = str(guild_id)
        self.guild_data[guild_id] = data
        return True
    
    def update_user_data(self, user_id, data):
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {"user_id": user_id}
        self.user_data[user_id].update(data)
        return True

# Mengganti instance database dengan memori
db = MemoryDB()
"""
    
    # Memeriksa apakah kode pengganti sudah ada
    if "class MemoryDB:" not in content:
        # Cari posisi untuk menambahkan kode pengganti (setelah import)
        import_pos = content.find("import")
        import_block_end = import_pos
        while import_block_end < len(content):
            next_line = content.find("\n", import_block_end + 1)
            if next_line == -1:
                break
            line = content[import_block_end:next_line]
            if not any(line.strip().startswith(x) for x in ["import ", "from "]):
                break
            import_block_end = next_line
        
        # Tentukan posisi untuk menambahkan kode pengganti
        insert_pos = import_block_end + 1
        
        # Masukkan kode pengganti setelah blok import
        content = content[:insert_pos] + replacement_code + content[insert_pos:]
    
    # Temukan dan hapus baris-baris terkait MongoDB
    lines = content.split('\n')
    new_lines = []
    skipped_lines = 0
    
    for line in lines:
        # Periksa apakah baris berisi kode terkait MongoDB
        has_mongo = False
        for pattern in mongo_patterns:
            if pattern in line:
                has_mongo = True
                break
        
        # Jika baris berisi kode MongoDB, komentari
        if has_mongo:
            new_lines.append(f"# REMOVED: {line}")
            skipped_lines += 1
        else:
            new_lines.append(line)
    
    # Gabungkan kembali baris-baris
    new_content = '\n'.join(new_lines)
    
    # Cadangkan file asli
    with open('main.py.bak', 'w', encoding='utf-8') as f:
        f.write(content)
    print("File asli dicadangkan sebagai main.py.bak")
    
    # Tulis kembali ke main.py
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Berhasil menghapus {skipped_lines} baris kode MongoDB dari main.py")
    print("File main.py telah diperbarui dengan implementasi memory database")

except Exception as e:
    print(f"Error: {e}") 