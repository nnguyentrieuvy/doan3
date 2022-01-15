from djongo import models

# Create your models here.
class Tuyen(models.Model):
    MaTuyen = models.CharField(max_length=10, primary_key=True)
    TenTuyen = models.CharField(max_length=80)

class LoTrinh(models.Model):
    MaLT = models.CharField(max_length=10, primary_key=True)
    XuatBen = models.TimeField()
    CapBen = models.TimeField()
    MaTuyen = models.ForeignKey(Tuyen, on_delete=models.CASCADE)

class NhanVien(models.Model):
    MaNV = models.CharField(max_length=10, primary_key=True)
    hoten = models.CharField(max_length=100)
    ns = models.DateTimeField()
    dc = models.CharField(max_length=200)
