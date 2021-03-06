from email import message
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    if request.GET.get('q')!=None:
        q = request.GET.get('q')
    else:
        q = ''
    rooms = Room.objects.filter(
       Q(topic__name__icontains=q) |
       Q(name__icontains=q) |
    #    Q(host__icontains=q) |
       Q(description__icontains=q) 
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method=="POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context = {'room' : room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context) 

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    context = {'user':user,'rooms':rooms,'topics':topics,'room_messages':room_messages}
    return render(request,'base/profile.html',context) 

@login_required(login_url='login')    #Decorators
def createRoom(request):
    form = RoomForm
    topics = Topic.objects.all()
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic=  topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home') #here home is a name attribute from urls.py

    context = {'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login') 
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #Old value will be prefilled
    topics = Topic.objects.all()
    if request.user!=room.host:
        return HttpResponse("You dont have rights!")

    if request.method=='POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid:
            form.save()
            return redirect('home')

    context = {'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login') 
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user!=room.host:
        return HttpResponse("You dont have rights!")

    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login') 
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user!=message.user:
        return HttpResponse("You dont have rights!")

    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message.body})

@login_required(login_url='login') 
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk = user.id)
    return render(request,'base/update-user.html',{'form':form})


def loginPage(request):  
    page="login"
    if request.user.is_authenticated:   #If already logged in thrn restrict this page
        return redirect('home')

    if request.method=='POST':
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid Credentials.')

    context={'page':page}
    return render(request,'base/login_register.html',context)

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method=='POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Error Occured while registeration!")

    context={'page':page,'form':form}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)   #logout current user using request token
    return redirect('home')     

def topicsPage(request):
    if request.GET.get('q')!=None:
        q = request.GET.get('q')
    else:
        q = ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})