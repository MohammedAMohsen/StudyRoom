from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .models import Room, Message, Topic, User
from .form import RoomForm, RegisterForm, UserForm

# +─────────────────────────────────────────────────────────────+
# |----------- (FBVs) Function-Based Views طريقة ال -------------|
# +─────────────────────────────────────────────────────────────+

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # انقلني الو واذا ما في رجعني على الصفحة الرئيسية طبيعي next اذا في الرابط
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, 'Incorrect username or password')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    return render(request, 'base/login_register.html', {'page': page})


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)
            # user.email = user.email.strip().lower()
            # user.save()
            # افضل وارتب Formنقلت التغيير داخل ال
            form.save()
            messages.success(request, 'Your account has been created! You are now able to login')
            return redirect('login')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    '''
        topic_id=q → يستخدم للفلترة الدقيقة والسريعة عندما تكون القيمة معروفة ومحددة مسبقًا (Exact Filtering).
        topic__name__icontains=q → يستخدم للبحث النصي المرن عندما يكتب المستخدم جزءًا من الاسم أو كلمات غير كاملة (Search).
    '''
    # q = request.GET.get('q', '') # ──> q = request.GET.get('q') if request.GET.get('q') != None else '' 
    # rooms = Room.objects.filter(topic=q).order_by('-updated', '-created') if q else rooms = Room.objects.all()

    q = request.GET.get('q', '')
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(host__username__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms': rooms,
        'topics':topics,
        'room_messages':room_messages
        }
    return render(request,'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() # ==> room_messages = Message.objects.filter(room=room)
    participants = room.participants.all()
    if request.method == 'POST':
        Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'room_messages':room_messages,
        'participants': participants
        }
    return render(request, 'base/room.html', context)


def topics(request):
    q = request.GET.get('q', '')
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityes(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activityes.html', {'room_messages': room_messages})


def user_profile(request, pk):
    user = User.objects.filter(username=pk).first()
    topics = Topic.objects.all()[:5]
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_messages': room_messages,
        }
    return render(request, 'base/profile.html', context)


@login_required(login_url='login') # Setting لاني اضفتها في صفحة ال login_url='/login' فعليا غير لازمة اضافة 
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':

        # Old manual approach using request.POST and Room.objects.create()
        # --------
        # topic_name = request.POST.get('topic')
        # topic, created = Topic.objects.get_or_create(name=topic_name)
        # Room.objects.create(
        #     host = request.user,
        #     topic = topic,
        #     name = request.POST.get('name'),
        #     description = request.POST.get('description'))
        # __________________________________
        
        # Manual data handling approach replaced by form-driven validation and save logic.
        # moving logic into form.py -> RoomForm.save()
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save(host=request.user)
            
        return redirect('home')
    context = {
        'page': 'create',
        'form': form,
        'topics': topics
        }
    return render(request, 'base/room_form.html', context)


@login_required()
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponseForbidden("You do not have permission to access this page.")
    if request.method == 'POST':

        # Old manual approach using request.POST and Update save
        # --------
        # topic_name = request.POST.get('topic')
        # topic, created = Topic.objects.get_or_create(name=topic_name)
        # room.name = request.POST.get('name')
        # room.description = request.POST.get('description')
        # room.topic = topic
        # room.save()
        # __________________________________

        # Manual data handling approach replaced by form-driven validation and save logic.
        # moving logic into form.py -> RoomForm.save() 
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save(host=request.user)
        return redirect('home')
    context = {
            'form': form,
            'topics': topics,
            'room': room
        }
    return render(request, 'base/room_form.html', context)


@login_required()
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponseForbidden("You do not have permission to access this page.")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required()
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponseForbidden("You are not allowed here!")
    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message})

@login_required()
def update_user(request):
    # user = request.user
    # أثناء التحقق من صحة النموذج request.user أنشئ مثيل مستخدم منفصل لتجنب التغييرات المؤقتة على
    user = User.objects.get(id=request.user.id)
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Your account has been Updated!')
            return redirect('user-profile', pk=user.username)
        else:
            messages.error(request, 'An error occured during updated!')
    context = {
        'form': form,
    }
    return render(request, 'base/update_user.html', context)


# +─────────────────────────────────────────────────────────────+
# |------------- (CBVs) Class-Based Views طريقة ال --------------|
# +─────────────────────────────────────────────────────────────+
# .....
# ....
# ...
# ..
# .
