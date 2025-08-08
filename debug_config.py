from dynaconf import Dynaconf
import os

print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    settings = Dynaconf(
        settings_files=['settings.toml', '.secrets.toml'],
        environments=False,
        load_dotenv=False,
    )
    
    print(f"AWS_REGION: {settings.get('aws_region')}")
    print(f"SECRET_KEY: {settings.get('secret_key')}")
    print(f"DYNAMODB_USERS_TABLE: {settings.get('dynamodb_users_table')}")
    
except Exception as e:
    print(f"Error loading settings: {e}")
    
    if os.path.exists('settings.toml'):
        print("settings.toml exists")
        with open('settings.toml', 'r') as f:
            print("Contents of settings.toml:")
            print(f.read())
    else:
        print("settings.toml does not exist")
        
    if os.path.exists('.secrets.toml'):
        print(".secrets.toml exists")
    else:
        print(".secrets.toml does not exist")