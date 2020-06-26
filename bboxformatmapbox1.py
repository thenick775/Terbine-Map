#!/usr/bin/env python
# coding: utf-8

#This script is designed to do some quick formatting
#of lat/lon points into formatted point strings compatible
#with a vector format compatible with plotly

import pandas as pd
import numpy as np

def sepcoordbboxpoly():
    df=pd.read_csv('latlondat.txt',dtype=str,encoding="ISO-8859-1")
    seplatlon(df)
    sepbboxpoly(df)

def seplatlon(df):
    df2=df[~df['lat'].str.contains("Points",na=False)].copy()#.to_csv('latlondatloc.csv',index=None)	
    df2=df2[df2['lat'].notnull()]
    df2['optrad'].fillna(0, inplace=True)
    df2['date'] = pd.to_datetime(df.date)
    df2=df2.drop_duplicates(subset=['lat','lon'], keep="first")#added for month visualization
    df2=df2.sort_values(by='date')
    df2.to_csv('latlondatloc.csv',index=None)

def sepbboxpoly(df):
    df3=df[df['lat'].str.contains("Points",na=False)].copy()
    df3.to_csv('latlonbbox.csv',index=None)

def bboxtovec(stri):
    theveclon=[]
    theveclat=[]
    afterarrs=[]
    arrs=stri.split('|')
    for stri1 in arrs:
        stri1=stri1.replace(")","")
        stri1=stri1.replace("(","")
        indiv=stri1.split(",")#indiv is alternating lat then lon
        afterarrs.append(indiv[0])
    #regroup
    t1=afterarrs[0:2]
    t2=afterarrs[2:4]
    afterarrs[0]=t1
    afterarrs[1]=t2
    #check for invalid points, first by points themselves, then by bbox dimensions (small height&large width->invalid)
    if (float(afterarrs[0][0])>90.0 or float(afterarrs[0][0])<-90.0) or (float(afterarrs[0][1])>180.0 or float(afterarrs[0][1])<-180.0) or (float(afterarrs[1][0])>90.0 or float(afterarrs[1][0])<-90.0) or (float(afterarrs[1][1])>180.0 or float(afterarrs[1][1])<-180.0):
        return "BAD POINT"
    elif abs(float(afterarrs[0][0])-float(afterarrs[1][0]))<5 and abs(float(afterarrs[0][1])-float(afterarrs[1][1]))>140:
        return "BAD POINT"

    #here we begin 4 point cases, 2 points->point vectors depending on order of points given
    if afterarrs[0][0] < afterarrs[1][0] and afterarrs[0][1] < afterarrs[1][1]:
        theveclon=[afterarrs[0][1],afterarrs[0][1],afterarrs[1][1],afterarrs[1][1]]
        theveclat=[afterarrs[0][0],afterarrs[1][0],afterarrs[1][0],afterarrs[0][0]]
    elif afterarrs[0][0] > afterarrs[1][0] and afterarrs[0][1] < afterarrs[1][1]:
        theveclon=[afterarrs[0][1],afterarrs[1][1],afterarrs[1][1],afterarrs[0][1]]
        theveclat=[afterarrs[0][0],afterarrs[0][0],afterarrs[1][0],afterarrs[1][0]]
    elif afterarrs[0][0] > afterarrs[1][0] and afterarrs[0][1] > afterarrs[1][1]:
        theveclon=[afterarrs[1][1],afterarrs[1][1],afterarrs[0][1],afterarrs[0][1]]
        theveclat=[afterarrs[1][0],afterarrs[0][0],afterarrs[0][0],afterarrs[1][0]]
    elif afterarrs[0][0] < afterarrs[1][0] and afterarrs[0][1] > afterarrs[1][1]:
        theveclon=[afterarrs[1][1],afterarrs[0][1],afterarrs[0][1],afterarrs[1][1]]
        theveclat=[afterarrs[1][0],afterarrs[1][0],afterarrs[0][0],afterarrs[0][0]]    
    
    return [theveclon,theveclat]

def polytovec(stri):
    #print("stri= '"+stri+"'")
    theveclon=[]
    theveclat=[]
    afterarrs=[]
    arrs=stri.split('|')
    for count, stri1 in enumerate(arrs):
        stri1=stri1.replace(")","")
        stri1=stri1.replace("(","")
        indiv=stri1.split(",")#indiv[0] is lat, indiv[1] is lon
        #print(indiv)
        #afterarrs.append(indiv)
        if count%2==0: #modified here since we sep by ',' now, so can add points to path in alternating fashion
            theveclat.append(indiv)
        else:
            theveclon.append(indiv)
        #print('\n')
    #print(afterarrs)
    
    #for subarr in afterarrs:
    #    theveclat.append(subarr[0])
    #    theveclon.append(subarr[1])
    
    #print('theveclat=')
    #print(theveclat)
    #print('theveclon=')
    #print(theveclon)
    return [theveclon,theveclat]

#driver code to format polygon and bounding box coordinates, while leaving original data intact
def driver():
    sepcoordbboxpoly()
    df=pd.read_csv("latlonbbox.csv",usecols=["date","name","lat"])

    df.columns=["Date","Name","Points"]

    df['FormatLat'] = pd.Series(index=df.index,dtype=str)
    df['IsBBOX'] = pd.Series(index=df.index,dtype=bool)
    df['LatVec'] = pd.Series(index=df.index,dtype=object)
    df['LonVec'] = pd.Series(index=df.index,dtype=object)

    for count,pstrall in enumerate(df["Points"]):
        arr=[]
        pstrall=pstrall.replace("Points:","")
        pstrdat=pstrall.split(",")
        for stri in pstrdat:
            arr.append(stri)
        if len(arr)>4:
            df.loc[count,'IsBBOX']=False
        elif len(arr)<=4:
            df.loc[count,'IsBBOX']=True
        strf='|'.join(arr)
        df.loc[count,'FormatLat']=strf

    dfbbox=df[df['IsBBOX']==True].reset_index()

    for i in range(0,len(dfbbox.index)):
        retv=bboxtovec(dfbbox["FormatLat"][i])
        if retv=="BAD POINT":
            print("**found bad point**")
            dfbbox["LatVec"][i]=retv
            continue
        dfbbox.at[i,"LatVec"]=retv[1]
        dfbbox.at[i,"LonVec"]=retv[0]

    #get rid of bad points, and delete them by row indexes from dataFrame
    indexNames = dfbbox[ dfbbox['LatVec'] == "BAD POINT" ].index
    dfbbox.drop(indexNames, inplace=True)

    dfbbox2=dfbbox.drop_duplicates(subset=["FormatLat"],keep='first')
    dfbbox2.reset_index(inplace=True)
    st2=dfbbox2.to_csv(index=None).replace("[","").replace("]","").replace("'","")
    with open("latlonbboxwvecreduced.csv","w") as f:
        f.write(st2)
    
    dfpoly=df[df['IsBBOX']==False].reset_index()
    for i in range(0,len(dfpoly.index)):
        retv=polytovec(dfpoly["FormatLat"][i])
        dfpoly.at[i,"LatVec"]=retv[1]
        dfpoly.at[i,"LonVec"]=retv[0]

    dfpoly2=dfpoly.drop_duplicates(subset=["FormatLat"],keep='first')
    dfpoly2=dfpoly2.reset_index()

    st3=dfpoly2.to_csv(index=None).replace("[","").replace("]","").replace("'","")
    with open("latlonpolywvecreduced.csv","w") as f:
        f.write(st3)

if __name__== "__main__":
    driver()

