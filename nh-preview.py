#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("Initializing . . .")


# In[2]:


# webscraping
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup

# regex, used in functions reSplit and validSearch
import re

# used in function openSite
import webbrowser

# rng used in random action
import secrets

# ceiling function
import math


# In[3]:


# webscraper init
site = "https://nhentai.net"
hdr = {"User-Agent": "Mozilla/5.0"}
bookpage = requests.get(site)
soup = BeautifulSoup(bookpage.text, "html.parser")


# In[4]:


# get numlim (ID limit)
numlim_htm = soup.find_all("a", class_ = "cover")[0]
numlim_htm = str(numlim_htm)
numlim = (numlim_htm.split("href=\"/g/")[1]).split("/\" style=")[0]
numlim = int(numlim)


# In[5]:


# get blacklist from file
# blacklist states:
# 1. empty: "#"
# 2. used: "[tag1];[tag2];[tag3]"
# 3. does not exist: go to exception
try:
    blackfile = open("blacklist.txt", "r")
    blacklist = blackfile.read()
    if blacklist[0] == "#":
        blacklist = []
    else:
        blacklist = blacklist.split(";")
except:
    blackfile = open("blacklist.txt", "w")
    blackfile.close()


# In[6]:


# convert a string-number with or without comma into an int type
def commaInt (instr):
    if (len(instr)<=3 or instr[-4]!=","):
        return int(instr)
    thousands = int(instr.split(",")[0])
    ones = int(instr.split(",")[1])
    if (thousands > 0):
        return (thousands * 1000 + ones)
    else:
        return (thousands * 1000 - ones)


# In[7]:


# convert an int into a string with comma
def commaStr (inum):
    if (inum < 1000):
        return str(inum)
    thousands = str(math.floor(inum / 1000))
    ones = str(inum % 1000)
    return (thousands + "," + ones)


# In[8]:


# split a string by the strings highlighted in delimiters
def reSplit (instr):
    delimiters = "\n\t\t\t\t\t\t", " (", ")"
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, instr)


# In[9]:


# returns 0 to quit, returns valid ID otherwise
def getDoujinID (come_from_search):
    
    r_doujin_id = 0
    
    while (r_doujin_id == 0 or abs(r_doujin_id) > numlim):
        
        print("\nWhich doujin to preview?")
        print("(Positive integer): Access doujin with ID")
        if come_from_search == False:
            print("(Negative integer): Access most recent doujins")
        print("(R)eturn")
        r_doujin_id = input().upper()
        
        if r_doujin_id in ["R", "RETURN"]:
            r_doujin_id = 0
            break
        
        try:
            r_doujin_id = commaInt(r_doujin_id)
        except:
            r_doujin_id = 0
        
        if (r_doujin_id == 0 or abs(r_doujin_id) > numlim):
            print("Invalid response, try again")
    
    if r_doujin_id < 0:
        r_doujin_id = numlim + 1 + r_doujin_id
    return r_doujin_id


# In[10]:


