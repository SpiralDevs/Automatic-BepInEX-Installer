import os
import json

CURR_LANG = 'en_us'

with open(os.path.join('resources', 'langs', f'{CURR_LANG}.json')) as file:
    translation = json.load(file)

ROOT_TITLE = translation['root']['title']

ROOT_STEAM =  translation['root']['steam']
ROOT_NONSTEAM =  translation['root']['non_steam']

WIDGETS_INSERT = translation['widget']['insert']

NON_STEAM_INSTALL = translation['non_steam_install']
STEAM_INSTALL = translation['steam_install']
INSTALL_BEPINEX = translation['install_bepinex']
SELECTBEPINEX = translation['select_bepinex_ver']

# STEAM
STEAM_GAMENAMEFOLDER = translation['steam']['game_name_folder']
STEAM_STEAMDIR = translation['steam']['steam_directory']
STEAM_AUTOFINDDIR = translation['steam']['autofind_dir']

# NON-STEAM
NONSTEAM_ASKDIR = translation['non_steam']['ask_dir']
NONSTEAM_GAMEDIR = translation['non_steam']['game_dir']
NONSTEAM_OPENFOLDER = translation['non_steam']['open_folder']

# TOOLTIPS
TOOLTIP_ENTERSTEAMDIR = translation['tooltip']['enter_steam_dir']
TOOLTIP_GAMENAMEFOLDER = translation['tooltip']['game_name_folder']
TOOLTIP_ENTERDIR = translation['tooltip']['enter_dir']
TOOLTIP_OPENDIR = translation['tooltip']['open_dir']
# INFO
INFO_STEAMALREADYSET_TITLE = translation['info']['steam_dir_already_set']['title']
INFO_STEAMALREADYSET_DESC = translation['info']['steam_dir_already_set']['desc']

INFO_BEPINEXINSTALLED_TITLE = translation['info']['bepinex_installed']['title']
INFO_BEPINEXINSTALLED_DESC = translation['info']['bepinex_installed']['desc']

INFO_BEPINEXALREADYADDED_TITLE = translation['info']['bepinex_already_added']['title']
INFO_BEPINEXALREADYADDED_DESC = translation['info']['bepinex_already_added']['desc']

# ERRORS
ERRORS_GAMENOTFOUND_TITLE = translation['errors']['game_not_found']['title']
ERRORS_GAMENOTFOUND_DESC = translation['errors']['game_not_found']['desc']

ERRORS_NOVALIDURL_TITLE = translation['errors']['no_valid_url']['title']
ERRORS_NOVALIDURL_DESC = translation['errors']['no_valid_url']['desc']

ERRORS_INVALIDDIR_TITLE = translation['errors']['invalid_dir']['title']
ERRORS_INVALIDDIR_DESC = translation['errors']['invalid_dir']['desc']

ERRORS_EMPTYGAMEFOLDER_TITLE = translation['errors']['empty_game_folder']['title']
ERRORS_EMPTYGAMEFOLDER_DESC = translation['errors']['empty_game_folder']['desc']

ERRORS_EMPTYSTEAMDIR_TITLE = translation['errors']['empty_steam_dir']['title']
ERRORS_EMPTYSTEAMDIR_DESC = translation['errors']['empty_steam_dir']['desc']

ERRORS_EMPTYGAMEDIR_TITLE = translation['errors']['empty_game_dir']['title']
ERRORS_EMPTYGAMEDIR_DESC = translation['errors']['empty_game_dir']['desc']

ERRORS_UNSUPPORTEDOS_TITLE = translation['errors']['unsupported_os']['title']
ERRORS_UNSUPPORTEDOS_DESC = translation['errors']['unsupported_os']['desc']

ERRORS_INVALIDPATH_TITLE = translation['errors']['invalid_path']['title']
ERRORS_INVALIDPATH_DESC = translation['errors']['invalid_path']['desc']