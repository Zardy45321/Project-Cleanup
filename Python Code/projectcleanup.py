## Fraytools Project Cleanup V.1
## Created by: Zardy Z

import os
import json
import sys
import PySimpleGUI as sg
import shutil



def myexcepthook(type,value,traceback,oldhook=sys.excepthook):
    oldhook(type,value,traceback)
    print(oldhook)
    print('oof there was an error!!')
    input("Press Enter to Close...")

sys.excepthook = myexcepthook

'''File Handling Functions'''

'''Read file contents from given path'''
def readFile(path: str):
    with open(path, 'r', encoding='utf8', errors='ignore') as file:
        return file.readlines()

'''Read JSON contents from given path'''
def getJSONData(path: str):
    with open(path,'r') as file:
        return json.load(file)

    
'''Input Validation Functions'''

'''Checks file exists'''
def checkFile(path:str):
    if os.path.isfile(path):
        return True
    else:
        if path == '':
            return False
        else:
            return False

'''Checks folder exists'''
def checkFolder(path:str):
    
    if os.path.exists(path):
        valid = False
        for f in os.listdir(path):
            if f == 'library':
                valid = True

        if valid == False:
            sg.popup('Folder selected is not valid! Missing a library folder!')
            return False
        else:
            return True
    else:
        if path == '':
            sg.popup('Please Provide a Folder Path!')
            return False
        else:
            sg.popup(path+' does not exist! Please choose a valid folder!!')
            return False

'''Checks folder exists'''
def checkFolderNoMessage(path:str):
    if os.path.exists(path):
        valid = False
        for f in os.listdir(path):
            if f == 'library':
                valid = True

        if valid == False:
            return False
        else:
            return True
    else:
        if path == '':
            return False
        else:
            return False

def getSettings():
    return getJSONData(settings_path)


#cwd = os.path.abspath(os.getcwd())
#settings_path = os.path.join(cwd,'Files','System','Settings.json')
#settings = getSettings()

'''Program Functions'''

'''Batch Caller'''
def cleanup_batch_project(project_path:str, advanced_audio:bool):
    subfolders = [ f.path for f in os.scandir(project_path) if f.is_dir() ]
    projects = 0
    cleaned_sprites = 0
    cleaned_audio = 0
    for s in subfolders:
        if checkFolderNoMessage(s) == True:
            cleaned_data = cleanup_project(s, advanced_audio)
            cleaned_sprites += cleaned_data[0]
            cleaned_audio += cleaned_data[1]
            projects += 1

    return projects, cleaned_sprites, cleaned_audio

'''Caller function'''
def cleanup_project(project_path:str, advanced_audio:bool):
    ## Create paths
    short_path = os.path.join(project_path,'library')
    entity_path = os.path.join(short_path,'entities')
    sprite_path = os.path.join(short_path,'sprites')
    scripts_path = os.path.join(short_path,'scripts')
    audio_path = os.path.join(short_path,'audio')

    ## Sprite Cleanup
    entity_data, audio_data = get_entity_data(entity_path)
    misc_data = get_misc_data(short_path,['.nineslice', '.palettes'])

    entity_data.extend(misc_data)
    
    cleaned_sprites = clean_sprites(sprite_path, entity_data, project_path)
    clean_folders(sprite_path)

    ## Audio Cleanup
    if advanced_audio == True:
        script_audio_data = get_audio_data(scripts_path)
        audio_data.extend(script_audio_data)
        audio_data = [a for a in audio_data if a != '']
        audio_data = list(set(audio_data))
        #print('This is audio data')
        #print(audio_data)
        cleaned_audio = clean_audio(audio_path,audio_data,project_path)
    else:
        cleaned_audio = clean_audio_basic(audio_path,project_path)
    #print(audio_data)

    return cleaned_sprites, cleaned_audio

'''Function that gets all entity data required'''
def get_entity_data(folder_path:str):
    entity_data = []
    audio_data = []
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            if '.entity' in file:
                new_data = parse_entity(os.path.join(folder_path,file))
                entity_data.extend(new_data)

                new_audio_data = parse_entity_audio(os.path.join(folder_path,file))
                audio_data.extend(new_audio_data)
    
    return entity_data, audio_data

'''Function that returns all symbol uuids from an entity'''
def parse_entity(file_path:str):
    data = getJSONData(file_path)
    symbols = []
    for s in data['symbols']:
        if s['type'] == "IMAGE": 
            symbols.append(s["imageAsset"])

    return symbols