# returns true if openSite should be called afterwards
def previewDoujin (doujin_id):
    
    # access site
    doujin_site = ""
    if doujin_id == "random":
        doujin_site = "https://nhentai.net/random"
    else:
        doujin_site = "https://nhentai.net/g/" + str(doujin_id)
    doujin_bookpage = requests.get(doujin_site)
    doujin_soup = BeautifulSoup(doujin_bookpage.text, "html.parser")
    
    # update doujin_id for random search
    if doujin_id == "random":
        doujin_id_htm = doujin_soup.find_all("a")[17]
        doujin_id_htm = str(doujin_id_htm)
        doujin_id = doujin_id_htm.split("href=\"/g/")[1].split("/1/\">")[0]
        doujin_id = int(doujin_id)
    
    # get title and subtitle
    doujin_title    = doujin_soup.find_all("h1")[0].get_text()
    doujin_subtitle = doujin_soup.find_all("h2")[0].get_text()
    
    # get tags
    # some compilers might not register the class with a space at the end
    doujin_alltags_section = doujin_soup.find_all("div", class_="tag-container field-name ")
    if len(doujin_alltags_section) == 0:
        doujin_alltags_section = doujin_soup.find_all("div", class_="tag-container field-name")
    
    doujin_tags = []    # tagtype, [tagnames], [tagcount]
    for doujin_tags_section in doujin_alltags_section:
        doujin_tags_section = doujin_tags_section.get_text()
        doujin_tags_section = reSplit(doujin_tags_section)
        doujin_tags_section = doujin_tags_section[1:-1]
        doujin_tagtype = doujin_tags_section[0]
        doujin_tagnames = []
        doujin_tagcount = []
        for i in range(1, len(doujin_tags_section)):
            if (i % 2 == 1):
                doujin_tagnames.append(doujin_tags_section[i])
            else:
                doujin_tagcount.append(doujin_tags_section[i])
        doujin_tags.append((doujin_tagtype, doujin_tagnames, doujin_tagcount))
    
    # output info + blacklist warnings
    bl_title = 0
    bl_subtitle = 0
    bl_tags = 0
    
    if [bl for bl in blacklist if bl in doujin_title]:
        bl_title = 1
        print("\nTitle:", doujin_title, "<BLACKLISTED>")
    else:
        print("\nTitle:", doujin_title)
        
    if [bl for bl in blacklist if bl in doujin_subtitle]:
        bl_subtitle = 1
        print("\nTitle:", doujin_subtitle, "<BLACKLISTED>")
    else:
        print("\nTitle:", doujin_subtitle)
    
    for i in range(0, len(doujin_tags)):
        print(doujin_tags[i][0])
        for j in range(0, len(doujin_tags[i][1])):
            if doujin_tags[i][1][j] in blacklist:
                bl_tags += 1
                print("    ", doujin_tags[i][1][j], " (", doujin_tags[i][2][j], ") <BLACKLISTED>", sep="")
            else:
                print("    ", doujin_tags[i][1][j], " (", doujin_tags[i][2][j], ")", sep="")
    
    if (bl_title + bl_subtitle + bl_tags) > 0:
        print("\nBLACKLIST WARNINGS:")
        if bl_title > 0:
            print("Title")
        if bl_subtitle > 0:
            print("Subtitle")
        if bl_tags == 1:
            print("1 tag")
        elif bl_tags > 1:
            print(bl_tags, "tags")
    
    # open site
    enter_site = 0
    while True:
        print("\nRead doujin? (Y/N)")
        enter_site = input().upper()
        if (enter_site in ["Y", "YES"]):
            return doujin_id
        elif (enter_site in ["N", "NO"]):
            return 0
        else:
            print("Invalid response, try again")


# In[11]:


# returns true if instr contains only (a-z), (0-9), ' ', ':', '-', '"', '!', '?'
def validSearch (instr):
    inv = re.findall("[^a-z0-9 :\-\"()\[\]!?]", instr)
    return (inv == [])


# In[12]:


# returns string after substituting characters
def qSubChar (matchobj):
    subRes = {
        " " : "+",
        "\"": "%22",
        ":" : "%3A",
        "(" : "%28",
        ")" : "%29",
        "[" : "%5B",
        "]" : "%5D",
        "!" : "%21",
        "?" : "%3F"
    }
    return subRes[matchobj.group()]


# In[13]:


