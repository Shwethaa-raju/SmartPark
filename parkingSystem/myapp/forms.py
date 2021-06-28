from django import forms

class loginForm(forms.Form):
    Email_ID = forms.CharField()
    password = forms.CharField()

class adminLoginForm(forms.Form):
    password = forms.CharField()

class signUpForm(forms.Form):
    License_No = forms.CharField()
    First_Name = forms.CharField()
    Last_Name = forms.CharField()
    Email_ID = forms.CharField()
    Contact_No = forms.CharField()
    password = forms.CharField()
    password_validation = forms.CharField()

class parkForm(forms.Form):
    Slot_Id = forms.IntegerField()
    Depart_Date_Time = forms.TimeField()
    VR_No = forms.CharField()

class vacateForm(forms.Form):
    vacate_Slot_Id=forms.IntegerField()

class forceVacateForm(forms.Form):
    vacate_Slot_Id=forms.IntegerField()
    Park_Id = forms.IntegerField()

class extendDurationForm(forms.Form):
    Slot_Id = forms.IntegerField()
    extendDur = forms.IntegerField()

class contactForm(forms.Form):
    Email_ID = forms.CharField()
    Contact_No = forms.CharField()
