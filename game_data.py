# ------------------------------------------------------------------------------
# file: game_data.py
# desc: data for the LPL game
# Dec 2024: Original code
# ------------------------------------------------------------------------------
passkeys = {
    "[50, 109, 134, 108, 181]": "YoricksSkull",
    "[242, 73, 113, 108, 166]": "ArthursTowel",
    "[226, 232, 146, 108, 244]": "PippinsBrooch",
    "[210, 182, 148, 108, 156]": "ShireMap",
    "[178, 242, 124, 108, 80]": "BardsMask",
    "[34, 55, 79, 108, 54]": "BabelFish",
    "[226, 174, 130, 108, 162]": "GandalfsPipe",
    "[50, 117, 133, 108, 174]": "Tollbooth",
    "[82, 15, 107, 108, 90]": "HamletsQuill",
    "[2, 162, 97, 108, 173]": "NotQuiteTea",
    "[66, 105, 186, 108, 253]": "JulietsPoison",
    "[114, 247, 103, 108, 142]": "EmmasPractice",
    "[98, 140, 132, 108, 6]": "TimeTurner",
    "[146, 36, 94, 108, 132]": "VictorsNotes",
    "[130, 7, 166, 108, 79]": "HestersLace",
    "[226, 105, 133, 108, 98]": "RonsWand",
    "[194, 236, 174, 108, 236]": "DarcysLetter",
    "[114, 219, 72, 108, 141]": "SortingHat",
    "[66, 53, 63, 108, 36]": "NarsilShards",
    "[114, 203, 75, 108, 158]": "MarleysChains",
    "[146, 43, 80, 108, 133]": "VictorsEquip",
    "[146, 173, 67, 108, 16]": "HestersA",
    "[210, 248, 93, 108, 27]": "Remembrall",
    "[66, 202, 71, 108, 163]": "WinstonsRations",
    "[2, 234, 195, 108, 71]": "VictoryGin",
    # Test passkeys
    "[58, 18, 86, 246, 136]": "TestSticker",
    "[117, 61, 155, 154, 73]": "TestTag"
}

artifacts={
    "YoricksSkull": "lost",
    "ArthursTowel": "lost",
    "PippinsBrooch": "lost",
    "BabelFish": "lost",
    "JulietsPoison": "lost",
    "TimeTurner": "lost",
    "DarcysLetter": "lost",
    "HestersA": "lost",
    "TestTag": "lost"
}

players={
    "[238, 60, 233, 48, 11]": "Tony",
    "[206, 27, 119, 48, 146]": "Dani",
    "[110, 3, 186, 153, 78]": "Zach",
    "[190, 48, 93, 50, 225]": "Lupe",
    "[206, 32, 179, 153, 196]": "Sofi",
    "[158, 13, 171, 153, 161]": "Ron",
    "[126, 250, 180, 153, 169]": "Paige",
    "[94, 203, 103, 49, 195]": "Marshall",
    # Test players
    "[174, 175, 176, 153, 40]": "John",
    "[62, 200, 246, 48, 48]": "Sherri",
    "[203, 48, 38, 3, 222]": "TestCard"
}

player_status={
    "Tony": "inactive",
    "Dani": "inactive",
    "Zach": "inactive",
    "Lupe": "inactive",
    "Sofi": "inactive",
    "Ron": "inactive",
    "Paige": "inactive",
    "Marshall": "inactive",
    # Test players
    "John": "inactive",
    "Sherri": "inactive",
    "TestCard": "inactive"
}

player_assignment={
    "Tony": "YoricksSkull",
    "Dani": "ArthursTowel",
    "Zach": "PippinsBrooch",
    "Lupe": "BabelFish",
    "Sofi": "JulietsPoison",
    "Ron": "TimeTurner",
    "Paige": "DarcysLetter",
    "Marshall": "HestersA",
    # Test players
    "John": "NotLost",
    "Sherri": "NotLost",
    "TestCard": "TestTag"
}

