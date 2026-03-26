class FileDao:
    def __init__(self, supabase):
        self.supabase = supabase
    
    async def get_files(self, file_paths: list[str]):
        files = []
        for path in file_paths:
            try:
                # The SDK returns 'bytes' directly. 
                # If the file doesn't exist, it usually raises an exception.
                file_content = self.supabase.storage.from_("documents").download(path)
                
                if file_content:
                    files.append(file_content)
                
            except Exception as e:
                # This catches 404s, 403s, or connection issues
                print(f"⚠️ Failed to download {path}: {e}")
                # We continue so one bad file doesn't kill the whole batch
                continue
                
        return files