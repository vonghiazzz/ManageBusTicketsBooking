from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import logging
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
from django.contrib.auth import logout as auth_logout
from .admin import CreateCustomerForm
from collections import defaultdict
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required



# Create your views here.
logger = logging.getLogger('app')





def chatBox(request):
    return render(request, "app/chatRoom.html")

def schedule(request):
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
        if hasattr(request.user, 'driver'):
            buses = Bus.objects.filter(id_Driver=request.user)
            trips = Trip.objects.filter(id_Buses__in=buses)
        else:
            return render(request, 'app/errors.html', {
                'error_code': 403,
                'error_message': 'Driver can see schedule.'
            }, status=403)    
    else:
        return render(request, 'app/errors.html', {
            'error_code': 403,
            'error_message': 'You must login to see schedule.'
        }, status=403)
    is_driver = hasattr(request.user, 'driver') 

    context = {
        'is_driver':is_driver,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'trips': trips,
    }
    return render(request, 'app/driver/schedule.html', context)


def search(request):
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
    else:
        user_not_login = "show"
        user_login = "hidden"

    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
    }

    if request.method == "POST":
        journeyType = request.POST.get('journeyType')
        start_point = request.POST.get('departure')
        end_point = request.POST.get('destination')
        departure_date = request.POST.get('departureDate')
        return_date = request.POST.get('returnDate', None)
        number_of_tickets = int(request.POST.get('numberOfTickets'))

        # Query routes based on start and end points
        routes = Route.objects.filter(startPoint=start_point, endPoint=end_point)
        
        # Query trips based on routes and departure date
        trips = Trip.objects.filter(
            id_Route__in=routes,
            departure_Time__date=departure_date,
            total_Seats__gte=number_of_tickets
        ).select_related('id_Buses', 'id_Route').prefetch_related('Tickets')

        if return_date:
            return_routes = Route.objects.filter(startPoint=end_point, endPoint=start_point)
            return_trips = Trip.objects.filter(
                id_Route__in=return_routes,
                departure_Time__date=return_date,
                total_Seats__gte=number_of_tickets
            ).select_related('id_Buses', 'id_Route').prefetch_related('Tickets')
        else:
            return_trips = []

        results = []
        for trip in trips:
            available_tickets = trip.total_Seats - trip.reserved_Seats
            if available_tickets >= number_of_tickets:
                results.append({
                    'trip': trip,
                    'available_tickets': available_tickets,
                    'tickets': trip.Tickets.all(),
                })

        return_results = []
        for return_trip in return_trips:
            available_tickets = return_trip.total_Seats - return_trip.reserved_Seats
            if available_tickets >= number_of_tickets:
                return_results.append({
                    'trip': return_trip,
                    'available_tickets': available_tickets,
                    'tickets': return_trip.Tickets.all(),
                })
        is_driver = hasattr(request.user, 'driver') 

        context.update({
            'is_driver':is_driver,
            'trips': results,
            'return_trips': return_results,
            'departure': start_point,
            'destination': end_point,
            'departure_date': departure_date,
            'return_date': return_date,
            'number_of_tickets': number_of_tickets,
            'journeyType':journeyType,
        })

    return render(request, 'app/search.html', context)


@login_required(login_url='/login/')
def history(request):
    if request.user.is_authenticated:
        # if hasattr(request.user, 'customer'):
             
        user = request.user
        print('user: ',user)
        bookings = Booking.objects.filter(idCustomer=user)

        booked_tickets = []

        # Duyệt qua từng booking để lấy thông tin vé tương ứng
        for booking in bookings:
            ticket = booking.idTicket  # Lấy vé từ booking

            # Kiểm tra xem vé có tồn tại không và có trạng thái đúng (đã booking)
            if ticket and ticket.status:
               booked_tickets.append({
                    'ticket': ticket,
                    'booking_status': booking.status,  # Lấy trạng thái của booking
                })
        user_not_login ="hidden"
        user_login = "show" 
        is_driver = hasattr(request.user, 'driver') 

        context={   
            'is_driver':is_driver,
            'user_not_login': user_not_login,
            'user_login':user_login,
            'booked_tickets':booked_tickets,
        }
    return render(request, 'app/customer/history.html', context)

