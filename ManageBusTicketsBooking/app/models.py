from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import pre_save, m2m_changed, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django import forms
from django.db import IntegrityError, transaction

#Cài thêm khi sử dụng CkEditor
from ckeditor.fields import RichTextField

# Create your models here.
# itemBase - id - name - start point - end point -bến xe đi - bến xe đến - Departure Date 
class ItemBase(models.Model):
    class Meta:
        abstract = True
   
    # name = models.CharField(max_length=100, null=False, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True) #Lúc chỉnh sửa mới update ngày
    active = models.BooleanField(default=True) # khi xóa khóa học này thì nó chuyển thành false và ẩn đi chứ không xóa
    # def __str__(self) :
    #      return self.name

#ROLE - id - name 
# class Role(models.Model):
#     class Meta: 
#         ordering=["id"]
#     name =  models.CharField(max_length=100, null=False, unique=True)
#     def __str__(self):
#         return self.name
    
#ACC - id - full name- birthday - address - user name - email - phone - điểm thưởng 
def validate_phone_number(value):
    if not str(value).isdigit() or len(str(value)) != 10:
        raise ValidationError('Phone number must be 10 digits.')

class User(AbstractUser):
    class Meta: 
        ordering=["id"]
    phone_Number = models.CharField(max_length=10, null=True, blank=True, validators=[validate_phone_number])
    avatar = models.ImageField(upload_to='uploads/%Y/%m', default=None, null=True, blank=True) 
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='custom_user_set',
    #     blank=True,
    #     help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
    #     related_query_name='user'
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='custom_user_set',
    #     blank=True,
    #     help_text=('Specific permissions for this user.'),
    #     related_query_name='user'
    # )
    # idRole = models.ForeignKey(Role, related_name="Users", on_delete= models.SET_NULL, null=True,blank=False)
    # USER_TYPE_CHOICES = (
    #     ('customer', 'Customer'),
    #     ('driver', 'Driver'),
    # )
    # user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')

class Customer(User):
    class Meta:
        ordering=["id"]
    point = models.FloatField(default=0, null=False, blank=False, max_length=10)
    def __str__(self):
        return str(self.id)
class Driver(User):
    class Meta:
        ordering=["id"]
    totalDrivingTime = models.FloatField(default=0, null=False, blank=False, max_length=10)
    totalSalary = models.FloatField(default=0, null=False, blank=False, max_length=10)
    def __str__(self):
        return str(self.id)




    
#TYPE - name 
class Type(models.Model):
    class Meta: 
        ordering=["id"]
    name = models.CharField(max_length=100, null= False, blank=False)
    def __str__(self) :
         return self.name
    
# Route - ID - START POINT- END POINT- Departure Date (ngày giờ) - FK TICKET
class Route(ItemBase):
    class Meta: 
        ordering=["id"]
        # unique_together=["startPoint"]
        unique_together = ("startPoint", "endPoint")  # Thêm ràng buộc unique

    VIETNAM_PROVINCES = [
    ('Hà Nội', 'Hà Nội'),
    ('Hà Giang', 'Hà Giang'),
    ('Cao Bằng', 'Cao Bằng'),
    ('Bắc Kạn', 'Bắc Kạn'),
    ('Tuyên Quang', 'Tuyên Quang'),
    ('Lào Cai', 'Lào Cai'),
    ('Điện Biên', 'Điện Biên'),
    ('Lai Châu', 'Lai Châu'),
    ('Sơn La', 'Sơn La'),
    ('Yên Bái', 'Yên Bái'),
    ('Hoà Bình', 'Hoà Bình'),
    ('Thái Nguyên', 'Thái Nguyên'),
    ('Lạng Sơn', 'Lạng Sơn'),
    ('Quảng Ninh', 'Quảng Ninh'),
    ('Bắc Giang', 'Bắc Giang'),
    ('Phú Thọ', 'Phú Thọ'),
    ('Vĩnh Phúc', 'Vĩnh Phúc'),
    ('Bắc Ninh', 'Bắc Ninh'),
    ('Hải Dương', 'Hải Dương'),
    ('Hải Phòng', 'Hải Phòng'),
    ('Hưng Yên', 'Hưng Yên'),
    ('Thái Bình', 'Thái Bình'),
    ('Hà Nam', 'Hà Nam'),
    ('Nam Định', 'Nam Định'),
    ('Ninh Bình', 'Ninh Bình'),
    ('Thanh Hóa', 'Thanh Hóa'),
    ('Nghệ An', 'Nghệ An'),
    ('Hà Tĩnh', 'Hà Tĩnh'),
    ('Quảng Bình', 'Quảng Bình'),
    ('Quảng Trị', 'Quảng Trị'),
    ('Thừa Thiên Huế', 'Thừa Thiên Huế'),
    ('Đà Nẵng', 'Đà Nẵng'),
    ('Quảng Nam', 'Quảng Nam'),
    ('Quảng Ngãi', 'Quảng Ngãi'),
    ('Bình Định', 'Bình Định'),
    ('Phú Yên', 'Phú Yên'),
    ('Khánh Hòa', 'Khánh Hòa'),
    ('Ninh Thuận', 'Ninh Thuận'),
    ('Bình Thuận', 'Bình Thuận'),
    ('Kon Tum', 'Kon Tum'),
    ('Gia Lai', 'Gia Lai'),
    ('Đắk Lắk', 'Đắk Lắk'),
    ('Đắk Nông', 'Đắk Nông'),
    ('Đà Lạt', 'Đà Lạt'),
    ('Bình Phước', 'Bình Phước'),
    ('Tây Ninh', 'Tây Ninh'),
    ('Bình Dương', 'Bình Dương'),
    ('Đồng Nai', 'Đồng Nai'),
    ('Bà Rịa - Vũng Tàu', 'Bà Rịa - Vũng Tàu'),
    ('Thành phố Hồ Chí Minh', 'Thành phố Hồ Chí Minh'),
    ('Long An', 'Long An'),
    ('Tiền Giang', 'Tiền Giang'),
    ('Bến Tre', 'Bến Tre'),
    ('Trà Vinh', 'Trà Vinh'),
    ('Vĩnh Long', 'Vĩnh Long'),
    ('Đồng Tháp', 'Đồng Tháp'),
    ('An Giang', 'An Giang'),
    ('Kiên Giang', 'Kiên Giang'),
    ('Cần Thơ', 'Cần Thơ'),
    ('Hậu Giang', 'Hậu Giang'),
    ('Sóc Trăng', 'Sóc Trăng'),
    ('Bạc Liêu', 'Bạc Liêu'),
    ('Cà Mau', 'Cà Mau'),
    ]
    startPoint = models.CharField(max_length=50, choices=VIETNAM_PROVINCES)
    endPoint = models.CharField(max_length=50, choices=VIETNAM_PROVINCES)
    
    def name(self):
        return f"{self.startPoint} - {self.endPoint}"

    def __str__(self):
        return str(self.startPoint) + "-" + str(self.endPoint)




