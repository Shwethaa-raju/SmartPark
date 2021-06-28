from django.shortcuts import render
from django.http import HttpResponse
from myapp.models import driver,slot,park
from myapp.forms import signUpForm,loginForm,parkForm,vacateForm,contactForm,extendDurationForm,adminLoginForm,forceVacateForm
from django.shortcuts import redirect
import json
from time import gmtime, strftime,strptime
import re

from datetime import datetime,timedelta
from django.contrib import messages
from django.utils.timezone import make_aware
from django.core.mail import send_mail
import threading
import time
from django.utils import timezone
import warnings
warnings.filterwarnings("ignore")

def main(request):
    if request.session['UserLogin'] == 1:
        #slot_details = slot.objects.raw("SELECT * FROM myapp_slot left join myapp_park on my_app.Slot_Id=myapp_park.Slot_Id_id ORDER BY Slot_Id")
        slot_details = slot.objects.raw("SELECT myapp_slot.Slot_Id,myapp_slot.Occupancy,myapp_slot.directions,myapp_slot.LatLon,table2.Depart_Date_Time from myapp_slot left join (select Slot_Id_id,Depart_Date_Time from myapp_park where typeof(Actual_Depart_Date_Time)='null' ) as table2 on myapp_slot.Slot_Id = table2.Slot_Id_id" )

        vacant_spots = park.objects.raw("select Park_Id,Slot_Id_id from myapp_park where License_No=%s AND typeof(Actual_Depart_Date_Time) = 'null' ORDER BY Slot_Id_id",[request.session['License_No']])
        vacateSpotList= []
        for i in vacant_spots:
            vacateSpotList.append(i.Slot_Id_id)

        if request.method=="POST":
            formName=request.POST.get('formType')
            if formName == "booking":
                form = parkForm(request.POST)
                if form.is_valid():
                    validParking = 0
                    Slot_Id = form.cleaned_data['Slot_Id']
                    VR_No = form.cleaned_data['VR_No']
                    Depart_Date_Time = form.cleaned_data['Depart_Date_Time']
                    timeNow = datetime.now()
                    date = datetime.now().date()
                    datetime1 = datetime.combine(date, Depart_Date_Time)
                    Duration = datetime1-timeNow
                    amount = int(Duration.seconds/3600*100)
                    #print(Duration)
                    #print(Duration.days)
                    temp = park.objects.raw("SELECT Park_Id,count(*) as count from myapp_park where VR_No=%s and typeof(Actual_Depart_Date_Time) = 'null'",[VR_No])
                    count = 0
                    for i in temp:
                        count = i.count
                    if count==0 and Duration.days!=-1 and (Duration.seconds)>=1800:    #greater than 30 mins
                        validParking = 1
                        dummy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        dummy2 = datetime1.strftime("%Y-%m-%d %H:%M:%S")
                        #print(Duration.seconds)
                        obj = park(License_No=request.session['License_No'], Slot_Id_id=Slot_Id, VR_No=VR_No, Entry_Date_Time=dummy, Depart_Date_Time=dummy2,Amount_Paid=int(Duration.seconds/3600*100) )
                        obj.save()
                        obj1 = slot.objects.get(pk=Slot_Id)
                        obj1.Occupancy = True
                        obj1.save()
                        slot_details = slot.objects.raw("SELECT * FROM myapp_slot ORDER BY Slot_Id")
                        vacant_spots = park.objects.raw("select Park_Id,Slot_Id_id from myapp_park where License_No=%s AND typeof(Actual_Depart_Date_Time) = 'null' ORDER BY Slot_Id_id",[request.session['License_No']])
                        vacateSpotList= []
                        for i in vacant_spots:
                            vacateSpotList.append(i.Slot_Id_id)
                    else:
                        validParking = 0
                    return render(request,"main.html",{"slot_details":slot_details,"vacateSpotList":vacateSpotList,"validParking":validParking,"Slot_Id":Slot_Id,"amount":amount})
                else:
                    message = "Invalid data"
                    return render(request, "main.html",{"slot_details":slot_details,"message":message,"vacateSpotList":vacateSpotList})
            elif formName == "vacate":
                form=vacateForm(request.POST)
                if form.is_valid():
                    vacate_Slot_Id=form.cleaned_data['vacate_Slot_Id']
                    timeNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    park_details=park.objects.raw("select Park_Id,Depart_Date_Time from myapp_park where License_No=%s and Slot_Id_id=%s and Actual_Depart_Date_Time is null",[request.session['License_No'],vacate_Slot_Id])
                    fare=0
                    for x in park_details:
                        obj=park.objects.get(pk=x.Park_Id)
                        obj.Actual_Depart_Date_Time=timeNow
                        time_delta=datetime.now(timezone.utc)-x.Depart_Date_Time
                        extra_mins=time_delta.total_seconds()/60
                        if extra_mins>0 :
                            obj.Amount_Paid = obj.Amount_Paid+extra_mins*5
                        obj.save()
                    obj1 = slot.objects.get(pk=vacate_Slot_Id)
                    obj1.Occupancy = False
                    obj1.save()
                    slot_details = slot.objects.raw("SELECT * FROM myapp_slot ORDER BY Slot_Id")
                    vacant_spots = park.objects.raw("select Park_Id,Slot_Id_id from myapp_park where License_No=%s AND typeof(Actual_Depart_Date_Time) = 'null' ORDER BY Slot_Id_id",[request.session['License_No']])
                    vacateSpotList= []
                    for i in vacant_spots:
                        vacateSpotList.append(i.Slot_Id_id)
                    return render(request,"main.html",{"slot_details":slot_details,"vacateSpotList":vacateSpotList})
            elif formName == "extendDuration":
                validExtension=0
                form=extendDurationForm(request.POST)
                if form.is_valid():
                    Slot_Id=form.cleaned_data['Slot_Id']
                    extendDur=form.cleaned_data['extendDur']
                    if extendDur>=5:
                        validExtension=1
                        park_details=park.objects.raw("select Park_Id,Depart_Date_Time,Amount_Paid from myapp_park where License_No=%s and Slot_Id_id=%s and Actual_Depart_Date_Time is null",[request.session['License_No'],Slot_Id])
                        for x in park_details:
                            obj=park.objects.get(pk=x.Park_Id)
                            #print(obj.Depart_Date_Time)
                            obj.Depart_Date_Time = obj.Depart_Date_Time+timedelta(minutes = extendDur)
                            obj.Amount_Paid = obj.Amount_Paid+extendDur
                            obj.save()
                    else:
                        validExtension=0
                    return render(request,"main.html",{"slot_details":slot_details,"vacateSpotList":vacateSpotList,"validExtension":validExtension,"Slot_Id":Slot_Id})
        else:   #GET METHOD
            return render(request,"main.html",{"slot_details":slot_details,"vacateSpotList":vacateSpotList})
    else:
        return redirect('/')

