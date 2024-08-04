import neocities
import configparser
import os
from alive_progress import alive_bar

version = '1.0'


def create_default_config():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'version': version,
        'id': "your-neocities-id",
        'password': "your-neocities-key",
        'include_files': "html,css,js,png,jpg,jpeg,gif,webp",
    }
    try:
        with open('config.ini', 'w', encoding='utf8') as configfile:
            config.write(configfile)
        return True
    except Exception as e:
        print('Error creating configuration file:', e)
        print('Try running the program as an administrator.')
        return False
    
def get_files(path="./", include_files=["html", "css", "js", "png", "jpg", "jpeg", "gif", "webp"]):
    result = []
    for file in os.listdir(path):
        file = path + file
        
        # Check if file is a directory
        if os.path.isdir(file):
            # Get files in directory
            result += get_files(file + "/")
        
        else:
            
            # Check if file is in include_files
            if not any(file_name in file for file_name in include_files): continue
            
            result.append(file.replace("./", ""))
    
    return result
    
if __name__ == '__main__':
    # Load the configuration file
    if not os.path.exists('config.ini'):
        print('No configuration file found. Creating one...')
        if not create_default_config(): exit(1)
    
    # Load the configuration
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf8')
    
    while True:
        # Ask account
        id = input(f"Enter your Neocities ID({config['DEFAULT']['id']}): ")
        if id == '':
            id = config['DEFAULT']['id']
        else:
            config['DEFAULT']['id'] = id
            
        password = input(f"Enter your Neocities password({config['DEFAULT']['password']}): ")
        if password == '':
            password = config['DEFAULT']['password']
        else:
            config['DEFAULT']['password'] = password
    
        # Login
        try:
            nc = neocities.NeoCities(id, password)
            break
        except Exception as e:
            print("Error:", e)
            print('Login failed. Please retry \n\n', )
    
    # Save the configuration
    with open('config.ini', 'w', encoding='utf8') as configfile:
        config.write(configfile)

    # Get files in current directory
    files = get_files()
    uploaded_files = nc.listitems()['files']
    
    
    existing_files = {"path": [file['path'] for file in uploaded_files if not file['is_directory']],
                  "size": [file['size'] for file in uploaded_files if not file['is_directory']],}
    
    total_file_len = len(files)

    # Filter out files that are already uploaded and are the same size
    files = [file for file in files if (not (file in existing_files["path"])) or (os.path.getsize(file) != existing_files["size"][existing_files["path"].index(file)])]

    should_updated = [file for file in files if (file in existing_files["path"]) and (os.path.getsize(file) != existing_files["size"][existing_files["path"].index(file)])]
    files.extend(should_updated)

    print(f"Files to upload: {len(files)}/{total_file_len} ({total_file_len - len(existing_files['path'])} new, {len(should_updated)} need update)")
    if(input("Do you want to continue? (y/n): ") != 'y'):
        input('Press enter to exit...')
        exit(0)
    
    with alive_bar(len(files), title='Uploading...', bar='classic') as bar:
        for file in files:
            nc.upload((file, file))
            
            # Update progress bar
            bar()

    # Print success message
    print("Upload complete!")
    input('Press enter to exit...')