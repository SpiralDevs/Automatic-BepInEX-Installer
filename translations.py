import os
import json

CURR_LANG = 'en_us'

with open(os.path.join('resources', 'langs', f'{CURR_LANG}.json')) as file:
    translation = json.load(file)

ROOT_TITLE = translation['root']['title']
ROOT_SHORT_TITLE =  translation['root']['short_title']

WIDGETS_INSERT = translation['widget']['insert']

NON_STEAM_INSTALL = translation['non_steam_install']
STEAM_INSTALL = translation['steam_install']

STEAM_COMMON_DIR_PROMPT = translation['steam_common_dir_prompt']

# ERRORS

ERRORS_GAMENOTFOUND_TITLE = translation['errors']['game_not_found']['title']
ERRORS_GAMENOTFOUND_DESC = translation['errors']['game_not_found']['desc']