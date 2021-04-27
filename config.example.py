# Game Flavourtext
import json

bio_gametext = [
        'Among Us',
]

# Pastebin Setup
pb_dev_key = "pastebinkey"
pb_dev_user = "pastebinuser"
pb_dev_pass = "pastebinpassword"

# Saucenao Setup
sn_key = "saucenao api key"

# Baker Mayfield
bmCounter = 0

# Vagina Counter
vaginaCounter = 0

with open('data.json') as json_file:
    data = json.load(json_file)
    vaginaCounter = int(data['vagina'])

# PFP
# with open('mad.jpg', 'rb') as f:
#     pfpAngury = f.read()
# with open('bio2.png', 'rb') as f:
#     pfpDefault = f.read()

# Reactions
REACT_QUOTE = "💬"
REACT_BIOONLY = "🗨"
REACT_SAUCE = "🍝"

REACT_M = "🇲"
REACT_I = "🇮"
REACT_L = "🇱"
REACT_D = "🇩"
REACT_C = "🇨"
REACT_A = "🇦"
REACT_R = "🇷"
REACT_P = "🇵"
REACT_E = "🇪"
REACT_T = "🇹"

REACT_Y = "🇾"
REACT_S = "🇸"
REACT_U = "🇺"
REACT_G = "🇬"
REACT_W = "🇼"


# Bot Setup
BOT_PREFIX = "bio!"
TOKEN = "your discord bot client key here"