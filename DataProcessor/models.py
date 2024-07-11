from django.db import models

class Category(models.Model):
    clubbed_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.clubbed_name

class Insurer(models.Model):
    insurer = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    clubbed_name = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.insurer

class Products(models.Model):
    Product = models.CharField(max_length=255)
    def __str__(self):
        return self.Product

class Month(models.Model):
    month = models.CharField(max_length=255)
    month_num = models.IntegerField()

    def __str__(self):
        return self.month