# TO ADD: BLACKLIST SEARCH
def makeSearch ():
    
    global blacklist
    
    wantBack = False
    madeSearch = False
    query = ""
    while (wantBack == False and madeSearch == False):
        print("\nEnter search:")
        print("Accepted characters: a-z 0-9 \":-!?()[]")
        print("Enter \"/help\" for details on how to perform search")
        print("Enter \"/return\" to exit search")
        query = input().lower()
        if query == "/return":
            wantBack = True
        elif query == "/help":
            print("You can search for multiple terms at the same time, and this will return only galleries that contain both terms.")
            print("    For example, [anal tanlines] finds all galleries that contain both [anal] and [tanlines].")
            print("You can exclude terms by prefixing them with \"-\".")
            print("    For example, [anal tanlines -yaoi] matches all galleries matching [anal] and [tanlines] but not [yaoi].")
            print("Exact searches can be performed by wrapping terms in double quotes.")
            print("    For example, [\"big breasts\"] only matches galleries with \"big breasts\" somewhere in the title or in tags.")
            print("These can be combined with tag namespaces for finer control over the query:")
            print("    For example, [parodies: railgun -tags:\"big breasts\"]")
            print("    Tag namespaces: tags, characters, parodies, artists, groups, languages, categories")
        elif validSearch(query):
            madeSearch = True
        else:
            print("Invalid response, try again")
    
    # leave search
    if wantBack == True:
        return False
    
    # add blacklisted results
    for bl_res in blacklist:
        if " " in bl_res:
            query += " -\"" + bl_res + "\""
        else:
            query += " -" + bl_res
    
    # replace characters
    query = re.sub("[ \":()\[\]]", qSubChar, query)
    
    # get site
    search_site = "https://nhentai.net/search/?q=" + query
    while True:
        print("\nSort by (R)ecent or (P)opular?")
        sort_method = input().upper()
        if sort_method in ["R", "RECENT"]:
            break
        elif sort_method in ["P", "POPULAR"]:
            search_site = search_site + "&sort=popular"
            break
        else:
            print("Invalid response, try again")
    
    # webscraping
    search_bookpage = requests.get(search_site)
    search_soup = BeautifulSoup(search_bookpage.text, "html.parser")
    search_count_total = search_soup.find_all("h2")[0].text
    
    # find total results and pages
    if (search_count_total == "No results found"):
        search_count_total = 0
        print("No results found")
        return False
    
    search_count_total = search_count_total.split(" Results")[0]
    print(search_count_total, "results found")
    search_count_total = commaInt(search_count_total)
    search_page_total = int(math.ceil(search_count_total / 25))
    search_page = 1
    
    # page webscrape and output
    search_done = False
    while search_done == False:
        
        search_page_site = search_site + "&page=" + str(search_page)
        search_page_book = requests.get(search_page_site)
        search_page_soup = BeautifulSoup(search_page_book.text, "html.parser")
        search_page_found = search_page_soup.find_all("a", class_="cover")
        search_page_res_count = len(search_page_found)
        print("\nPage ", commaStr(search_page), " of ", commaStr(search_page_total), ", showing results ", commaStr((search_page-1)*25+1), " to ", commaStr((search_page-1)*25+search_page_res_count), sep="")
        
        for i in range(0, search_page_res_count):
            search_page_res = str(search_page_found[i])
            search_page_res_id = search_page_res.split("href=\"/g/")[1].split("/\" style=")[0]
            search_page_res_id = search_page_res_id.rjust(6, " ")
            search_page_res_title = search_page_res.split("<div class=\"caption\">")[1].split("</div>")[0]
            print("   ", search_page_res_id, "  ", search_page_res_title)
        
        if search_page == search_page_total:
            print("\nReached end of search")
            search_done = True
        else:
            while True:
                print("\nSee (M)ore Results or (E)nd Search?")
                search_more = input().upper()
                if search_more in ["E", "END", "END SEARCH"]:
                    print("Search ended")
                    search_done = True
                    break
                elif search_more in ["M", "MORE", "MORE RESULTS", "SEE MORE", "SEE MORE RESULTS"]:
                    search_page += 1
                    break
                else:
                    print("Invalid response, try again")
    
    while True:
        print("\nPreview a search result? (Y/N)")
        search_preview = input().upper()
        if search_preview in ["Y", "YES"]:
            return True
        elif search_preview in ["N", "NO"]:
            return False
        else:
            print("Invalid response, try again")


# In[14]:


def openSite (doujin_id):
    print("Opening . . .")
    print("If the site does not open, make sure you have a stable internet connection and try again")
    doujin_site = "https://nhentai.net/g/" + str(doujin_id)
    webbrowser.open(doujin_site, new=2)


# In[15]:


def runList():
    cont_to_preview = makeSearch()
    if cont_to_preview == True:
        doujin_id = getDoujinID(True)
        if doujin_id == 0:
            return
        doujin_id = previewDoujin(doujin_id)
        if doujin_id != 0:
            openSite(doujin_id)


# In[16]:


def blackView():
    
    global blacklist
    
    if len(blacklist) == 0:
        print("No results found")
        return
    
    bl_page_max = math.ceil(len(blacklist) / 25)
    bl_page_cur = 1
    bl_view = True
    
    while (bl_view == True):
        
        if (bl_page_cur == bl_page_max):
            bl_res_count = len(blacklist) - (bl_page_max - 1) * 25
        else:
            bl_res_count = 25
        print("\nPage ", commaStr(bl_page_cur), " of ", commaStr(bl_page_max), ", showing results ", commaStr((bl_page_cur-1)*25+1), " to ", commaStr((bl_page_cur-1)*25+bl_res_count), sep="")
        
        for i in range((bl_page_cur-1)*25, (bl_page_cur-1)*25+bl_res_count):
            print("   ", blacklist[i])
        
        if (bl_page_cur == bl_page_max):
            print("\nReached end of view")
            bl_view = False
        else:
            while True:
                print("\nSee (M)ore Results or (E)nd Search?")
                search_more = input().upper()
                if search_more in ["E", "END", "END SEARCH"]:
                    print("Search ended")
                    search_done = True
                    break
                elif search_more in ["M", "MORE", "MORE RESULTS", "SEE MORE", "SEE MORE RESULTS"]:
                    bl_page_cur += 1
                    break
                else:
                    print("Invalid response, try again")
        
    return


# In[17]:


