import mechanicalsoup
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import time

version = '0.4'

#---- Sunwell Login Code

browser = mechanicalsoup.StatefulBrowser()

browser.open("https://sunwell.pl/")

browser.select_form('form[action="https://sunwell.pl/ucp/login"]')

browser["username"] = "GrearBot"
browser["password"] = "windclubes"
browser["realm_type"] = "Frosthold"
browser.submit_selected()

#---- Google Sheets auth

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

template = client.open("gear_template").sheet1
sheet = client.open("Requiem_Roster_Gear")


def parse(ign):
    gearlist = []
    dirtylist = []
    browser.open("https://sunwell.pl/armory/Frosthold/" + ign)
    pull = browser.get_current_page().findAll("div", class_="item-slot")
    blacklist = json.loads(open('blacklist.json').read())

    for item in pull:
        line = str(item).split("<")
        split1 = (line[3])
        split2 = split1.split('"')

        try:
            split3 = split2[3].split('=')
            if int(split3[1]) in blacklist:
                pass
            else:
                gearlist.append(split2[3])
                try:
                    dirtylist.append(split2[5])
                except IndexError:
                    pass
        except IndexError:
            pass
    return gearlist, dirtylist


def enchant(id):
    browser.open('https://wotlk.evowow.com/?enchantment=' + id)
    itemname = browser.get_current_page().find('h1')
    cleaned = str(itemname).split(">")
    cleaned2 = cleaned[1].split("<")
    return cleaned2[0]


def gems(id):
    browser.open('https://wotlk.evowow.com/?item=' + id)
    itemname = browser.get_current_page().find('h1')
    cleaned = str(itemname).split(">")
    cleaned2 = cleaned[1].split("<")
    return cleaned2[0]


def gearcheck(item):
        browser.open(item)
        itemname = browser.get_current_page().find('h1')
        cleaned = str(itemname).split(">")
        cleaned2 = cleaned[1].split("<")
        return cleaned2[0]


def rostercheck():
    i = 0

    names = json.loads(open('roster.json').read())
    sheetlist = sheet.worksheets()

    for wk in sheetlist:
        if i < 1:
            pass
        else:
            sheet.del_worksheet(wk)
        i += 1

    for name in names:
        i = 0

        worksheet = sheet.add_worksheet(title=name, rows="25", cols="5")
        parsed = parse(name)
        char = parsed[0]
        dirty = parsed[1]

        itemlist = []
        enchantlist = []
        gemlist1 = []
        gemlist2 = []
        gemlist3 = []
        gemdict = [gemlist1, gemlist2, gemlist3]

        for item in char:
            cleaned = gearcheck(item)
            link = "=HYPERLINK({},{})".format('"' + item + '"', '"' + cleaned + '"')
            itemlist.append([link])

        worksheet.update('A2', itemlist, value_input_option='USER_ENTERED')

        for item in dirty:
            if "ench" in item:
                loc = item.find("ench")
                stats = enchant(item[loc + 5:loc + 9])
                if stats.startswith("+4" or "+6" or "+5" or "+8"):
                    enchantlist.append([])
                else:
                    enchantlist.append([stats])
            else:
                enchantlist.append([])

        worksheet.update('B2', enchantlist)

        for item in dirty:
            z = 0
            if "gems" in item:
                split = item[5:].split("&")
                split2 = split[0].split(":")
                while z <= 2:
                    try:
                        stats = gems(split2[z])
                        gemdict[z].append([stats])
                    except IndexError:
                        gemdict[z].append([])
                    z += 1
            else:
                gemdict[0].append([])
                gemdict[1].append([])
                gemdict[2].append([])

        for x in gemdict:
            worksheet.update(chr(ord('C') + i) + str(2), gemdict[i])
            i += 1

rostercheck()

