import blescan
import pymysql
import pandas as pd
from pandas import DataFrame as df
import os
import math
import socket
import sys
import bluetooth._bluetooth as bluez
from numpy import median

beacon1="e1c56db5dffb48d2b060d0f5a71096e0"
beacon2="e2c56db5dffb48d2b060d0f5a71096e0"
beacon3="e3c56db5dffb48d2b060d0f5a71096e0"
dev_id=0
count=0

position1=[45,90,0]
position2=[0,0,0]
position3=[90,0,0]

def push(element):
    global top
    top=top+1
    stack[top]=element

def pop():
    global top
    ret=stack[top]
    top=top-1
    return ret

def show():
    global top
    global mincorner
    global mincorv
    for i in range(0,top+1):
        mincorv+=" ->"+stack[i][0]

def getDistance(a,b):
    return math.sqrt((a[1]-b[1])*(a[1]-b[1])+(a[2]-b[2])*(a[2]-b[2]))

def TSP(start, corner, number, sumv, now):
    global minv
    global totalCount
    global mincorner
    global mincorv
    count=0
    visited[start]=1
    for i in range(0,number):
        if visited[i]== 0:
            count=count+1
            visited[i]=1
            push(corner[i])
            TSP(start,corner, number,sumv+getDistance(corner[now], corner[i]),i)
            visited[i]=0
            pop()
            
    if count == 0:
        mincorv=mincorv+"->"+corner[start][0]
        sumv=sumv+getDistance(corner[now], corner[start])
        show()
        mincorv+="\nDistance: "+ str(sumv)
        mincorner.append(mincorv)
        mincorv=""
        if minv>sumv:
            minv=sumv

        totalCount=totalCount+1

def getTrilateration(position1, position2, position3):
    x1=position1[0]
    y1=position1[1]
    r1=position1[2]
    x2=position2[0]
    y2=position2[1]
    r2=position2[2]
    x3=position3[0]
    y3=position3[1]
    r3=position3[2]

    S=(math.pow(x3,2.0)-math.pow(x2,2.0)+math.pow(y3,2.0)-math.pow(y2,2.0)+math.pow(r2,2.0)-math.pow(r3,2.0))/2.0
    T=(math.pow(x1,2.0)-math.pow(x2,2.0)+math.pow(y1,2.0)-math.pow(y2,2.0)+math.pow(r2,2.0)-math.pow(r1,2.0))/2.0

    y=((T*(x2-x3))-(S*(x2-x1)))/(((y1-y2)*(x2-x3))-((y3-y2)*(x2-x1)))
    x=((y*(y1-y2))-T)/(x2-x1)

    return x,y

#Initialization DataBase
stack=[0 for i in range(5)]
top = -1
corner=[("Enter", 75.1, 53.3),
        ("Dressed meat", 0.0, 5.1), ("Vegetable", 0.0, 10.2), ("Seafood", 0.0, 15.3), ("Fruit", 15.7, 19.1),
        ("Toy", 5.0, 5.5), ("Beverage", 5.0, 10.6), ("Home appliance", 28.7, 41.8), ("Kitchenware", 5.0, 20.8),
        ("Bathroom", 10.0, 5.9), ("Snack", 10.0, 10.0), ("Instant noodles", 40.9, 38.3), ("Egg", 10.0, 20.2),
        ("Diary products", 44.6, 24.6), ("Frozen food", 52.2, 59.6), ("Clothing", 15.0, 15.5), ("Shoes", 15.0, 20.6),
        ("Tool", 20.0, 5.7), ("Electronics", 20.0, 10.8), ("Pet goods", 20.0, 15.9), ("Beer", 20.0, 20.0)]
mincorner=[]
mincorv=""
visited=[0 for i in range(5)]
minv=2147483647.0
totalCount=0

try:
    sock = bluez.hci_open_dev(dev_id)
    print "ble thread started"

except:
    print "error accessing bluetooth device..."
    #sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

conn = pymysql.connect(host='localhost', user='yang', passwd='1', db='goods',charset='utf8mb4')
cur = conn.cursor()
DT = df({'Goods List': [],'Number of':[]});
pd.options.display.float_format='{:,.0f}'.format


#Initialization Socket
PORT=8888
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