'''Funciton that scans for nineslice files and returns the image asset ids'''
def get_misc_data(folder_path:str, file_extensions:list):
    misc_data = []
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            for fe in file_extensions:
                if fe in file:
                    data = getJSONData(os.path.join(subdir,file))
                    misc_data.append(data['imageAsset'])
                
    return misc_data

'''
Function for iterating over all sprite
.meta files within the project sprite folder.
If the uuid is not found within the entities,
remove the sprite
'''
def clean_sprites(folder_path:str, entity_data:list, project_path:str):
    cleaned_sprites = 0
    ## Iterate over all files
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            ## Check if .meta is in the file
            if '.meta' in file:

                ## Used to get the name of the subdir
                folder_name = subdir.split('library\\sprites')[-1]
                
                data = getJSONData(os.path.join(subdir,file))
                ## If guid not in the valid entity data, yeet it out
                if data['guid'] not in entity_data:
                    moveBadSprites(project_path,os.path.join(subdir,file),folder_name,'sprites')
                    cleaned_sprites += 1
                    
    return cleaned_sprites
         
'''Function that removes all empty folders from the sprites folder'''
def clean_folders(folder_path:str):
    
    ## Iterate over all subdirs
    for subdir, dirs, files in os.walk(folder_path):
        ## If the length of the subdir is 0
        ## then recursively remove all directories with .removedirs
        if len(os.listdir(subdir)) == 0:
            os.removedirs(subdir)

    
'''Function that moves all bad sprites out of the sprites folder'''
def moveBadSprites(folder_path:str,bad_sprite:str, folder_name:str, extension:str):
    ## Default cleanp path in project folder
    cleanup_path = os.path.join(folder_path,'cleanup',extension)

    ## If the cleanup folder is non-existent, create it
    if not os.path.exists(cleanup_path):
        os.makedirs(cleanup_path)

    ## length folder_name could be 0 if the sprites
    ## are not located in a subdir in sprites folder
    if len(folder_name) != 0:
        cleaner_path = os.path.join(cleanup_path,folder_name[1:])
    else:
        cleaner_path = cleanup_path
        
    
    ## If subdir does not exist, make it
    ## and parent dirs inside of the cleanup folder
    if not os.path.exists(cleaner_path):
        os.makedirs(cleaner_path)
        
    ## If the file already exists within the cleanup folder
    ## remove that file from the project
    ## Avoids errors with the .move() function
    if os.path.isfile(os.path.join(cleaner_path,bad_sprite.split('\\')[-1])):
        os.remove(bad_sprite)
        if checkFile(bad_sprite.replace('.meta','')) == True:
            os.remove(bad_sprite.replace('.meta',''))
        
    ## Else move that bad sprite OUTTA THERE
    else:
        shutil.move(bad_sprite,cleaner_path)
        if checkFile(bad_sprite.replace('.meta','')) == True:
            shutil.move(bad_sprite.replace('.meta',''),cleaner_path)
        

def get_audio_data(folder_path:str):
    ## Iterate over all subdirs
    audio_data = []
    valid_lines = ['attackVoiceIds','hurtLightVoiceIds','hurtMediumVoiceIds','hurtHeavyVoiceIds','koVoiceIds']
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            if 'characterstats.hx' in file.lower() and '.meta' not in file:
                data = readFile(os.path.join(subdir,file))
                for d in data:
                    for vl in valid_lines:
                        if vl in d:
                            new_data = d[d.find('['):d.find(']')+1]
                            json_data = json.loads(new_data)
                            audio_data.extend(json_data)
            elif 'script.hx' in file.lower() and '.meta' not in file:
                data = readFile(os.path.join(subdir,file))
                for d in data:
                    if 'AudioClip.play(self.getResource().getContent' in d:
                        start = d.find('.getContent')
                        audio_term = d[d.find('(',start)+1:d.find(')',start)]
                        audio_term = audio_term.replace('"','').replace("'",'')
                        audio_data.append(audio_term)

    return audio_data

def parse_entity_audio(file_path:str):
    data = getJSONData(file_path)
    audio = []
    for s in data['keyframes']:
        if s['type'] == "FRAME_SCRIPT":
            
            code = s['code']
            
            if code != None and 'AudioClip.play(self.getResource()' in code:
                
                code_items = code.splitlines()
                
                for ci in code_items:
                    if 'AudioClip.play(self.getResource().getContent' in ci:
                        start = ci.find('.getContent')
                        audio_term = ci[ci.find('(',start)+1:ci.find(')',start)]
                        audio_term = audio_term.replace('"','').replace("'",'')
                        audio.append(audio_term)
                    
    return audio

