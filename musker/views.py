from django.shortcuts import redirect, render, get_object_or_404
from .models import Profile, Tweet
from django.contrib import messages
from .forms import TweetForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


# Create your views here.
def home(request):

    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, "Your tweet has been posted!")
                return redirect("home")
                
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets": tweets, "form": form ,})
    else:
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets": tweets})

def profile_list(request):

    #query to user exclude the request user
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user = request.user)
        return render(request, 'profile_list.html', {'profiles': profiles})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')
    
def unfollow(request, pk):
    if request.user.is_authenticated:
        #Get the profile to unfollow
        profile = Profile.objects.get(user_id = pk)
        #Unfollow the user
        request.user.profile.follows.remove(profile)
        #Save our profile
        request.user.profile.save()

        messages.success(request, (f"You have successfully unfollowed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')
    
def follow(request, pk):
    if request.user.is_authenticated:
        #Get the profile to unfollow
        profile = Profile.objects.get(user_id = pk)
        #Unfollow the user
        request.user.profile.follows.add(profile)
        #Save our profile
        request.user.profile.save()

        messages.success(request, (f"You have successfully followed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')    

    
def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id = pk)
        tweets = Tweet.objects.filter(user_id = pk).order_by("-created_at")

        #Post Form Logic
        if request.method =="POST":
            #get current user
            current_user_profile = request.user.profile
            #Get form data
            action = request.POST['follow']
            #Decide to follow or unfollow
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            #Save the profile
            current_user_profile.save()

        return render(request, "profile.html", {"profile": profile, "tweets": tweets})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')
    
def followers(request, pk):
    #query to user exclude the request user
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id = pk )
            return render(request, 'followers.html', {'profiles': profiles})
        else:
            messages.success(request, ("That's not your page."))
            return redirect('home')
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')

def follows(request, pk):
#query to user exclude the request user
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id = pk )
            return render(request, 'follows.html', {'profiles': profiles})
        else:
            messages.success(request, ("That's not your page."))
            return redirect('home')
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')

def login_user(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been successfully logged in!")
            return redirect("home")
        else:
            messages.success(request,"There was an error loggin in. Please try again")
            return redirect("login")
    else:
        return render(request, "login.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logout.")
    return redirect("home")

def register_user(request):

    form = SignUpForm()

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password = password)
            login(request, user)
            messages.success(request, "You hava successfully registered.Welcome!")
            return redirect('home')

    return render(request, "register.html", {"form": form})

def update_user(request):

    if request.user.is_authenticated:
        current_user = User.objects.get(id = request.user.id)
        profile_user = Profile.objects.get(user__id = request.user.id)

        #Get Forms
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance = current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance = profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, "Your profile has been updated. ")
            return redirect('home')

        return render(request, "update_user.html", {'user_form': user_form, 'profile_form': profile_form})
    
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')

def tweet_like(request, pk):

    if request.user.is_authenticated:

        tweet = get_object_or_404(Tweet, id = pk)
        if tweet.likes.filter(id = request.user.id):
            tweet.likes.remove(request.user)
        else:
            tweet.likes.add(request.user)
        
        return redirect(request.META.get("HTTP_REFERER"))
    
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')
    
def tweet_show(request,pk):
    
    tweet = get_object_or_404(Tweet, id = pk)
    if tweet:
        return render(request, "show_tweet.html", {'tweet': tweet})
    else:
        messages.success(request, ("That tweet does not exist"))
        return redirect('home')
    
def delete_tweet(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id = pk)
        #Check to see if you own the meep
        if request.user.username == tweet.user.username:
            #Delete the tweet
            tweet.delete()
            messages.success(request, ("Your tweet has been deleted."))
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.success(request, ("You do not own that tweet."))
            return redirect('home')
    else:
        messages.success(request, ("Please log in to continue"))
        return redirect(request.META.get("HTTP_REFERER"))
    

def edit_tweet(request,pk):
    if request.user.is_authenticated:
        #Check to see if you own the meep
        tweet = get_object_or_404(Tweet, id = pk)
        if request.user.username == tweet.user.username:
            form = TweetForm(request.POST or None, instance = tweet)
            if request.method == "POST":
                if form.is_valid():
                    tweet = form.save(commit=False)
                    tweet.user = request.user
                    tweet.save()
                    messages.success(request, "Your tweet has been edited!")
                    return redirect("home")
            else:
                return render(request, "edit_tweet.html", {'form': form, 'tweet': tweet})

            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.success(request, ("You do not own that tweet."))
            return redirect('home')
    else:
        messages.success(request, ("Please log in to continue"))
        return redirect('home')
    
def search(request):
    if request.method == "POST":
        #Grab the form field input
        search = request.POST['search']
        #Search the database
        searched = Tweet.objects.filter(body__contains = search)

        return render(request, 'search.html', {'search': search, 'searched': searched,  })
    
    else:
        return render(request, 'search.html', {})

def search_user(request):
    if request.method == "POST":
        #Grab the form field input
        search = request.POST['search']
        #Search the database
        searched = User.objects.filter(username__contains = search)

        return render(request, 'search_user.html', {'search': search, 'searched': searched,  })
    
    else:
        return render(request, 'search_user.html', {})
    





    
