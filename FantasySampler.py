import requests
import json
import pprint
import math

gw = input("Select gameweek \n *Note: Sampler works only for past gameweeks since FPL doesn't provide current gw transfers info of users \n")

#first, get the desired number of users' entries, default case menas first two pages of API -> first 100 users in overall standings


data = []
for i in range(1,3):
    response = requests.get(f'https://fantasy.premierleague.com/api/leagues-classic/314/standings/?page_standings={i}')
    response = json.loads(response.text)
    data.append(response)


#we loop through data and append everything under 'results' key into a separate list
#through which we also loop with a double 'for' loop to get each entry of the desired number of users

results = []
for item in data:
    results.append(item['standings']['results'])



userIds=[]
for i in range(len(results)):
    for item in results[i]:
        userIds.append(item['entry'])

#then, we get team data of each entry

teams=[]
for item in userIds:
    response = requests.get(f'https://fantasy.premierleague.com/api/entry/{item}/event/{gw}/picks/')
    response=json.loads(response.text)
    teams.append(response)


#looping through teams will get us all the IDs(elements term use by fpl) of players who appear in our teams

playerIds = []

for item in teams:
    for k in item['picks']:
        playerIds.append(k['element'])

#we then use the setDefault option to loop through the IDs of players ant count them

count = {}
for item in playerIds:
    count.setdefault(item, 0)
    count[item] = count[item] + 1


#now we have the ammount each player appears in the desired number of users' teams, however we only have their IDs
#because the fpl API won't give us info about player's name in the selected player stats:
#https://fantasy.premierleague.com/api/element-summary/{id}, we have to extract them from the link below

response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
response = json.loads(response.text)
elements = response['elements']


#after extracting the info we can get the names by looping through their IDs in our count dict and returning 
#the corresponding name in elements. we loop thorugh the sorted keys so the names will match values when we patch the 
#lists of names and values together in the end

players=[]
for number in sorted(list(count.keys())):
    for item in elements:
        if number == item['id']:
            players.append(item['web_name'])

#we create a sorted count dict

countSorted = dict(sorted(count.items()))

#finally, we merge the sorted count values with the players' names gotten from the same sorted dict

final = dict(zip((players), list(countSorted.values())))

#just a little prettier print, btw. players are sorted by their team name in alphabetical order, with the ones at the bottom being players on loan from abroad

print ("{:<20} {:<8} ".format('\033[1m' +'Name', '\033[1m' + 'SelectedBy'))
for k, v in final.items():
    print ("{:<20} {:<8}".format(k, v))