def adminMain(request):
    if request.session['AdminLogin'] == 1:
        slot_details = slot.objects.raw("SELECT myapp_slot.Slot_Id,table2.Park_Id,myapp_slot.Occupancy,table2.Depart_Date_Time,table2.License_No,table2.First_Name,table2.Last_Name,table2.Contact_No from myapp_slot left join (select myapp_park.Slot_Id_id,myapp_park.Park_Id,myapp_park.Depart_Date_Time,myapp_park.License_No,myapp_driver.First_Name,myapp_driver.Last_Name,myapp_driver.Contact_No from myapp_park,myapp_driver where typeof(myapp_park.Actual_Depart_Date_Time)='null' and myapp_driver.License_No=myapp_park.License_No) as table2 on myapp_slot.Slot_Id = table2.Slot_Id_id")

        if request.method=="POST":
            formName=request.POST.get('formType')
            if formName == "forceVacate":
                form=forceVacateForm(request.POST)
                if form.is_valid():
                    vacate_Slot_Id=form.cleaned_data['vacate_Slot_Id']
                    Park_Id = form.cleaned_data['Park_Id']
                    timeNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    obj=park.objects.get(pk=Park_Id)
                    obj.Actual_Depart_Date_Time=timeNow
                    time_delta=datetime.now(timezone.utc)-obj.Depart_Date_Time
                    extra_mins=time_delta.total_seconds()/60
                    if extra_mins>0 :
                        obj.Amount_Paid = obj.Amount_Paid+extra_mins*5
                    obj.save()

                    obj1 = slot.objects.get(pk=vacate_Slot_Id)
                    obj1.Occupancy = False
                    obj1.save()
                    slot_details = slot.objects.raw("SELECT myapp_slot.Slot_Id,table2.Park_Id,myapp_slot.Occupancy,table2.Depart_Date_Time,table2.License_No,table2.First_Name,table2.Last_Name,table2.Contact_No from myapp_slot left join (select myapp_park.Slot_Id_id,myapp_park.Park_Id,myapp_park.Depart_Date_Time,myapp_park.License_No,myapp_driver.First_Name,myapp_driver.Last_Name,myapp_driver.Contact_No from myapp_park,myapp_driver where typeof(myapp_park.Actual_Depart_Date_Time)='null' and myapp_driver.License_No=myapp_park.License_No) as table2 on myapp_slot.Slot_Id = table2.Slot_Id_id")
                    return render(request,"adminMain.html",{"slot_details":slot_details})
        else:
            return render(request,"adminMain.html",{"slot_details":slot_details})
    else:
        return redirect('/adminLogin')


