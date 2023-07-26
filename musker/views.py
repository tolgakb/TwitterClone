from django.shortcuts import redirect, render
from .models import Profile, Tweet
from django.contrib import messages
from .forms import TweetForm

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
        return render(request, 'home.html', {"tweets": tweets, "form": form})
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
