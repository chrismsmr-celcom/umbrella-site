import os
import shutil
import time

# Dossier où sont créés les dossiers temporaires
TEMP_BASE_DIR = "/tmp" 
# Seuil de rétention (supprime tout ce qui a plus de 30 minutes)
MAX_AGE_SECONDS = 1800 

def clean_old_folders():
    now = time.time()
    print(f"--- Nettoyage lancé à {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    for folder_name in os.listdir(TEMP_BASE_DIR):
        folder_path = os.path.join(TEMP_BASE_DIR, folder_name)
        
        # On ne touche qu'aux dossiers créés par tempfile (souvent préfixés 'tmp')
        if os.path.isdir(folder_path):
            folder_age = now - os.path.getmtime(folder_path)
            
            if folder_age > MAX_AGE_SECONDS:
                try:
                    shutil.rmtree(folder_path)
                    print(f"🗑️ Supprimé : {folder_name} ({int(folder_age/60)} min)")
                except Exception as e:
                    print(f"⚠️ Erreur sur {folder_name} : {e}")

if __name__ == "__main__":
    clean_old_folders()
