from unicodedata import category
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import json, datetime
from django.contrib.auth.models import User
from django.contrib import messages
from blogApp.models import UserProfile,Category, Post, Comment

from blogApp.forms import UserRegistration, UpdateProfile, UpdateProfileMeta, UpdateProfileAvatar, SaveCategory, SavePost, AddAvatar, CommentForm

category_list = Category.objects.exclude(status = 2).all()
context = {
    'page_title' : 'UERR',
    'category_list' : category_list,
    'category_list_limited' : category_list[:3]
}
#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'

        

            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')
    
def home(request):

    posts = Post.objects.filter(status=1)
    page = Paginator(posts, 10)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    context['page_title'] = "Home"
    context['page'] = page
    
    return render(request, "home.html", context)

def search(request):
    search  = ''
    if request.GET.get('search_query'):
       search = request.GET.get('search_query')
        
    
    if search:
        posts = Post.objects.filter(
                Q(capital__icontains = search) |
                Q(title__icontains = search) 
            )
        context['posts'] = posts
        context['page_title'] = 'Home'   
        return render(request, "search.html", context)
        

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            newUser = User.objects.all().last()
            try:
                profile = UserProfile.objects.get(user = newUser)
            except:
                profile = None
            if profile is None:
                UserProfile(user = newUser, avatar = request.FILES['avatar']).save()
            else:
                
                avatar = AddAvatar(request.POST,request.FILES, instance = profile)
                if avatar.is_valid():
                    avatar.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def profile(request):
    context = {
        'page_title':"My Profile"
    }

    return render(request,'profile.html',context)
    
@login_required
def update_profile(request):
    context['page_title'] = "Update Profile"
    user = User.objects.get(id= request.user.id)
    profile = UserProfile.objects.get(user= user)
    context['userData'] = user
    context['userProfile'] = profile
    if request.method == 'POST':
        data = request.POST
        # if data['password1'] == '':
        # data['password1'] = '123'
        form = UpdateProfile(data, instance=user)
        if form.is_valid():
            form.save()
            form2 = UpdateProfileMeta(data, instance=profile)
            if form2.is_valid():
                form2.save()
                messages.success(request,"Your Profile has been updated successfully")
                return redirect("profile")
            else:
                # form = UpdateProfile(instance=user)
                context['form2'] = form2
        else:
            context['form1'] = form
            form = UpdateProfile(instance=request.user)
    return render(request,'update_profile.html',context)