def userLogin(request):
    vacancy_details=slot.objects.raw("select Slot_Id,count(*) as TotalSlots,sum(case Occupancy when True then 1 else 0 end) as OccupiedSlots,sum(case Occupancy when False then 1 else 0 end) as VacantSlots from myapp_slot")
    if request.method=="POST":
        form = loginForm(request.POST)
        if form.is_valid():
            Email_ID = form.cleaned_data['Email_ID']
            password = form.cleaned_data['password']
            recordSet = driver.objects.raw("SELECT * FROM myapp_driver WHERE Email_ID=%s AND password=%s",[Email_ID,password])
            if len(list(recordSet))>0:
                for x in recordSet:
                    request.session['License_No']=x.License_No
                request.session['UserLogin']=1
                return redirect("/main/")
            else:
                message="Either user name or password is incorrect"
                return render(request,"login.html",{'form':form,"message":message,'vacancy_details':vacancy_details})
        else:
            message = "Invalid data"
            return render(request, "login.html",{'form':form,"message":message,'vacancy_details':vacancy_details})
    else:
        request.session['UserLogin']=0
        form = loginForm()
        return render(request,"login.html",{'form':form,'vacancy_details':vacancy_details})

def adminLogin(request):
    vacancy_details=slot.objects.raw("select Slot_Id,count(*) as TotalSlots,sum(case Occupancy when True then 1 else 0 end) as OccupiedSlots,sum(case Occupancy when False then 1 else 0 end) as VacantSlots from myapp_slot")
    if request.method=="POST":
        form = adminLoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            recordSet = driver.objects.raw("SELECT * FROM myapp_driver WHERE Email_ID=%s AND password=%s",["iit2019185@iiita.ac.in",password])
            if len(list(recordSet))>0:
                for x in recordSet:
                    request.session['License_No']=x.License_No
                request.session['AdminLogin']=1
                return redirect("/adminMain/")
            else:
                message="Either user name or password is incorrect"
                return render(request,"adminLogin.html",{'form':form,"message":message,'vacancy_details':vacancy_details})
        else:
            message = "Invalid data"
            return render(request, "adminLogin.html",{'form':form,"message":message,'vacancy_details':vacancy_details})
    else:
        request.session['AdminLogin']=0
        form = loginForm()
        return render(request,"adminLogin.html",{'form':form,'vacancy_details':vacancy_details})

