from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import PostForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import requests
from .models import Location, Userprofile, Follow, Post, Likes,Comment
from django.db import connection
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from itertools import chain

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
            connections = Follow.objects.all().filter(follower=request.user)
            connections_list = []
            for connection in connections:
                connections_list.append(connection.user.id)

            near_by_users = get_nearby_users(request,"kannur",connections_list)
            
        posts = get_posts(request)
        notifications = get_notifications(request)
       
        context = {'form':form,"near_by_users":near_by_users,"posts":posts,"connections":connections_list,"notifications" : notifications,}
        return render(request,'insta/feed.html',context)
    else:
        return redirect('accounts/login')
def get_posts(request):
    sql="""select * from insta_post 
           where user_id = """+str(request.user.id)+""" or user_id in
           (select user_id from insta_follow where follower_id = """+str(request.user.id)+""")"""
    #posts = Post.objects.select_related('user_id')
    with connection.cursor() as cursor:


        print(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        paginator = Paginator(rows, 20)
        page_number = request.GET.get('page',1)
        page_obj = paginator.get_page(page_number)
    #posts = Post.objects.filter(follows_follower=request.user.id)
    print("----")
    #print(page_obj)
    posts = {}
    i = 0
    liked_val = False
    for postval in page_obj:
        print("****")
        print(postval)
        print("******")
        post_id_val = postval[0]
        liked = get_like_status(request,post_id_val)
        if(liked):
            liked_val = True
        
        print(liked_val)
        post_user = User.objects.get(pk=postval[7])
        posts[i] = {'id': post_id_val,'image': postval[1],'caption': postval[2],'liked':liked_val,'post_user' : post_user,}
        i += 1
    return posts
    

   # filter(follow__follower_id_id=request.user)
def get_like_status(request,id):
    try:
        liked = Likes.objects.get(post_id=id)
        if liked:
            
            print(liked)
            
            return liked
    except:
        return False


def get_location(request,name):
    location_name = name
    api_url = "https://api.opencagedata.com/geocode/v1/json?key=3fe48045b93f40d0a7abcefa54689931&q="+name

    response = requests.get(api_url)
    geodata = response.json()
    
    if(geodata['results']):
        data = geodata['results'][0]
        name = data['formatted']
        lattitude = data['geometry']['lat']
        longitude = data['geometry']['lng']
        continent = data['components']['continent']
        country_code = data['components']['country_code']
        country = data['components']['country']
        state = data['components']['state']
        postcode = data['components']['postcode']
        county = data['components']['county']
        location = Location.objects.get_or_create(name=name,lattitude=lattitude,longitude=longitude)
        if type(location == 'tuple'):
            location = location[0]
        
        # location.continent = continent
        # location.country_code = country_code
        # location.country = country
        # location.state = state
        # location.postcode = postcode
        # location.county = county
        # location.save()
        user = request.user
        #current_user = requ 
        user_profile = Userprofile.objects.create(user = user,location=location,profile_name=request.user.username)
        user_profile.save()
    else :
        return False
    
    # return render(request, 'core/home.html', {
    #     'ip': geodata['ip'],
    #     'country': geodata['country_name']
    # })

def get_nearby_users(request,locations,connections_list):
    locs = Location.objects.raw('SELECT id, name,( 6371 * acos ( cos ( radians(11.8762254) ) * cos( radians( lattitude ) ) * cos( radians( longitude ) - radians(75.3738043) ) + sin ( radians(11.8762254) ) * sin( radians( lattitude ) ))) AS distance FROM insta_location ORDER BY distance LIMIT 20')
    near_by_user_dict = {}
    i = 0  
    for loc in locs:
        ups = Userprofile.objects.all().filter(location=loc.id).exclude( user = request.user)
        for up in ups:
            if up.user_id not in connections_list:
                near_by_user_dict[i] = {'profile' : up.profile_name,"id": up.user_id,"location":up.location.name}
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
    follower = Follow.objects.get_or_create(user=follow_user,follower=follower,is_accepted=is_accepted)
    return HttpResponse({"data":"success"})

def likeme(request):
    print (request.POST)
    userid = request.user
    post_id = request.POST['post_id']
    unlike= request.POST['unlike']
    print("----unlike------")
    print(unlike)
    print("----------")
    if unlike == 'unlike' :

        Likes.objects.filter(post_id=post_id,user=userid).delete()
    else :
        likes = Likes.objects.get_or_create(read_by_owner=0,post_id=post_id,user=userid)
    return HttpResponse({"data":"success"})

def comment(request):
    print("in comment.....")
    user = request.user
    postVal = request.POST['post_id']
    comment_val = request.POST['comment_val']
    commented = Comment.objects.get_or_create(user=user,post_id = postVal,comment_body=comment_val)
    return HttpResponse({"data":"success"})


def get_notifications(request):
#     sql = """SELECT l.user_id as liked_user, c.user_id as commented_user 
# from 
# insta_likes l, insta_comment c, insta_post p 
# WHERE
# (l.post_id = p.id 
# OR 
# c.post_id = p.id)
# AND
# p.user_id = 3
# """

    likes = Likes.objects.filter(post__user = request.user)
    comments = Comment.objects.filter(post__user = request.user)
    follows = Follow.objects.filter(user = request.user)
    result_list = sorted(
    chain(likes, comments, follows),
    key=lambda instance: instance.created_time)


    notifications = form_notification(result_list)
    return notifications

def form_notification(results):
    i = 0 
    notification = {}
    for result in results :
        notification[i] = {'type' :result.__str__(),"result" : result}
        i+= 1
    return notification