def blackEdit():
    
    global blacklist
    
    bl_edit = True
    while (bl_edit == True):
        print("\nEdit blacklist")
        print("(A)dd entry")
        print("(D)elete entry")
        print("(R)eturn")
        
        bl_input = input().upper()
        if bl_input in ["A", "ADD"]:
            wantBack = False
            madeSearch = False
            query = ""
            while (wantBack == False and madeSearch == False):
                print("\nEnter blacklisted tag or string:")
                print("Accepted characters: a-z 0-9 \":-!?()[]")
                print("Enter \"/return\" to exit search")
                query = input().lower()
                if query == "/return":
                    wantBack = True
                elif validSearch(query):
                    madeSearch = True
                    blacklist.append(query)
                else:
                    print("Invalid response, try again")
        
        elif bl_input in ["D", "DELETE"]:
            wantBack = False
            madeSearch = False
            query = ""
            while (wantBack == False and madeSearch == False):
                print("\nEnter blacklisted tag or string:")
                print("Accepted characters: a-z 0-9 \":-!?()[]")
                print("Enter \"/return\" to exit search")
                query = input().lower()
                if query == "/return":
                    wantBack = True
                elif validSearch(query):
                    try:
                        blacklist.remove(query)
                        madeSearch = True
                    except:
                        print("Tag not found in blacklist")
                else:
                    print("Invalid response, try again")
        
        elif bl_input in ["R", "RETURN"]:
            bl_edit = False
            
        else:
            print("Invalid response, try again")
    
    return


# In[18]:


def black():
    want_back_blacklist = False
    while (want_back_blacklist == False):
        print("\nSettings: Blacklist")
        print("(V)iew")
        print("(E)dit")
        print("(R)eturn")
        
        user_action_blacklist = input().upper()
        
        if user_action_blacklist in ["V", "VIEW"]:
            blackView()
        elif user_action_blacklist in ["E", "EDIT"]:
            blackEdit()
        elif user_action_blacklist in ["R", "RETURN"]:
            want_back_blacklist = True
        else:
            print("Invalid response, try again")


# In[19]:


def runSet():
    want_back_set = False
    while (want_back_set == False):
        print("\nSettings")
        print("(B)lacklist: Edit blacklist")
        print("(R)eturn: Return to home")
        
        user_action_set = input().upper()
        
        if user_action_set in ["B", "BLACK", "BLACKLIST"]:
            black()
        elif user_action_set in ["R", "RETURN"]:
            want_back_set = True
        else:
            print("Invalid response, try again")


# In[20]:


def closeProgram():
    global blacklist
    blackfile = open("blacklist.txt", "w")
    if len(blacklist) == 0:
        blackfile.write("#")
    else:
        blacklist.sort()
        blacklist = ";".join(blacklist)
        blackfile.write(blacklist)
    blackfile.close()
    return


# In[21]:


print("Initialization complete!\n\nWelcome!\n====================================\n")


# In[22]:


# driver
quit = False
while (quit == False):
    print("\nWhat would you like to do?")
    print("(O)pen: Directly open a doujin")
    print("(P)review: See information about a doujin")
    print("(R)andom: Preview a random doujin")
    print("(L)ist: Look for your favourite doujin")
    print("(S)ettings: Personalize the assistant")
    print("(Q)uit: Exit program")
    
    user_action = input().upper()
    
    if user_action in ["O", "OPEN"]:
        doujin_id = getDoujinID(False)
        if doujin_id == 0:
            continue
        openSite(doujin_id)
        
    elif user_action in ["P", "PREVIEW"]:
        doujin_id = getDoujinID(False)
        if doujin_id == 0:
            continue
        doujin_id = previewDoujin(doujin_id)
        if doujin_id != 0:
            openSite(doujin_id)
        
    elif user_action in ["R", "RANDOM"]:
        doujin_id = "random"
        doujin_id = previewDoujin(doujin_id)
        if doujin_id != 0:
            openSite(doujin_id)
        
    elif user_action in ["L", "LIST"]:
        runList()
    
    elif user_action in ["S", "SET", "SETTINGS"]:
        runSet()
        
    elif user_action in ["Q", "QUIT"]:
        are_you_sure = 0
        while True:
            print("Are you sure you want to quit? (Y/N)")
            are_you_sure = input().upper()
            if are_you_sure in ["Y", "YES"]:
                print("See you again!")
                print("Closing program . . .")
                quit = True
                closeProgram()
                break
            elif are_you_sure in ["N", "NO"]:
                break
            else:
                print("Invalid response, try again")
        if are_you_sure == "Y":
            break
        
    else:
        print("Invalid response, try again")


# In[23]:


# DEBUG - delete and reset blacklist file
#blackfile = open("blacklist.txt", "w")
#blackfile.write("#")
#blackfile.close()


# In[ ]:




