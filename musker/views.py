from django.shortcuts import redirect, render
from .models import Profile
from django.contrib import messages

# Create your views here.
def home(request):

    return render(request, 'home.html', {})

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

        return render(request, "profile.html", {"profile": profile})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')
