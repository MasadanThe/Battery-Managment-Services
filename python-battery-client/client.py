import json
import requests
import time
import math
import matplotlib.pyplot as plt
import numpy as np

url="http://127.0.0.1:5000"
price = ""
baseLoad = ""
ev_batt_max_capacity=46.3

#Get price
response = requests.get(url + "/priceperhour")
if response.status_code == 200:
    price = json.loads(response.text)
    print(price)
else:
    print("Error retrieving data, status code:", response.status_code)


#Get base load
response = requests.get(url + "/baseload")
if response.status_code == 200:
    baseLoad = json.loads(response.text)
    print(baseLoad)
else:
    print("Error retrieving data, status code:", response.status_code)
    
    
def startCharge():
    
    payload = {'charging': 'on'}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url + "/charge", data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(result)

def stopCharge():
    payload = {'charging': 'off'}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url + "/charge", data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(result)


def restart():
    payload = {'discharging': 'on'}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url + "/discharge", data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(result)

def getInfo():
    response = requests.get(url + "/info")
    if response.status_code == 200:
        info = json.loads(response.text)
        print(info)
        return info
    else:
        print("Error retrieving data, status code:", response.status_code)

def firstAssignment():
    chargeDuringHours = []
    
    #Calculate how many hours the car needs to charge, rounded up
    hoursNeededToCharge =  (math.ceil((ev_batt_max_capacity * 0.8 - ev_batt_max_capacity * 0.2) / 7.3)) + 1
    print(hoursNeededToCharge)
    
    baseLoadAscending = []
    
    #If the load doesn't exceed 11 kWh, add to the list
    for i in range(len(price)):
        if baseLoad[i] + 7.3 <= 11:
            baseLoadAscending.append(baseLoad[i])

    #Sort and remove all the hours not needed to charge
    baseLoadAscending.sort()
    baseLoadAscending = baseLoadAscending[:hoursNeededToCharge]
    
    print(baseLoadAscending)
    print(baseLoad)
    
    houresToCharge= []
    #Put charge hours in hoursToCharge
    for i in range(len(baseLoad)):
        if baseLoad[i] in baseLoadAscending:
            houresToCharge.append(i)
    print(houresToCharge)    
        
    restart()
    charging = False
    for i in range(192):
        info = getInfo()
        
        #If it is the next day break and stopCharge()
        if int(info["sim_time_hour"]) == 0 and i > 10:
            stopCharge()
            break
        
        #If we haven't added to chargeDuringHours, append else modify
        if len(chargeDuringHours) < info["sim_time_hour"] + 1:
            chargeDuringHours.append(info["base_current_load"])
        else:
            if info["base_current_load"] > chargeDuringHours[info["sim_time_hour"]]:
                chargeDuringHours[info["sim_time_hour"]] = info["base_current_load"]
            
        #If we have charged the battery to 80% or more, stop charging
        if info["battery_capacity_kWh"] >= ev_batt_max_capacity * 0.8:
            if charging:
                    stopCharge()
                    charging = False
        else:
            #If it is time to charge
            if info["sim_time_hour"] in houresToCharge:
                if not charging:
                    startCharge()
                    charging = True
            else:
                if charging:
                    stopCharge()
                    charging = False
        time.sleep(0.5)
    
    return chargeDuringHours

def secondAssignment():
    chargeDuringHours = []
    
    #Calculate how many hours the car needs to charge, rounded up
    hoursNeededToCharge =  (math.ceil((ev_batt_max_capacity * 0.8 - ev_batt_max_capacity * 0.2) / 7.3)) + 1
    print(hoursNeededToCharge)
    
    priceList = []
    
    #If the load doesn't exceed 11 kWh, add to the list
    for i in range(len(price)):
        if baseLoad[i] + 7.3 <= 11:
            priceList.append(price[i])
    
    #Sort and remove all the hours not needed to charge
    priceList.sort()
    priceList = priceList[:hoursNeededToCharge]
    
    houresToCharge= []
    #Put charge hours in hoursToCharge
    for i in range(len(price)):
        if price[i] in priceList:
            houresToCharge.append(i)
    print(houresToCharge)    
        
    restart()
    charging = False
    for i in range(192):
        info = getInfo()
        
        #If it is the next day break and stopCharge()
        if int(info["sim_time_hour"]) == 0 and i > 10:
            stopCharge()
            break
        
        #If we haven't added to chargeDuringHours, append else modify
        if len(chargeDuringHours) < info["sim_time_hour"] + 1:
            chargeDuringHours.append(info["base_current_load"])
        else:
            if info["base_current_load"] > chargeDuringHours[info["sim_time_hour"]]:
                chargeDuringHours[info["sim_time_hour"]] = info["base_current_load"]
            
        #If we have charged the battery to 80% or more, stop charging
        if info["battery_capacity_kWh"] >= ev_batt_max_capacity * 0.8:
            if charging:
                stopCharge()
                charging = False
        else:
            #If it is time to charge
            if info["sim_time_hour"] in houresToCharge:
                if not charging:
                    startCharge()
                    charging = True
            else:
                if charging:
                    stopCharge()
                    charging = False
        time.sleep(0.5)
    
    return chargeDuringHours
    
#stopCharge()
#getInfo()
firstX = firstAssignment()
secondX = secondAssignment()


plt.figure(1)
plt.title("Assignment 1")
plt.plot(firstX, label='current load')
plt.plot(baseLoad, label='base load')

plt.figure(2)
plt.title("Assignment 2")
plt.plot(secondX, label='current load')
plt.plot(baseLoad, label='base load')

plt.figure(3)
plt.title("Assignment 2")
plt.plot(price, label='price')

plt.show()