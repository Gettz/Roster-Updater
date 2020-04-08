import mechanicalsoup
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import time

version = '0.2'

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

sheet = client.open("Requiem_Roster_Gear")


def parse(ign):
    gearlist = []
    browser.open("https://sunwell.pl/armory/Frosthold/" + ign)
    pull = browser.get_current_page().findAll("div", class_="item-slot")
    for item in pull:
        line = str(item).split("<")
        split1 = (line[3])
        split2 = split1.split('"')
        try:
            if split2[3] == "https://db.darkwizard.pl/?item=5976":
                pass
            else:
                gearlist.append((split2[3]))
        except IndexError:
            pass
    return gearlist


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
        i = 1

        print(name)
        worksheet = sheet.add_worksheet(title=name, rows="25", cols="5")
        char = parse(name)

        for item in char:
            cleaned = gearcheck(item)
            worksheet.update('A' + str(i), cleaned)
            worksheet.update('B' + str(i), item)
            i += 1
            time.sleep(1)

rostercheck()
