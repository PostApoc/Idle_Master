import logging
from colorama import init, Fore, Back, Style

def inGame():
    
    import bs4
    import requests
    from start import getSettings, generateCookies

    authData = getSettings()
    myProfileURL = "http://steamcommunity.com/profiles/" + authData["steamLogin"][:17]

    try:
        cookies = generateCookies(authData)
        r = requests.get(myProfileURL, cookies=cookies)
    except:
        logging.fatal("Error reading profile page")
        return

    try:
        profilePage = bs4.BeautifulSoup(r.text, "lxml")
        profileStatus = profilePage.find("div", class_="playerAvatar")['class']
        #profileStatus = profilePage.findAll("div",{"class" : "user_avatar"})
        logging.info("Found profile status")
    except:
        logging.fatal("Did not find profile status")
        return

    if "in-game" or "online" in profileStatus:
        return True
    if "offline" in profileStatus:
        return False
    else:
        print profileStatus
        logging.fatal("Did not find profile status in " + profileStatus)
        return

def gamesLeft():
    
    import bs4
    import requests
    import re
    from start import getSettings, generateCookies

    authData = getSettings()
    myProfileURL = "http://steamcommunity.com/profiles/" + authData["steamLogin"][:17]

    try:
        cookies = generateCookies(authData)
        r = requests.get(myProfileURL + "/badges/",cookies=cookies)
    except:
        logging.fatal("Error reading badge page")
        return

    try:
        badgesLeft = []
        badgePageData = bs4.BeautifulSoup(r.text, "lxml")
        badgeSet = badgePageData.find_all("div",{"class": "badge_title_stats"})
    except:
        logging.fatal("Error finding drop info")
        return

    # For profiles with multiple pages
    try:
        badgePages = int(badgePageData.find_all("a",{"class": "pagelink"})[-1].text)
        if badgePages:
            logging.info(str(badgePages) + " badge pages found.  Gathering additional data")
            currentpage = 2
            while currentpage <= badgePages:
                r = requests.get(myProfileURL + "/badges/?p=" + str(currentpage),cookies=cookies)
                badgePageData = bs4.BeautifulSoup(r.text, "lxml")
                badgeSet = badgeSet + badgePageData.find_all("div",{"class": "badge_title_stats"})
                currentpage = currentpage + 1
    except:
        logging.info("Reading badge page, please wait")

    userinfo = badgePageData.find("a",{"class": "user_avatar"})
    if not userinfo:
        logging.fatal("Invalid cookie data, cannot log in to Steam")
        return

    for badge in badgeSet:
        try:
            badge_text = badge.get_text()
            dropCount = badge.find_all("span",{"class": "progress_info_bold"})[0].contents[0]
            has_playtime = re.search("[0-9\.] hrs on record", badge_text) != None
            if "No card drops" in dropCount or (has_playtime == False and authData["hasPlayTime"].lower() == "true") :
                continue
            else:
                # Remaining drops
                dropCountInt, junk = dropCount.split(" ",1)
                dropCountInt = int(dropCountInt)
                linkGuess = badge.find_parent().find_parent().find_parent().find_all("a")[0]["href"]
                junk, badgeId = linkGuess.split("/gamecards/",1)
                badgeId = int(badgeId.replace("/",""))
                push = [badgeId, dropCountInt, 0]
                badgesLeft.append(push)
        except:
            continue
     
    return len(badgesLeft)

if __name__ == '__main__':
    
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter("[ %(asctime)s ] %(message)s", "%m/%d/%Y %I:%M:%S %p"))
    logging.getLogger('').addHandler(console)

    int_gamesLeft = gamesLeft()
    bool_inGame = inGame()

    # executed as a script
    logging.warning("Steam games with cards: " + str(int_gamesLeft))
    logging.warning("Player in-game: " + str(bool_inGame))