def signUp(request):
    vacancy_details=slot.objects.raw("select Slot_Id,count(*) as TotalSlots,sum(case Occupancy when True then 1 else 0 end) as OccupiedSlots,sum(case Occupancy when False then 1 else 0 end) as VacantSlots from myapp_slot")
    if request.method=="POST":
        form = signUpForm(request.POST)
        if form.is_valid():
            License_No = form.cleaned_data['License_No']
            First_Name = form.cleaned_data['First_Name']
            Last_Name =form.cleaned_data['Last_Name']
            Email_ID = form.cleaned_data['Email_ID']
            Contact_No = form.cleaned_data['Contact_No']
            password = form.cleaned_data['password']
            password_validation = form.cleaned_data['password_validation']


            recordSet = driver.objects.raw("SELECT * FROM myapp_driver WHERE Email_ID=%s OR License_No=%s",[Email_ID,License_No])
            flag = 1
            if len(License_No)==15 and License_No[0].isalpha() and License_No[1].isalpha():
                for i in License_No[2:]:
                    if (i.isdigit()):
                        flag=1
                    else:
                        flag=0
            else:
                flag=0

            if re.search(r'\d', First_Name) != None or re.search(r'\d', Last_Name) != None or len(Contact_No)<10 or Contact_No<str(6000000000) or flag==0  :
                #print(flag)
                #print("PHone validation")
                message = "Ensure that name doesnt contain any digits, phone number is valid and license number is of the format AA1212341234567"
            else:
                if len(list(recordSet))==0:
                    if password==password_validation:
                        signUpRecord = driver(License_No=License_No,First_Name=First_Name,Last_Name=Last_Name,Email_ID=Email_ID,Contact_No=Contact_No,password=password)
                        signUpRecord.save()
                        request.session['License_No']=License_No
                        return redirect("/main/")
                    else:
                        message = "Password & confirm Password mismatch"
                        return render(request,"signUp.html",{'form':form,"message":message,'vacancy_details':vacancy_details})
                else:
                    message = "This username already exists"
            return render(request,"signUp.html",{'form':form,"message":message,'vacancy_details':vacancy_details})

        else:
            message = "Invalid data"
            return render(request, "signUp.html",{'form':form,"message":message,'vacancy_details':vacancy_details})
    else:
        form = signUpForm()
        return render(request, "signUp.html",{'form':form,'vacancy_details':vacancy_details})

def logout(request):
    request.session['UserLogin']=0
    request.session['AdminLogin']=0
    try:
        del request.session['License_No']
    except:
        return redirect("/")
    return redirect("/")

def profile(request):
    if request.session['UserLogin'] == 1:
        details = driver.objects.raw('SELECT * from myapp_driver where License_No=%s',[request.session['License_No']])
        detailsDict = {}
        detailsDict["License_No"]=[]
        detailsDict["First_Name"]=[]
        detailsDict["Last_Name"]=[]
        detailsDict["Email_ID"]=[]
        detailsDict["Contact_No"]=[]
        for i in details:
            detailsDict["License_No"].append(i.License_No)
            detailsDict["First_Name"].append(i.First_Name)
            detailsDict["Last_Name"].append(i.Last_Name)
            detailsDict["Email_ID"].append(i.Email_ID)
            detailsDict["Contact_No"].append(i.Contact_No)

        return render(request,"profile.html",{"details":detailsDict})
    else:
        return redirect('/')

def history(request):
    if request.session['UserLogin'] == 1:
        history_details = park.objects.raw("SELECT * from myapp_park where License_No=%s",[request.session['License_No'] ])
        license = request.session['License_No']
        history_details_list=[]
        flag=0
        for i in history_details:
            flag=1
            temp =[]
            temp.append(i.VR_No)
            temp.append(i.Slot_Id_id)
            temp.append(i.Entry_Date_Time)
            temp.append(i.Actual_Depart_Date_Time)
            temp.append(i.Amount_Paid)
            history_details_list.append(temp.copy())
        return render(request,"history.html",{"license":license,"history_details":history_details_list,"flag":flag})
    else:
        return redirect('/')