"""
The first set of clues indcating which passkeys to find.
""" 
passkey_clues={
    "BabelFish":
    "A tiny friend, within the ear it lies,\nTranslating tongues, of any alien kind.\nA miracle of science, a wondrous prize,\nUnlocking worlds, where understanding's \n    enshrined.",
    "PippinsBrooch":
    "A gift of grace, from Elven hands so fine,\nA shimmering gem, a beauty unsurpassed.\nIt whispers tales of ancient lore divine,\nA bond of friendship, forever to be cast.",
    "MarleysChains":
    "A specter bound, by errors of the past,\nA chilling sight, where guilt forever \n    lies.\nA mournful plea, for mercy that won't \n    last,\nA haunting sign, of where the soul can \n    rise.",
    "DarcysLetter":
    "A confession penned, with honesty and \n    grace,\nOf pride subdued, and prejudice laid low.\nA plea for love, in words of heartfelt \n    space,\nA chance for bliss, where true affections \n    grow.",
    "JulietsPoison":
    "A secret held, a deadly art concealed,\nTo mimic death, and steal the life away.\nA desperate act, where true love is \n    revealed,\nA final sleep, until the break of day.",
    "HestersA":
    "A mark of shame, upon a breast it lies,\nA symbol borne, of sin and shame and \n    grace.\nA constant thorn, that pierces and that \n    tries,\nA badge of love, in this forsaken place.",
    "TimeTurner":
    "A golden hour, spun within a hand,\nTo bend the clock, and time's relentless \n    flow.\nA secret kept, across the wizard land,\nTo mend the past, and futures yet to know.",
    "Tollbooth":
    "A coin unseen, yet payment it demands,\nFor entry sought, to lands of pure \n    delight.\nA toll exacted, by unseen hands,\nFor journeys born, in shadows of the \n    night.",
    "ArthursTowel":
    "A traveler's friend, a comfort in the \n    vast,\nA humble cloth, yet worth a king's domain.\nThrough cosmic woes, its presence ever \n    fast\nA symbol of hope, defying space and rain.",
    "YoricksSkull":
    "I was a head, once full of wit and grace,\nNow hollowed out, a vessel for the dust.\nMy laughter's gone, replaced by a grim \n    face,\nA silent echo of life's fleeting gust.",
 
    "TestTag":
    "A test, a trial, this, a fleeting art,\nTo weave a spell, to play a subtle part,\nTo give these words a life, a beating \n    heart,\nA simple task, to tear the soul apart.",
    "NotLost":
    "The empty slot, a barren, lonely space,\nNo treasure found, nor artifact to\n    claim.\nHis quest remains, with unadorned grace,\nNo fitting prize to glorify his name."
}

"""
These clue indicate where to find the artifacts
"""
artifact_clues = {
"YoricksSkull":
    "no clue",
"ArthursTowel":
    "no clue",
"PippinsBrooch":
    "no clue",
"BabelFish":
    "no clue",
"JulietsPoison":
    "no clue",
"TimeTurner":
    "no clue",
"DarcysLetter":
    "no clue",
"HestersA":
    "no clue",
"TestTag":
    "no clue"
}

ErrorMessages = {
    "Error":
    "An error found, a glitch, a sudden halt,\nMy program stumbles, loses its own fault.\nA message cryptic, a frustrating call,\nI have encountered an error, that's all.",
    "NotAuthenticated":
    "You are not logged in, the manual's command,\nRead its advice, to understand the land.\nInstructions guide, the path to this \n    domain,\nSo read with care, and find your rightful \n    gain.",
    "NotLost":
    "This passkey, though strange, is not \n    misplaced,\nNor vanished, gone, nor in the shadows \n    chased.\nIt may be found, its purpose can be \n    traced,\nThis passkey is not lost, it's in its \n    place",
    "WrongPasskey":
    "This passkey, a task not your own,\nBelongs elsewhere, a story left unknown.\nYour quest lies elsewhere, on a different \n    trail,\nThis object's purpose, you cannot avail.",
    "WrongArtifact":
    "This artifact, is not your own,\nBelongs elsewhere, a story left unknown.\nYour quest lies elsewhere, on a different \n    trail,\nThis object's purpose, you cannot avail."
}