class Trip(ItemBase):
    class Meta: 
        ordering=["id"]
        unique_together = ('departure_Station','departure_Time','id_Buses')
        # unique_together = ('id_Buses', 'departure_Time')
        # unique_together =('id','id_Buses')
    price = models.FloatField(validators=[MinValueValidator(50), MaxValueValidator(200)],default=50)  # Giới hạn giá trị từ 50 đến 200
    distance = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(3000)],default=0)
    departure_Station = models.CharField(max_length =100, null = False, blank=False)
    ending_Station = models.CharField(max_length =100, null = False, blank=False)
    departure_Time = models.DateTimeField(null=False, blank=False,default=timezone.now)
    arrival_Time = models.DateTimeField(null=False, blank=False, default=timezone.now)
    hours = models.CharField(max_length=20, blank=True, null=True)  # Trường để lưu giờ
    total_Seats = models.IntegerField(default=34)
    reserved_Seats = models.IntegerField(default=0)

    id_Route = models.ForeignKey(Route, related_name= "trip",on_delete= models.SET_NULL, null=True)
    id_Buses= models.ForeignKey('Bus', related_name="trip", on_delete= models.SET_NULL, null=True, blank=True, default=None)
    def name(self):
        return str(self.departure_Station)+ '-'+str(self.ending_Station)
    def __str__(self) :
        return str(self.departure_Station)+ '-'+str(self.ending_Station)+' ('+str(self.departure_Time)+')'



    def save(self, *args, **kwargs):
        # if self.id_Buses:
        #     self.total_Seats = self.id_Buses.total_Seats  # Assign Bus's total seats
        # self.reserved_Seats = Ticket.objects.filter(idTrip=self, status=True).count()

        if self.departure_Time is None or self.arrival_Time is None:
            raise ValidationError("Departure time and Arrival time cannot be None.")
        
        if self.arrival_Time and self.departure_Time :
            time_difference = self.arrival_Time - self.departure_Time
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            self.hours = f"{hours:02d}:{minutes:02d}"
        super().save(*args, **kwargs)

        if self.id_Buses and self.pk:
            trip_name = f"{self.departure_Station} - {self.ending_Station} - {self.departure_Time}"

        for i in range(1, self.total_Seats + 1):
            unique_ticket_name = f"{trip_name} - Seat {i} - Id Bus {self.id_Buses}"
            try:
                with transaction.atomic():
                    seatNumber = SeatNumber.objects.get(idBus=self.id_Buses, seat_number=i)
                    Ticket.objects.create(
                        name=unique_ticket_name,  # Đảm bảo tên ticket là duy nhất
                        idTrip=self,
                        idSeatNumber=seatNumber,
                        status=False,
                        img="ticket/2024/04/ticket.jpeg"
                    )
            except SeatNumber.DoesNotExist:
                print(f"SeatNumber with idBus={self.id_Buses} and seat_number={i} does not exist.")
            except IntegrityError:
                print(f"Ticket with name {unique_ticket_name} already exists.")
        super().save(*args, **kwargs)