def historyAdmin(request):
    if request.session['AdminLogin'] == 1:
        history_details = park.objects.raw("SELECT * from myapp_park order by Actual_Depart_Date_Time desc")
        history_details_list=[]
        flag=0
        for i in history_details:
            flag=1
            temp =[]
            temp.append(i.License_No)
            temp.append(i.VR_No)
            temp.append(i.Slot_Id_id)
            temp.append(i.Entry_Date_Time)
            temp.append(i.Actual_Depart_Date_Time)
            temp.append(i.Amount_Paid)
            history_details_list.append(temp.copy())
        return render(request,"historyAdmin.html",{"history_details":history_details_list,"flag":flag})
    else:
        return redirect('/adminLogin')


def contact(request):
    if request.session['UserLogin'] == 1:
        if request.method=="POST":
            formName=request.POST.get('formType')
            if formName == "contact":
                form = contactForm(request.POST)
                if form.is_valid():
                    #here
                    Email_ID_form = form.cleaned_data['Email_ID']
                    Contact_No_form = form.cleaned_data['Contact_No']
                    obj = driver.objects.raw("Select License_No from myapp_driver where License_No=%s",[request.session['License_No']])
                    for x in obj:   #updating the db
                        obj=driver.objects.get(pk=x.License_No)
                        obj.Email_ID=Email_ID_form
                        obj.Contact_No=Contact_No_form
                        obj.save()
                    message = "Contact details updated successfully"
                    return render(request,"contact.html",{"message":message})
                else:
                    message = "invalid Form"
                    return render(request,"contact.html",{'form':form,"message":message})
            elif formName == "CancelContact":
                message = "Contact details were not updated"
                return render(request,"contact.html",{"message":message})
        else:   #get method
            form = contactForm()
            return render(request,"contact.html",{'form':form})
    else:
        return redirect('/')


def notifyuser(emailid,parkId):
    subject ='Vacate Parking Spot'
    if parkId!=0:
        msg = 'Parking Id '+str(parkId)+' has exceeded its time limit'
    else:
        msg= 'Times up! Kindly vacate the parking Spot or Request extension'
    to =emailid
    res =send_mail(subject,msg,"iit2019185@iiita.ac.in",[to])
    if(res==1):
        print('eMail success')
    else:
        print('eMail failure')

def checkin():
    infolists = park.objects.raw("Select License_No,Depart_Date_Time,Park_Id from myapp_park where typeof(Actual_Depart_Date_Time)='null' ")

    for i in infolists:
        ltime=i.Depart_Date_Time
        print('Server checkin website')
        print("Leaving time",end=' ')
        print(ltime)
        print("Time now",end=' ')
        print(make_aware(datetime.now()))
        nowtime=make_aware(datetime.now())
        tdiff=(ltime-nowtime).total_seconds()/60.0
        #print(nowtime+timedelta(minutes=tdiff)) # just to check time converts from utc to ist correctly
        print("Time difference",end=' ')
        print(tdiff,end='\n\n')
        if tdiff>0 and tdiff < 10 :
            #user has less than 10 minutes left
            print("under 10 minutes")
            emailId = driver.objects.raw("select License_No,Email_ID from myapp_driver where License_No=%s",[i.License_No])
            for j in emailId:
                print("Email sent to",end=' ')
                print(j.Email_ID)
                notifyuser(j.Email_ID,0)
        elif tdiff < 0 and tdiff > -20 :
            #user hasn't vacated yet. inform admin.
            print("complain sent to admin")
            #send a mail to admin
            notifyuser("iit2019133@iiita.ac.in",i.Park_Id)

def checker():
    while True:
        checkin()
        time.sleep(300)

threading.Thread(target=checker,daemon=True).start() #just one extra thread to handle scheduled checkup of expiry timings
