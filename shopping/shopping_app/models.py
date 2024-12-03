from django.db import models

# Create your models here.
class Login(models.Model):
    username = models.CharField(max_length=250,null=True)
    password = models.CharField(max_length=250,null=True)
    utype = models.CharField(max_length=250, null=True)
    name = models.CharField(max_length=250,null=True)

class Items(models.Model):
    itemname = models.CharField(max_length=250,null=True)
    price = models.FloatField(max_length=250,null=True)
    hsncode = models.IntegerField(null=True)
    gst = models.IntegerField(null=True)
    cgst = models.FloatField(max_length=250,null=True)
    sgst = models.FloatField(max_length=250,null=True)
    discount = models.IntegerField(null=True)
    stock = models.IntegerField(null=True)
    barcode_number = models.CharField(max_length=250,null=True)
    date = models.DateField(null=True)
    purchasedstock = models.IntegerField(null=True)

class Sales(models.Model):
    phonenumber = models.IntegerField(null=True)
    itemname = models.CharField(max_length=250,null=True)
    hsncode = models.CharField(max_length=250,null=True)
    price = models.CharField(max_length=250,null=True)
    gst = models.IntegerField(null=True)
    cgst = models.FloatField(null=True)
    sgst = models.FloatField(null=True)
    quantity = models.IntegerField(null=True)
    date = models.DateField(null=True)
    invoiceNo =models.CharField(max_length=250,null=True)
    username = models.CharField(max_length=250,null=True)
    barcode_number = models.CharField(max_length=250,null=True)
    discount = models.IntegerField(null=True)
    discountAmt = models.FloatField(null=True)
    payment_mode = models.CharField(max_length=250,null=True)
    cash = models.FloatField(null=True)
    UPI = models.FloatField(null=True)
    status = models.CharField(max_length=250,null=True)

class Return(models.Model):
    phonenumber = models.IntegerField(null=True)
    itemname = models.CharField(max_length=250,null=True)
    hsncode = models.CharField(max_length=250,null=True)
    price = models.CharField(max_length=250,null=True)
    gst = models.IntegerField(null=True)
    cgst = models.FloatField(null=True)
    sgst = models.FloatField(null=True)
    quantity = models.IntegerField(null=True)
    date = models.DateField(auto_now_add=True)
    invoiceNo =models.CharField(max_length=250,null=True)
    username = models.CharField(max_length=250,null=True)
    barcode_number = models.CharField(max_length=250,null=True)
    discount = models.IntegerField(null=True)


class Customer(models.Model):
    name = models.CharField(max_length=250,null=True)
    phonenumber = models.IntegerField(null=True)
    address = models.CharField(max_length=250,null=True)


