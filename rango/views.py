from django.shortcuts import render, redirect
from django.urls import reverse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

from django.contrib.auth import authenticate, login 
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

def index(request):
    # Query the top 5 categories by likes
    category_list = Category.objects.order_by('-likes')[:5]

    # Query the top 5 pages by views
    page_list = Page.objects.order_by('-views')[:5]

    # Create a context dictionary to pass to the template
    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': category_list,
        'pages': page_list,
    }

    # Return a rendered response to send to the client
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html',{})

def show_category(request, category_name_slug):
    # Create a context dictionary to pass to the template
    context_dict = {}

    try:
        # Find the category with the given slug
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all associated pages, ordered by title
        pages = category.page_set.all().order_by('title')
        # Add the pages and category to the context
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        # If the category doesn't exist, set context to None
        context_dict['category'] = None
        context_dict['pages'] = None

    # Render the response
    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            # Redirect to the index page using reverse()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        # Find the category with the given slug
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        # If the category doesn't exist, redirect to the index page
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                # Save the page with the associated category
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                # Redirect to the category page using reverse()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    # Add the form and category to the context
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to 
    # True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information. 
        # Note that we make use of both UserForm and UserProfileForm. 
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid(): 
            # Save the user's form data to the database. 
            user = user_form.save()

            # Now we hash the password with the set_password method. 
            # Once hashed, we can update the user object. 
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and 
            # put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to indicate that the template # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal. 
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances. 
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    # Render the template depending on the context.
    return render(request, 'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})

def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

 #Use the login_required() decorator to ensure only those logged in can 
 # access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))


def user_login(request):
# If the request is a HTTP POST, try to pull out the relevant information. 
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>'] # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')


        # Use Django's machinery to attempt to see if the username/password 
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user 
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
            # If the account is valid and active, we can log the user in. 
            #We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
        # Bad login details were provided. So we can't log the user in. 
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

# The request is not a HTTP POST, so display the login form.
# This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the # blank dictionary object...
        return render(request, 'rango/login.html')



    
