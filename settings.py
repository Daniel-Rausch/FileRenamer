from yaml import load, dump, YAMLError

import logging


settings = {}

__defaultSettings = {
    'LoggingLevel': 'INFO',
    'Path' : '', # Folder containing the files to be renamed
    'FileRegex': '', # Regex identifying files to be renamed
    'NewFileFormat': '', # Format for renaming. Supports special string "#(n)", where "n" is a number. This will be replaced with the group n of the regex match, modulo the number of groups. The string "#()" is interpreted as "#"".
    }


#Read the settings.yml file
try:
    with open('settings.yml', 'r') as file:
        settings = load(file)
        if settings is None:
            settings = {}
except YAMLError as e:
    logging.error('Your settings.yml file could not be parsed. Using default config. Try fixing or deleting your settings.yml file to get rid of this error.')
    settings = __defaultSettings
except FileNotFoundError as e:
    with open('settings.yml', 'w') as file:
        file.write(dump(__defaultSettings))
    settings = __defaultSettings
else:
    
    #If some options were not present in the settings.yml file, use the default instead
    for key in __defaultSettings:
        if key not in settings:
            settings[key] = __defaultSettings[key]


#print (settings)
#print (__defaultSettings)


