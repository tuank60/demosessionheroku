from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django.contrib.auth import login, authenticate
import time, os
from django.conf import settings
from datetime import datetime
from django.core.files.storage import FileSystemStorage


from django.shortcuts import render,HttpResponse, redirect,render_to_response,HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.template.loader import render_to_string
from mysession.token import account_activation_token
from django.core.mail import EmailMessage
from django.db.models import Q
from mysession import models
import threading
# Create your views here.

def registration(request):
    data = {}
    error = {}
    content = {
        'data': data,
        'error': error
    }
    if request.method == 'POST':
        data['username'] = request.POST.get('username')
        data['email'] = request.POST.get('email')
        data['password'] = request.POST.get('password')
        data['firstname'] = request.POST.get('firstname')
        data['lastname'] = request.POST.get('lastname')
        if models.AuthUser.objects.filter(username= data['username']).exists():
            error['username'] = 'Username already exist'
        if models.AuthUser.objects.filter(email= data['email']).exists():
            error['email'] = 'Email already exist'
        if not error:
            auther = models.AuthUser(username= data['username'], email= data['email'], password= data['password'],
                                     first_name= data['firstname'], last_name= data['lastname'])
            auther.save()

            auth_profile = models.AuthUserProfile(user= auther)
            auth_profile.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account'
            message = render_to_string('activate_email.html', {
                'user':auther,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(auther.pk)).decode(),
                'token':account_activation_token.make_token(auther),
            })
            to_email = data['email']
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            # return HttpResponse('Please confirm your email address to complete the registration')
            return render_to_response('register_complete.html')
    return render(request, 'registration.html', content)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = models.AuthUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, models.AuthUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        #return HttpResponse('Thank you for your email confirmation. Now you can login your account!')
        return render_to_response('sucess.html')
    else:
        return render_to_response('failure.html')

# @login_required
@csrf_protect
def home(request):
    models.DjangoSession.objects.filter(expire_date__lt= datetime.utcnow()).delete()
    if not request.session.has_key('username'):
        return redirect('login')
    else:
        username = request.session['username']
        auth = models.AuthUser.objects.get(username= username)
        profile = models.AuthUserProfile.objects.get(user= auth)
        filename = profile.image_name
        if request.method == 'POST' and request.FILES['myimage']:
            myfile = request.FILES['myimage']
            fs = FileSystemStorage()
            old_url = fs.url(username)
            url_file = settings.BASE_DIR.replace('\\', '//') + str(old_url).replace('/', '//').replace('%20',' ')
            try:
                os.remove(url_file)
            except OSError:
                pass
            fs.save(username, myfile)
            profile.image_name = username
            profile.save()
        content = {'username': username,
                   'filename': filename}
        return render(request,'home.html' , content)

@csrf_protect
def myview(request):
    return render(request, 'hello.html')

def RegularVerification():
    print("tuan")

@csrf_protect
def Mylogin(request):
    t1 = threading.Thread(target=RegularVerification)
    t1.setDaemon(True)
    t1.start()
    error = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        exist_user = models.AuthUser.objects.filter(Q(is_active=1) , Q(username= username) | Q(email= username))
        if exist_user.exists() and exist_user[0].password == password:
            login(request, exist_user[0])
            request.session['username'] = username    # ki login thi tao phien lam viec
            # request.session['permission'] = exist_user[0].user_type
            request.session.set_expiry(0)         #khoang thoi gian lam viec cua phien
            return redirect('home')
        else:
            error['uname'] = 'something when wrong'
    return render(request, 'login.html', {'error':error})

def Mylogout(request):
    try:
         del request.session['username']
    except:
        pass
    return render(request, 'logout.html')

@csrf_protect
def hello(request):
    if request.method == 'POST' and request.FILES['img']:
        myfile = request.FILES['img']
        fs = FileSystemStorage()
        fs.save('a', myfile)
    return render(request, 'hello.html')

@csrf_protect
def haspermission(username):
    permission = {}
    permission['has_view'] = False
    permission['has_use'] = False
    permission['has_edit'] = False

    auth = models.AuthUser.objects.get(username= username)