@login_required(login_url='/login/')
def profile(request):
    if request.user.is_authenticated:
        user_not_login ="hidden"
        user_login = "show" 

    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # print('first_name: ' ,first_name)
        # print('last_name: ' ,last_name)
        user_name = request.POST.get('user_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
       
        if (len(phone_number)!=10): messages.info(request, 'Phone number must be exactly 10 digits!')
        else:
            # Kiểm tra và cập nhật avatar nếu có
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            user.first_name = first_name
            user.last_name = last_name
            user.username = user_name
            user.phone_Number = phone_number  # Đảm bảo bạn đã định nghĩa phone_Number trong model User
            user.email = email
            user.save()
            messages.success(request, 'Profile updated successfully.')

        return redirect('profile')
    is_driver = hasattr(request.user, 'driver') 

    # Nếu là GET request hoặc nếu có lỗi trong POST request, render lại trang profile
    context = {
        'is_driver':is_driver,
        'full_name': user.first_name,
        'user_name': user.username,
        'phone': user.phone_Number,
        'email': user.email,
        'user_not_login': user_not_login,
        'user_login':user_login,

    }
    return render(request, 'app/profile.html', context)






def logoutPage(request):
    auth_logout(request)
    request.session.flush()  # Xóa toàn bộ session data
    request.session.clear_expired()  # Xóa session đã hết hạn

    logout(request)
    messages.success(request, "Logout successful!")
    return redirect('login')


# def schedule(request):
#     return render(request, 'app/driver/schedule.html')



def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index') 
        elif hasattr(request.user, 'driver'):
            return redirect('schedule')
        return redirect('home') 
       
    user_not_login ="show"
    user_login = "hidden" 
    if request.method == "POST":
        username= request.POST.get('username')
        password= request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin:index')    
            elif hasattr(request.user, 'driver'):
                return redirect('schedule')
            else:
                return redirect('home')
        else: messages.info(request, 'User or password is not correct!')
    is_driver = hasattr(request.user, 'driver') 
    context = {'user_not_login':user_not_login, 'user_login':user_login,'is_driver':is_driver}
    return render(request,'app/login.html',context)

def test(request):
    return render(request, 'app/test.html')


def aboutUs(request):
    if request.user.is_authenticated:
        user_not_login ="hidden"
        user_login = "show" 
    else:
        user_not_login ="show"
        user_login = "hidden" 
    is_driver = hasattr(request.user, 'driver') 

    context = {
        'is_driver':is_driver,
        'user_not_login': user_not_login,
        'user_login':user_login,

    }

    return render(request, 'app/aboutUs.html',context)



def register(request):
    form = CreateCustomerForm()
    if request.method == "POST":
        form = CreateCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    is_driver = hasattr(request.user, 'driver') 
    user_not_login = "show"
    user_login = "hidden" 
    return render(request, 'app/register.html', {'form': form,'user_not_login': user_not_login, 'user_login': user_login, 'is_driver':is_driver})

def index(request):
    if request.user.is_authenticated:
        user_not_login ="hidden"
        user_login = "show"
    else:
        user_not_login ="show"
        user_login = "hidden"   
    try:
            # Lấy dữ liệu từ tất cả các trang
            all_buses = Bus.objects.all()
            all_trips =Trip.objects.all()


            # Lọc ra các chuyến đi có điểm khởi hành là "Thành phố Hồ Chí Minh"
            hcm = Trip.objects.filter(id_Route__startPoint='Thành phố Hồ Chí Minh')
            dl = Trip.objects.filter(id_Route__startPoint='Đà Lạt')
            vt = Trip.objects.filter(id_Route__startPoint='Bà Rịa - Vũng Tàu')

            # Nhóm các chuyến đi theo điểm khởi hành và chỉ lấy tối đa 3 chuyến xe đầu tiên của mỗi nhóm
            grouped_trips_hcm = defaultdict(list)
            grouped_trips_dl = defaultdict(list)
            grouped_trips_vt = defaultdict(list)

            for tripHCM in hcm:
                if len(grouped_trips_hcm[tripHCM.departure_Station]) < 3:
                    grouped_trips_hcm[tripHCM.departure_Station].append(tripHCM)
            for tripDL in dl:
                if len(grouped_trips_dl[tripDL.departure_Station]) < 3:
                    grouped_trips_dl[tripDL.departure_Station].append(tripDL)
            for tripVT in vt:
                if len(grouped_trips_vt[tripVT.departure_Station]) < 3:
                    grouped_trips_vt[tripVT.departure_Station].append(tripVT)

            # Kết quả là danh sách các chuyến đi
            hcm_trips = [tripHCM for trips in grouped_trips_hcm.values() for tripHCM in trips]
            dl_trips = [tripDL for trips in grouped_trips_dl.values() for tripDL in trips]
            vt_trips = [tripVT for trips in grouped_trips_vt.values() for tripVT in trips]
            is_driver = hasattr(request.user, 'driver') 
            # print('is_driver',is_driver)
            user_data = request.session.get('user_data')
            response = request.session.get('response')
            context = {
                'hcm_trips':hcm_trips,
                'dl_trips':dl_trips,
                'vt_trips':vt_trips,
                'is_driver':is_driver,

                'all_buses':all_buses,
                'all_trips':all_trips,
                'user_not_login':user_not_login,
                'user_login': user_login,
                'user_data':user_data,
                'response':response,
            }
            
            return render(request, 'app/home.html', context)
    except Exception as e:
        print('Error:', e)
        return render(request, 'app/home.html', {'error': 'An error occurred'})




def booking(request, trip_id):
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
        # print('is_Customer: ',hasattr(request.user, 'customer'))
        if hasattr(request.user, 'customer'):
            try:
                customer = Customer.objects.get(id=request.user.id)
                print('customer: ',customer)
            except Customer.DoesNotExist:
                customer = None
        else:
            return render(request, 'app/errors.html', {
                'error_code': 403,
                'error_message': 'Customer can booking.'
            }, status=403)        
    else:
        customer = None
        user_not_login = "show"
        user_login = "hidden"
    
    trip = Trip.objects.get(id=trip_id)
    tickets = Ticket.objects.filter(idTrip=trip)
    error_message = ""

    if request.method == "POST":
        name = request.POST.get('name', '')
        mobile = request.POST.get('mobile', '')
        selected_tickets = request.POST.get('selected_tickets')
        
        try:
            selected_tickets = json.loads(selected_tickets)
            print('selected_tickets: ',selected_tickets)
        except json.JSONDecodeError:
            selected_tickets = []
        
        if name and mobile:
            # Check for each selected ticket if it already has a booking
            for ticket_id in selected_tickets:
                ticket = Ticket.objects.get(id=ticket_id)
                if Booking.objects.filter(idTicket=ticket).exists():
                    error_message = f"Ticket {ticket.idSeatNumber} is already booked."
                    context = {
                        'user_not_login': user_not_login,
                        'user_login': user_login,
                        'trip': trip,
                        'tickets': tickets,
                        'error_message': error_message,
                    }
                    return render(request, 'app/customer/booking.html', context)
            for ticket_id in selected_tickets:
                
                ticket = Ticket.objects.get(id=ticket_id)
                Booking.objects.create(
                    name_Customer=name,
                    phone_Customer=mobile,
                    idTicket=ticket,
                    idCustomer=customer                
                    )
        else:
            error_message = "Name and mobile number are required."
            context = {
                'user_not_login': user_not_login,
                'user_login': user_login,
                'trip': trip,
                'tickets': tickets,
                'error_message': error_message,
            }
            return render(request, 'app/customer/booking.html', context)


            
        return HttpResponse(f'Hello {name}! Your form has been submitted successfully with {mobile}.\n selected_tickets: {selected_tickets}')
    
    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'trip': trip,
        'tickets': tickets,
        'error_message': error_message,

    }
    return render(request, 'app/customer/booking.html', context)