distance_avg=[]
while True:
    returnedList = blescan.parse_events(sock, 10)
    print "Select the Mode(0:Short Path, 1:Scan barcode, Exit is any Number): ",
    mode=int(input())
    if mode==0:
        #print corner number
        print "1.Dressed meat     2.Vegetable     3.Seafood           4.Fruit"
        print "5.Toy              6.Beverage      7.Home appliances   8.Kitchenware"
        print "9.Bathroom         10.Snack        11.Instant noodles  12.Dairy product"
        print "13.Egg             14.Frozen food  15.Clothing         16.Shoes"
        print "17.Tool            18.Electronics  19.Pet goods        20.Beer"
        
        print "\nSelec the Corner: ",
        num=(input()).split()
        flag=[0 for i in range(21)]
        vis=[0 for i in range(len(num))]
        #print corner map
        print "===================================================================="
        for j in range(0,len(num)):
                flag[int(num[j])]=1
                vis[j]=corner[int(num[j])]

        for i in range(1,21):
            if flag[i] == 1:
                print corner[i][0],
                for j in range(0,16-len(corner[i][0])):
                    print " ",
            else:
                print "                ",

            if i%4==0 and i!=0:
                print "\n"

        print "                               ",
        print corner[0][0]
        print "====================================================================\n"
        for beacon in returnedList:
            if beacon[18:18+len(beacon3)]==beacon1:
                distance_avg.insert(count,(10**((float(beacon[61:64])-(float(beacon[65:])))/20.0))*100)
                count=count+1
                if count == 10:
                    if median(distance_avg)<1:
                        position1[2]=median(distance_avg)
                        count=0
                        del distance_avg[:]

            if beacon[18:18+len(beacon3)]==beacon2:
                distance_avg.insert(count,(10**((float(beacon[61:64])-(float(beacon[65:])))/20.0))*100)
                count=count+1
                if count == 10:
                    if median(distance_avg)<1:
                        position2[2]=median(distance_avg)
                        count=0
                        del distance_avg[:]
            
            if beacon[18:18+len(beacon3)]==beacon3:
                distance_avg.insert(count,(10**((float(beacon[61:64])-(float(beacon[65:])))/20.0))*100)
                count=count+1
                if count == 10:
                    if median(distance_avg)<1:
                        position3[2]=median(distance_avg)
                        count=0
                        del distance_avg[:]

            if beacon[18:18+len(beacon3)]==beacon3 and beacon[18:18+len(beacon3)]==beacon2 and beacon[18:18+len(beacon3)]==beacon1:
                X,Y=getTrilateration(position1,position2,position3)
                #find current location
                for i in range(0,21):
                    if abs(X-coner[i][1])<1 and abs(Y-coner[i][2])<1:
                        myplace=i

        #print short path
        TSP(i,vis,len(vis),0,0)
        print "Total Path Num: ",totalCount
        for i in range(0,len(mincorner)):
            if mincorner[i].find(str(minv)) != -1:
                n=i
        print "Shortest Path: ",mincorner[n]
        print "\n"
        mincorner=["" for i in range(len(mincorner))]
        minv=2147483647
        

    elif mode==1:
         while True:
            print "Scan barcode(1:Delete, 2:Pay): ",
            goods_cnt=1
            scan_in,n=[input() for _ in range (2)]
            scan_in.strip('\n\n')
            if scan_in is 'q':
                break
            elif scan_in is '1':
                print "========================================="
                print(DT)
                num=int(input("delete (-1:return):"))
                #while(num==)
                if num== -1:
                    continue
                else:
                    DT.drop(num,inplace=True)
                    DT.reset_index(inplace=True)
                    DT.drop('index', axis=1,inplace=True)
                    print("{0} delete".format(num))
                    print(DT)
            elif scan_in is '2':
                A=[0 for i in range(len(DT))]
                sumf=0
                ip=input("Input IP of App: ")
                s.connect((ip,PORT))
                for i in range(0,len(DT)):
                    A[i]=str(DT.iloc[i]).split(',')
                    #print(A[i][2])
                    B=A[i][3].split('Number of')
                    C=(B[1].replace(" ",""))
                    sumf+=int(A[i][2])*int(C[0])
                    sumf=str(sumf)
                s.send(sumf.encode('utf-8'))
                #msg=s.recv(1024)
                #print(msg.decode('utf-8'))
                s.close()
                break
            
            else:
                sql="SELECT * FROM list WHERE barcode LIKE %s"
                cur.execute(sql,scan_in)
                for row in cur:
                    cp=str(row)
                empty=str(DT[DT['Goods List'].isin([cp])])
                if (empty.find("Empty") is not 0):
                    i=DT[DT['Goods List'].isin([cp])].index
                    num=DT[DT['Goods List']==cp]['Number of'].tolist()
                    num=DT.loc[i,['Number of']]=(num[0]+1)
                else:
                    new_data={'Goods List':cp, 'Number of':goods_cnt}
                    DT=DT.append(new_data, ignore_index=True)
                    text=str(new_data).split(',')
                    text=text[3].replace(')"',"")
                    os.system('echo Event is %s | festival --tts' %text)
                print(DT)
    else:
        break

cur.close()
conn.close()
