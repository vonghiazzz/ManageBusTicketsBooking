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
import math
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
        unique_together=["email"]
    email = models.EmailField(unique=True)  # Đảm bảo trường email là duy nhất
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
        return str(self.username)
class Driver(User):
    class Meta:
        ordering=["id"]
    totalDrivingTime = models.FloatField(default=0, null=False, blank=False, max_length=10)
    totalSalary = models.FloatField(default=0, null=False, blank=False, max_length=10)
    def __str__(self):
        return str(self.username)


class Salary(models.Model):
    class Meta:
        ordering=["id"]
    month = models.DateField(null=False, blank=False)  
    totalDistance = models.FloatField(null=False, blank=False, max_length=10)
    idDriver = models.ForeignKey(Driver, related_name='Salary', on_delete= models.CASCADE, null=False, blank=False)
    def __str__(self):
        return f"Salary of {self.idDriver.username} for {self.month.strftime('%B %Y')}"
    
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
    POSITION = [
   ('Gas Hà Nội,21.0285,105.8542', 'Gas Hà Nội'),
    ('Gas Hà Giang,22.3255,104.4660', 'Gas Hà Giang'),
    ('Gas Cao Bằng,22.6636,106.2874', 'Gas Cao Bằng'),
    ('Gas Bắc Kạn,22.1533,105.6126', 'Gas Bắc Kạn'),
    ('Gas Tuyên Quang,21.8122,105.2176', 'Gas Tuyên Quang'),
    ('Gas Lạng Sơn,21.8458,106.7610', 'Gas Lạng Sơn'),
    ('Gas Quảng Ninh,21.0467,107.0832', 'Gas Quảng Ninh'),
    ('Gas Bắc Giang,21.2726,106.2025', 'Gas Bắc Giang'),
    ('Gas Bắc Ninh,21.1857,106.0854', 'Gas Bắc Ninh'),
    ('Gas Hải Dương,20.9388,106.3216', 'Gas Hải Dương'),
    ('Gas Hải Phòng,20.8449,106.6881', 'Gas Hải Phòng'),
    ('Gas Hưng Yên,20.5882,106.0664', 'Gas Hưng Yên'),
    ('Gas Thái Bình,20.4477,106.3586', 'Gas Thái Bình'),
    ('Gas Hà Nam,20.5737,105.9898', 'Gas Hà Nam'),
    ('Gas Nam Định,20.4098,106.1630', 'Gas Nam Định'),
    ('Gas Ninh Bình,20.2530,105.9767', 'Gas Ninh Bình'),
    ('Gas Thanh Hóa,19.8076,105.7740', 'Gas Thanh Hóa'),
    ('Gas Nghệ An,19.2613,104.4558', 'Gas Nghệ An'),
    ('Gas Hà Tĩnh,18.3358,105.9112', 'Gas Hà Tĩnh'),
    ('Gas Quảng Bình,17.4620,106.1955', 'Gas Quảng Bình'),
    ('Gas Quảng Trị,16.7425,107.1276', 'Gas Quảng Trị'),
    ('Gas Thừa Thiên Huế,16.4637,107.5836', 'Gas Thừa Thiên Huế'),
    ('Gas Đà Nẵng,16.0544,108.2022', 'Gas Đà Nẵng'),
    ('Gas Quảng Nam,15.5850,108.0751', 'Gas Quảng Nam'),
    ('Gas Quảng Ngãi,15.1176,108.8404', 'Gas Quảng Ngãi'),
    ('Gas Bình Định,13.7824,109.2102', 'Gas Bình Định'),
    ('Gas Phú Yên,13.0900,109.2470', 'Gas Phú Yên'),
    ('Gas Khánh Hòa,12.2384,109.1967', 'Gas Khánh Hòa'),
    ('Gas Ninh Thuận,11.5802,108.9351', 'Gas Ninh Thuận'),
    ('Gas Bình Thuận,10.9284,108.4731', 'Gas Bình Thuận'),
    ('Gas Đà Lạt,11.6684,108.5402', 'Gas Đà Lạt'),
    ('Gas Đắk Lắk,12.6780,108.3434', 'Gas Đắk Lắk'),
    ('Gas Đắk Nông,12.1910,107.5921', 'Gas Đắk Nông'),
    ('Gas Gia Lai,13.9860,108.4451', 'Gas Gia Lai'),
    ('Gas Kon Tum,14.3506,108.0001', 'Gas Kon Tum'),
    ('Gas Hồ Chí Minh,10.8231,106.6297', 'Gas Hồ Chí Minh'),
    ('Gas Bình Dương,11.0072,106.6512', 'Gas Bình Dương'),
    ('Gas Bình Phước,11.5020,106.9498', 'Gas Bình Phước'),
    ('Gas Tây Ninh,11.3478,106.1034', 'Gas Tây Ninh'),
    ('Gas Long An,10.5580,106.3420', 'Gas Long An'),
    ('Gas Tiền Giang,10.3619,106.3481', 'Gas Tiền Giang'),
    ('Gas Bến Tre,10.2430,106.3570', 'Gas Bến Tre'),
    ('Gas Trà Vinh,9.9274,106.3294', 'Gas Trà Vinh'),
    ('Gas Vĩnh Long,10.2537,105.9562', 'Gas Vĩnh Long'),
    ('Gas Cần Thơ,10.0451,105.7460', 'Gas Cần Thơ'),
    ('Gas Hậu Giang,10.3130,105.3880', 'Gas Hậu Giang'),
    ('Gas Sóc Trăng,9.5960,105.9800', 'Gas Sóc Trăng'),
    ('Gas Bạc Liêu,9.2950,105.7117', 'Gas Bạc Liêu'),
    ('Gas Cà Mau,9.1750,105.1500', 'Gas Cà Mau')
   ]
    price = models.FloatField(validators=[MinValueValidator(50), MaxValueValidator(200)],default=50)  # Giới hạn giá trị từ 50 đến 200
    distance = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(3000)],default=0)
    # departure_Station = models.CharField(max_length =100, null = False, blank=False)
    departure_Station = models.CharField(
        max_length=100,
        choices=POSITION,
        default='Gas Đà Lạt,11.6684,108.5402' 
    )
    # ending_Station = models.CharField(max_length =100, null = False, blank=False)
    ending_Station = models.CharField(
        max_length=100,
        choices=POSITION,
        default='Gas Cần Thơ,10.0451,105.7460'  
    )
    departure_Time = models.DateTimeField(null=False, blank=False,default=timezone.now)
    arrival_Time = models.DateTimeField(null=False, blank=False, default=timezone.now)
    hours = models.CharField(max_length=20, blank=True, null=True)  # Trường để lưu giờ
    total_Seats = models.IntegerField(default=34)
    reserved_Seats = models.IntegerField(default=0)

    id_Route = models.ForeignKey(Route, related_name= "trip",on_delete= models.SET_NULL, null=True)
    id_Buses= models.ForeignKey('Bus', related_name="trip", on_delete= models.SET_NULL, null=True, blank=True, default=None)
    def name(self):
        departure_name = self.departure_Station.split(',')[0]  # Chỉ lấy phần tên trước dấu phẩy
        ending_name = self.ending_Station.split(',')[0]  # Chỉ lấy phần tên trước dấu phẩy
        return f"{departure_name} - {ending_name}"
    def departure_name(self):
        departure_name = self.departure_Station.split(',')[0]  # Chỉ lấy phần tên trước dấu phẩy
        return departure_name
    def ending_name(self):
        ending_name = self.ending_Station.split(',')[0]  # Chỉ lấy phần tên trước dấu phẩy
        return ending_name

    def __str__(self) :
        return f"{self.departure_name()} - {self.ending_name()}"
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        # Chuyển đổi từ độ sang radian
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Tính sự chênh lệch
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Áp dụng công thức Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # Bán kính của Trái Đất (km)
        R = 6371
        
        # Tính khoảng cách
        distance = R * c
        return distance
    @staticmethod
    def get_coordinates(station_value):
        for value, label in Trip.POSITION:
            if station_value == value:
                coords = value.split(',')[1:]  # Lấy phần tọa độ từ chuỗi
                lat = float(coords[0])
                lon = float(coords[1])
                return lat, lon
        return None, None   
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
        if self.departure_Station and self.ending_Station:
            # Lấy tọa độ từ giá trị trong danh sách POSITION
            dep_lat, dep_lon = self.get_coordinates(self.departure_Station)
            end_lat, end_lon = self.get_coordinates(self.ending_Station)
            
            # print(f"Departure Coordinates: {dep_lat}, {dep_lon}")
            # print(f"Ending Coordinates: {end_lat}, {end_lon}")

            if dep_lat is not None and dep_lon is not None and end_lat is not None and end_lon is not None:
                self.distance = self.haversine(dep_lat, dep_lon, end_lat, end_lon)
                self.distance = round(self.distance, 2)
                # print(f"Calculated Distance: {self.distance}")


        super().save(*args, **kwargs)

        if self.id_Buses and self.pk:
            trip_name = f"{self.departure_Station} - {self.ending_Station} - {self.departure_Time}"
            bus = self.id_Buses
            driver = bus.id_Driver 

            if driver:
                if self.hours:
                    hours_parts = self.hours.split(':')
                    hours = int(hours_parts[0])
                    minutes = int(hours_parts[1])
                    total_hours = hours + minutes / 60.0
                else:
                    total_hours = 0
                driver.totalDrivingTime += total_hours
                driver.totalSalary += self.distance / 50 * 10
                driver.save()
                 # Lưu thông tin lương vào bảng Salary
                month = self.departure_Time.date().replace(day=1)
                salary, created = Salary.objects.get_or_create(
                    month=month,
                    idDriver=driver,
                    defaults={'totalDistance': self.distance}
                )

                if not created:
                    salary.totalDistance += self.distance
                    salary.save()
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
            unique_together=['vehycle_number']
        vehycle_number=models.CharField(null=False, blank=False, max_length=8)
        idType = models.ForeignKey(Type,related_name='Buss', on_delete= models.SET_NULL, null=True,blank=False)
        vehicle_Condition =  models.TextField(null=True,blank=True) 
        id_Driver = models.ForeignKey(
                    Driver, 
                    on_delete= models.SET_NULL, null=True,
                    limit_choices_to={'bus__isnull': True}  # Chỉ hiển thị Driver chưa có trong Bus
                )    
        def __str__(self):
            return str(self.vehycle_number)
        

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
    def seatNumber(self):
        return str(self.seat_number)



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


    

# class Feedback(models.Model):
#     class Meta: 
#         ordering = ["id"]
#     content = models.CharField(max_length=500, null=False, blank=False)
#     feedback_date = models.DateTimeField(auto_now_add=True)
#     idBooking = models.ForeignKey(Booking, related_name='feedbacks', on_delete=models.CASCADE, null=False, blank=False)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Thêm trường này để lưu trữ thông tin người dùng

    
    
#     def __str__(self):
#         return f"Feedback for Booking {self.idBooking.id}"

class Feedback(models.Model):
    class Meta: 
        ordering = ["id"]
    content = models.CharField(max_length=500, null=False, blank=False)
    feedback_date = models.DateTimeField(auto_now_add=True)
    idTrip = models.ForeignKey(Trip, related_name='feedbacks', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Lưu trữ thông tin người dùng
    
    def __str__(self):
        trip_info = f"Trip {self.idTrip.id}" if self.idTrip else "No Trip"
        user_info = self.user.username if self.user else "Unknown User"
        return f"Feedback for {trip_info} by {user_info}"