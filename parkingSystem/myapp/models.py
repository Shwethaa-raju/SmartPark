from django.db import models

class driver(models.Model):
    License_No = models.CharField(max_length=20,primary_key=True)
    First_Name = models.CharField(max_length=25)
    Last_Name = models.CharField(max_length=25)
    Email_ID = models.CharField(max_length=50)
    Contact_No = models.CharField(max_length=10)
    password = models.CharField(max_length=20)
    def __str__(self):
        return self.First_Name

class park(models.Model):
    class meta:
        db_table="park"
    Park_Id = models.AutoField(primary_key=True)
    Slot_Id = models.ForeignKey('slot', on_delete=models.CASCADE)
    License_No = models.CharField(max_length=20)
    VR_No = models.CharField(max_length=20)
    Entry_Date_Time = models.DateTimeField()
    Depart_Date_Time = models.DateTimeField()
    Actual_Depart_Date_Time = models.DateTimeField(blank =True,null=True)
    Amount_Paid = models.IntegerField()

class slot(models.Model):
    class meta:
        db_table="slot"
    Slot_Id =  models.IntegerField(primary_key=True)
    Occupancy = models.BooleanField()
    directions = models.CharField(max_length=1000)
    LatLon = models.CharField(max_length=1000)
