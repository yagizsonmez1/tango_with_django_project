from django.shortcuts import render, redirect
from django.urls import reverse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
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
    if request.session.test_cookie_worked(): 
        print("TEST COOKIE WORKED!") 
        request.session.delete_test_cookie()

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

@login_required
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

@login_required
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
  registered = False
  if request.method == 'POST':
    user_form = UserForm(request.POST)
    profile_form = UserProfileForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save()
        user.set_password(user.password)
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        if 'picture' in request.FILES:
          profile.picture = request.FILES['picture']
        profile.save()
        registered = True
    else:
        print(user_form.errors, profile_form.errors)
  else:
      user_form = UserForm()
      profile_form = UserProfileForm()
  return render(request, 'rango/register.html',
                context = {'user_form': user_form,
                            'profile_form': profile_form,
                            'registered': registered})

def user_login(request):
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(username=username, password=password)
      if user:
          if user.is_active:
            login(request, user)
            return redirect(reverse('rango:index'))
          else:
              return HttpResponse("Your Rango account is disabled.")
      else:
        print(f"Invalid login details: {username}, {password}")
        return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
  return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
  # Since we know the user is logged in, we can now just log them out.
  logout(request)
  # Take the user back to the homepage.
  return redirect(reverse('rango:index'))

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

          

    