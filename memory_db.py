"""
memory_db.py - Module untuk penyimpanan data dalam memory

Module ini menyediakan alternatif sederhana dari database MongoDB
dengan menyimpan data dalam memory selama runtime.
"""

class MemoryDB:
    def __init__(self):
        self.user_data = {}
        self.guild_data = {}
        self.command_logs = []
        self.guild_settings = {}
        print("[INFO] MemoryDB initialized")
    
    def connect(self):
        """Mengembalikan True karena tidak perlu koneksi sebenarnya"""
        return True
    
    def get_user_data(self, user_id):
        """Mendapatkan data pengguna dari memory"""
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {"user_id": user_id}
        return self.user_data[user_id]
    
    def set_user_data(self, user_id, data):
        """Menyimpan data pengguna ke memory"""
        user_id = str(user_id)
        self.user_data[user_id] = data
        return True
    
    def get_guild_data(self, guild_id):
        """Mendapatkan data guild dari memory"""
        guild_id = str(guild_id)
        if guild_id not in self.guild_data:
            self.guild_data[guild_id] = {"guild_id": guild_id}
        return self.guild_data[guild_id]
    
    def set_guild_data(self, guild_id, data):
        """Menyimpan data guild ke memory"""
        guild_id = str(guild_id)
        self.guild_data[guild_id] = data
        return True
    
    def update_user_data(self, user_id, data):
        """Update sebagian data pengguna"""
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {"user_id": user_id}
        self.user_data[user_id].update(data)
        return True
    
    def log_command(self, user_id, guild_id, command_name):
        """Log penggunaan command"""
        from datetime import datetime
        
        log_entry = {
            'user_id': user_id,
            'guild_id': guild_id,
            'command': command_name,
            'timestamp': datetime.now()
        }
        self.command_logs.append(log_entry)
        
        # Update user data
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'commands_used': 0,
                'last_command': None,
                'last_command_time': None
            }
        
        self.user_data[user_id]['commands_used'] = self.user_data[user_id].get('commands_used', 0) + 1
        self.user_data[user_id]['last_command'] = command_name
        self.user_data[user_id]['last_command_time'] = datetime.now()
        
        return True
    
    def get_command_stats(self):
        """Mendapatkan statistik penggunaan command"""
        stats = {}
        for log in self.command_logs:
            command = log['command']
            if command not in stats:
                stats[command] = 0
            stats[command] += 1
        return stats
    
    def get_guild_language(self, guild_id):
        """Mendapatkan setting bahasa guild"""
        if guild_id is None:
            return "id"  # Default language for DMs
        
        guild_id = str(guild_id)
        if guild_id in self.guild_settings and 'language' in self.guild_settings[guild_id]:
            return self.guild_settings[guild_id]['language']
        return "id"  # Default language
    
    def set_guild_language(self, guild_id, language):
        """Menyimpan setting bahasa guild"""
        guild_id = str(guild_id)
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = {}
        self.guild_settings[guild_id]['language'] = language
        return True
    
    def get_guild_prefix(self, guild_id):
        """Mendapatkan prefix command guild"""
        if guild_id is None:
            return "!"  # Default prefix for DMs
        
        guild_id = str(guild_id)
        if guild_id in self.guild_settings and 'prefix' in self.guild_settings[guild_id]:
            return self.guild_settings[guild_id]['prefix']
        return "!"  # Default prefix
    
    def set_guild_prefix(self, guild_id, prefix):
        """Menyimpan prefix command guild"""
        guild_id = str(guild_id)
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = {}
        self.guild_settings[guild_id]['prefix'] = prefix
        return True

# Buat instance untuk digunakan dalam program
db = MemoryDB() 