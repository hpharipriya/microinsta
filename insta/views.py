from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import PostForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import requests
from .models import Location, Userprofile, Follow, Post
from django.db import connection
from django.contrib.auth.models import User

# Create your views here.

def add(request):
    return render(request,'insta/feed.html')
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            print(form.cleaned_data)
            print(request.POST)
            user = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            location = request.POST['location']
            user = authenticate(username=user,password=password)
            login(request,user)
            get_location(request,location)
            return redirect('index')
    else:
        form = UserCreationForm()
    context = {'form':form}
    return render(request,'registration/register.html', context)
def index(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST,request.FILES,user=request.user)
            if form.is_valid():
                postModel = form.save()
                imagepath = form.cleaned_data['image']
                caption = form.cleaned_data['caption']
                print(imagepath)
                print(caption)
                uploadDict = {}
                uploadDict['imagepath'] = imagepath
                uploadDict['caption'] = caption
                print(uploadDict)
                context = {'uploadedValues':uploadDict}
                #return redirect('index')
                return render(request,'insta/feed.html',context)
            else:
                print(form.errors)
        else:
            form = PostForm(user=request.user)
            near_by_users = get_nearby_users(request,"kannur")
            posts = get_posts(request)
        context = {'form':form,"near_by_users":near_by_users,}
        return render(request,'insta/feed.html',context)
    else:
        return redirect('accounts/login')
def get_posts(request):
    #sql="select * from post where user_id_id in (select user_id from follow where floower_id = request.user.id"
    #posts = Post.objects.select_related('user_id')
    with connection.cursor() as cursor:
        sql = "select * from insta_post left join insta_follow on insta_post.user_id_id = insta_follow.user_id_id where (insta_post.user_id_id = "+str(request.user.id) +") or  (insta_follow.follower_id_id =" + str(request.user.id) +") order by insta_post.created_at desc" 
        print(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
    #posts = Post.objects.filter(follows_follower=request.user.id)
    print("----")
    print(rows)
    for post in rows:
        print(post)
    print("-----")
   # filter(follow__follower_id_id=request.user)

def get_location(request,name):
    location_name = name
    api_url = "https://api.opencagedata.com/geocode/v1/json?key=3fe48045b93f40d0a7abcefa54689931&q="+name

    response = requests.get(api_url)
    geodata = response.json()
    data = geodata['results'][0]
    if(data):
        name = data['formatted']
        lattitude = data['geometry']['lat']
        longitude = data['geometry']['lng']
        continent = data['components']['continent']
        country_code = data['components']['country_code']
        country = data['components']['country']
        state = data['components']['state']
        postcode = data['components']['postcode']
        county = data['components']['county']
        location = Location.objects.create(name=name,lattitude=lattitude,longitude=longitude)
        location.continent = continent
        location.country_code = country_code
        location.country = country
        location.state = state
        location.postcode = postcode
        location.county = county
        location.save()
        userid = request.user
        #current_user = requ 
        user_profile = Userprofile.objects.create(user_id = userid,location=location,profile_name=request.user.username)
        user_profile.save()
    else :
        return False
    
    # return render(request, 'core/home.html', {
    #     'ip': geodata['ip'],
    #     'country': geodata['country_name']
    # })

def get_nearby_users(request,locations):
    locs = Location.objects.raw('SELECT id, name,( 6371 * acos ( cos ( radians(11.8762254) ) * cos( radians( lattitude ) ) * cos( radians( longitude ) - radians(75.3738043) ) + sin ( radians(11.8762254) ) * sin( radians( lattitude ) ))) AS distance FROM insta_location ORDER BY distance LIMIT 0 , 20')
    near_by_user_dict = {}
    i = 0 
    for loc in locs:
        ups = Userprofile.objects.all().filter(location=loc.id).exclude( user_id = request.user)
        for up in ups:
            near_by_user_dict[i] = {'profile' : up.profile_name,"id": up.user_id_id}
            
        i = i+1
    return near_by_user_dict

def follow(request):
    userid = request.user.id
    print (request.POST['follow_id'])
    follow_id = request.POST['follow_id']

    follow_user = User.objects.get(pk=follow_id)
    follower = User.objects.get(pk=userid)

    up = Userprofile.objects.get(user_id=follow_id)
    if up.is_public :
        is_accepted = True
    else:
        is_accepted = False
    follower = Follow.objects.create(user_id=follow_user,follower_id=follower,is_accepted=is_accepted)
    return HttpResponse({"data":"success"})