# BUS -  ID- NAME - TÌNH TRẠNG XE - TỔNG SỐ GHẾ - bến xe đi - bến xe đến - GHẾ ĐÃ ĐẶT - FK acc
class Bus(ItemBase):
        class Meta: 
            ordering=["id"]
            db_table = 'Buses'  # Đặt tên bảng là "Buses"
        idType = models.ForeignKey(Type,related_name='Buss', on_delete= models.SET_NULL, null=True,blank=False)
        vehicle_Condition =  RichTextField() 
        id_Driver = models.ForeignKey(
                    Driver, 
                    on_delete= models.SET_NULL, null=True,
                    limit_choices_to={'bus__isnull': True}  # Chỉ hiển thị Driver chưa có trong Bus
                )    
        def __str__(self):
            return str(self.id)
        

        def save(self, *args, **kwargs):                
            if self.pk:
                # Nếu Bus đã tồn tại, xóa các ghế cũ của nó
                SeatNumber.objects.filter(idBus=self).delete()
            super().save(*args, **kwargs)
            
            for i in range(1, 34 + 1):
                SeatNumber.objects.create(idBus=self, seat_number=i)





    

#SEAT NUMBER -id - des - fk idBus
class SeatNumber(models.Model):
    class Meta: 
        ordering=["id"]
        unique_together = ('seat_number','idBus')
    idBus = models.ForeignKey(Bus, related_name='seatNumber', on_delete=models.CASCADE, null=False, blank=False)
    seat_number = models.IntegerField()
   

    def __str__(self) :
      return str(self.idBus)  + "-" + str(self.seat_number)




#TICKET - ID - NAME - HOURS - STATUS  - PRICE - FK (seat number, trip, type, bus)
class Ticket(ItemBase):
    class Meta: 
        ordering=["id"]
    name = models.CharField(max_length=100, null=False, unique=True)
    img = models.ImageField(upload_to='ticket/%Y/%m', default=None, null=True, blank=True)
    status = models.BooleanField(default=False) 
    # idSeatNumber = models.ForeignKey(SeatNumber, related_name='Tickets',on_delete=models.CASCADE)
    idSeatNumber = models.ForeignKey(
            SeatNumber, 
            related_name='Tickets',
            on_delete=models.CASCADE,
            limit_choices_to={'seat_number__isnull': True}  # Chỉ hiển thị seatNumber chưa có trong Ticket
    )   
    idTrip = models.ForeignKey(Trip,related_name='Tickets', on_delete=models.CASCADE, null=True,blank=True)
    def __str__(self) :
         return str(self.id)
    

    # def save(self, *args, **kwargs):
    #     if not self.pk:  # Chỉ kiểm tra khi tạo Ticket mới
    #         trip_ids = [trip.id for trip in self.idBus.trip.all()]
    #         if Ticket.objects.filter(name=self.name, idBus__trip__id__in=trip_ids).exists():
    #             raise ValidationError("Tên vé đã tồn tại trong một hoặc nhiều chuyến đi.")
    #     super().save(*args, **kwargs)

    def update_status(self):
        # Kiểm tra xem có booking nào liên quan đến Ticket không
        has_booking = Booking.objects.filter(idTicket=self).exists() 
        # Cập nhật trạng thái của Ticket dựa trên sự tồn tại của booking
        self.status = has_booking
        self.save()  # Lưu lại Ticket để cập nhật trạng thái
    
# BOOKING - id - bookingDate - status - FK (ticket, acc)
class Booking(models.Model):
    class Meta: 
        ordering=["id"]
        # unique_together = ('idTicket','idBooking')
    name_Customer = models.CharField(max_length=100, null= False, blank=False)
    phone_Customer = models.CharField(max_length=10, null=True, blank=True, validators=[validate_phone_number])
    bookingDate = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False) 
    idTicket = models.ForeignKey(
            Ticket, 
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            limit_choices_to={'booking__isnull': True}  # Chỉ hiển thị Ticket chưa có trong Booking
        )    
    idCustomer = models.ForeignKey(Customer, related_name='Booking', on_delete= models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return str(self.idTicket) + " of "+ str(self.idCustomer)
    
    
    def save(self, *args, **kwargs):
        old_ticket = None
        if self.id:
            old_ticket = self.__class__.objects.get(pk=self.pk).idTicket  # Lấy vé cũ trước khi lưu
            print(1)
        super().save(*args, **kwargs)
        if old_ticket:
            old_ticket.status = False  # Đặt status của vé cũ là False
            old_ticket.save()
            print(2)
        if self.idTicket:
            self.idTicket.status = True  # Set status of new ticket to True
            self.idTicket.save()


        self.update_trip_reserved_seats()


    def delete(self, *args, **kwargs):  
        super().delete(*args, **kwargs)
        self.update_trip_reserved_seats()
        print(3)

    def update_trip_reserved_seats(self):
        if self.idTicket:
            self.idTicket.idTrip.reserved_Seats = Ticket.objects.filter(idTrip=self.idTicket.idTrip, status=True).count()
            self.idTicket.idTrip.save()
            print(4)


    








    

 









 