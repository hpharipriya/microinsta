from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import PostForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import requests
from .models import Location, Userprofile
from django.db import connection
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
            
        context = {'form':form}
        return render(request,'insta/feed.html',context)
    else:
        return redirect('accounts/login')


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
        get_nearby_users(county)
    else :
        return False
    
    # return render(request, 'core/home.html', {
    #     'ip': geodata['ip'],
    #     'country': geodata['country_name']
    # })

def get_nearby_users(location):
    locs = Location.objects.raw('SELECT id, name,( 6371 * acos ( cos ( radians(11.8762254) ) * cos( radians( lattitude ) ) * cos( radians( longitude ) - radians(75.3738043) ) + sin ( radians(11.8762254) ) * sin( radians( lattitude ) ))) AS distance FROM insta_location ORDER BY distance LIMIT 0 , 20')
    for loc in locs:
        ups = Userprofile.objects.all().filter(location=loc.id)
        for up in ups:
            print(up.profile_name)
    pass