@login_required
def update_avatar(request):
    context['page_title'] = "Update Avatar"
    user = User.objects.get(id= request.user.id)
    context['userData'] = user
    context['userProfile'] = user.profile
    img = user.profile.avatar.url

    context['img'] = img
    if request.method == 'POST':
        form = UpdateProfileAvatar(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Profile has been updated successfully")
            return redirect("profile")
        else:
            context['form'] = form
            form = UpdateProfileAvatar(instance=user)
    return render(request,'update_avatar.html',context)

#Category
@login_required
def category_mgt(request):
    categories = Category.objects.all()
    context['page_title'] = "Category Management"
    context['categories'] = categories
    return render(request, 'category_mgt.html',context)

@login_required
def manage_category(request,pk=None):
    # category = Category.objects.all()
    if pk == None:
        category = {}
    elif pk > 0:
        category = Category.objects.filter(id=pk).first()
    else:
        category = {}
    context['page_title'] = "Manage Category"
    context['category'] = category

    return render(request, 'manage_category.html',context)

@login_required
def manage_comment(request):
    comments = Comment.objects.all()
    page = Paginator(comments, 10)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    context['page_title'] = "Comment Management"
    context['page'] = page
    return render(request, 'manage_comment.html',context) 

@login_required
def manage_user(request):
    users = UserProfile.objects.all()
    context['page_title'] = "User Management"
    context['users'] = users
    return render(request, 'manage_user.html',context) 

     

@login_required
def save_category(request):
    resp = { 'status':'failed' , 'msg' : '' }
    if request.method == 'POST':
        category = None
        if not request.POST['id'] == '':
            category = Category.objects.filter(id=request.POST['id']).first()
        if not category == None:
            form = SaveCategory(request.POST,instance = category)
        else:
            form = SaveCategory(request.POST)
    if form.is_valid():
        form.save()
        resp['status'] = 'success'
        messages.success(request, 'Category has been saved successfully')
    else:
        for field in form:
            for error in field.errors:
                resp['msg'] += str(error + '<br>')
        if not category == None:
            form = SaveCategory(instance = category)
       
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def save_post(request):
    resp = { 'status':'failed' , 'msg' : '' }
    if request.method == 'POST':
        post = None
        if not request.POST['id'] == '':
            post = Post.objects.filter(id=request.POST['id']).first()
        if not post == None:
            form = SavePost(request.POST,request.FILES,instance = post)
        else:
            form = SavePost(request.POST,request.FILES)
    if form.is_valid():
        form.save()
        resp['status'] = 'success'
        messages.success(request, 'Post has been saved successfully')
    else:
        for field in form:
            for error in field.errors:
                resp['msg'] += str(error + '<br>')
        if not post == None:
            form = SavePost(instance = post)
       
    return HttpResponse(json.dumps(resp),content_type="application/json")    

@login_required
def delete_category(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            category = Category.objects.filter(id = id).first()
            category.delete()
            resp['status'] = 'success'
            messages.success(request,'Category has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def delete_comment(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            comment = Comment.objects.filter(id = id).first()
            comment.delete()
            resp['status'] = 'success'
            messages.success(request,'Comment has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")


@login_required
def delete_user(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            comment = UserProfile.objects.filter(id = id).first()
            comment.delete()
            resp['status'] = 'success'
            messages.success(request,'User has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")

#Post
@login_required
def post_mgt(request):
    if request.user.profile.user_type == 1:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(author = request.user).all()

    context['page_title'] = "post Management"
    context['posts'] = posts
    return render(request, 'post_mgt.html',context)

@login_required
def manage_post(request,pk=None):
    # post = post.objects.all()

    if pk == None:
        post = {}
        
    elif pk > 0:
        post = Post.objects.filter(id=pk).first()
        
    else:
        post = {}
  
    context['page_title'] = "Manage post"
    context['post'] = post
  
  

    return render(request, 'manage_post.html',context)

@login_required
def publish(request,pk=None):
    if pk == None:
        post = {}
    elif pk > 0:
        
        Post.objects.filter(id = pk).update(status = 1)
        post = Post.objects.all()
    else:
        post = {}
    context['page_title'] = "Manage post"
    context['post'] = post

    return render(request, 'post_mgt.html',context)



@login_required
def delete_post(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            post = Post.objects.filter(id = id).first()
            post.delete()
            resp['status'] = 'success'
            messages.success(request,'Post has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")

def view_post(request,pk=None):
    
    context['page_title'] = ""
    if pk is None:
        messages.error(request,"Unabale to view Post")
        return redirect('home-page')
    else:
        post = Post.objects.filter(id = pk).first()
        count = Comment.objects.filter(id = post.id).count()
        form = CommentForm(request.POST or None)

        
        context['page_title'] = post.title
        context['post'] = post
        context['count'] = count
        context['form'] = form

        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment=form.save(commit=False)
                comment.post=post
                comment.save()
                return redirect('view-post', pk=post.id)
        else:
            
            form = CommentForm()
             
        return render(request, 'view_post.html', context)



def post_by_category(request,pk=None):
    if pk is None:
        messages.error(request,"Unabale to view Post")
        return redirect('home-page')
    else:
        category = Category.objects.filter(id=pk).first()
        context['page_title'] = category.name
        context['category'] = category
        posts = Post.objects.filter(category = category).all()
        context['posts'] = posts
    return render(request, 'by_categories.html',context)

def categories(request):
    categories = Category.objects.filter(status = 1).all()
    context['page_title'] = "Category Management"
    context['categories'] = categories
    return render(request, 'categories.html',context)

def contactus(request):
    countries = ['Afghanistan', 'Åland Islands', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bangladesh', 'Barbados', 'Bahamas', 'Bahrain', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'British Indian Ocean Territory', 'British Virgin Islands', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burma', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos (Keeling) Islands', 'Colombia', 'Comoros', 'Congo-Brazzaville', 'Congo-Kinshasa', 'Cook Islands', 'Costa Rica', '$_[', 'Croatia', 'Curaçao', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'El Salvador', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands', 'Faroe Islands', 'Federated States of Micronesia', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern Lands', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard and McDonald Islands', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macau', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn Islands', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Réunion', 'Romania',
     'Russia', 'Rwanda', 'Saint Barthélemy', 'Saint Helena', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin', 'Saint Pierre and Miquelon', 'Saint Vincent', 'Samoa', 'San Marino', 'São Tomé and Príncipe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Sint Maarten', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Georgia', 'South Korea', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Svalbard and Jan Mayen', 'Sweden', 'Swaziland', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Vietnam', 'Venezuela', 'Wallis and Futuna', 'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe']
    
    context['countries']=countries
    return render(request,'contactus.html',context )

def aboutus(request):
    return render(request,'aboutus.html' )