def clean_audio(folder_path:str, audio_data:list, project_path:str):
    cleaned_audio = 0
    ## Iterate over all files
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            ## Check if .meta is in the file
            if '.meta' in file:
                
                ## Used to get the name of the subdir
                folder_name = subdir.split('library\\audio')[-1]
                
                data = getJSONData(os.path.join(subdir,file))
                ## If guid not in the valid entity data, yeet it out
                if data['id'] not in audio_data:
                    moveBadSprites(project_path,os.path.join(subdir,file),folder_name,'audio')
                    cleaned_audio += 1
                    
    return cleaned_audio

def clean_audio_basic(folder_path:str, project_path:str):
    cleaned_audio = 0
    ## Iterate over all files
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            ## Check if .meta is in the file
            if '.meta' in file:
                ## Used to get the name of the subdir
                folder_name = subdir.split('library\\audio')[-1]
                
                data = getJSONData(os.path.join(subdir,file))
                ## If guid not in the valid entity data, yeet it out
                if data['id'] == '':
                    moveBadSprites(project_path,os.path.join(subdir,file),folder_name,'audio')
                    cleaned_audio += 1
                    
    return cleaned_audio
                         
'''Creates the Fray Theme'''
fray_theme = {'BACKGROUND': '#323232',
             'TEXT': '#e2eef5',
             'INPUT': '#585858',
             'TEXT_INPUT': '#cecad0',
             'SCROLL': '#585858',
             'BUTTON': ('#e2eef5', '#585858'),
             'PROGRESS': ('#f5ba04', '#6b6b6b'),
             'BORDER': 1,
             'SLIDER_DEPTH': 0,
             'PROGRESS_DEPTH': 0}

sg.theme_add_new('fraymakers', fray_theme)                   

sg.theme('fraymakers')
sg.set_options(font=('Calibri',12))

'''Window Functions'''
def update_visibility(elements: dict):
    '''
    Updates the visibility
    of specified elements
    '''
    global window
    for k,v in elements.items():
        window[k].update(visible=v)

def update_table_values(table_name: str):
    '''
    Updates table values
    based upon table name
    '''
    global window
    
    window['db_table'].update(values=anim_indexes)
    
    return anim_indexes

def update_disabled(elements: dict):
    '''
    Updates the disabled
    status of buttons
    '''
    global window
    for k,v in elements.items():
        window[k].update(disabled=v)


layout = [[sg.Text('Project Cleanup V1.0', justification='center',font=('Centie Sans',26))],
          [sg.Text('Project Folder',font=('Edit Undo BRK',18)),
           sg.InputText(key='project_folder_path',size=25),
           sg.FolderBrowse(key='project_folder')],
          [sg.Checkbox('Batch Clean Projects', default=False,key='batch_project_clean',enable_events=True)],
          [sg.Checkbox('Advanced Audio Cleanup', default=False,key='advanced_audio_check',enable_events=True)],
          [sg.Button('Submit'),sg.Button('Exit')]]

window = sg.Window('Project Cleanup',layout,element_justification = 'center')

while True:
    event, values = window.read()
    
    if event == None or event == 'Exit':
        window.close()
        break

    elif event == 'Submit':
        folder = values['project_folder_path']
        if values['batch_project_clean'] == False:
            if checkFolder(folder) == True:
                cleaned_stats = cleanup_project(folder, values['advanced_audio_check'])
                sg.popup('Project successfully cleaned!!\nA backup of all things removed can be found in the base project folder called cleanup\nStats:\n'+str(cleaned_stats[0])+' sprites were cleaned\n'+str(cleaned_stats[1])+' audio files were cleaned!')
        else:
            cleaned_stats = cleanup_batch_project(folder, values['advanced_audio_check'])
            sg.popup('Project successfully cleaned!!\nA backup of all things removed can be found in the base project folder called cleanup\nStats:\n'+str(cleaned_stats[0])+' projects were cleaned\n'+str(cleaned_stats[1])+' sprites were cleaned\n'+str(cleaned_stats[2])+' audio files were cleaned!')
            
    elif event == 'advanced_audio_check':
        if values['advanced_audio_check'] == True:
            sg.popup('Warning: This method is still experimental!! May remove unwanted audio files')
        
    elif event == 'batch_project_clean':
        if values['batch_project_clean'] == True:
            sg.popup('Warning: This method cleans all projects in the provided folder! Only use if you want all projects in the folder to be cleaned')
