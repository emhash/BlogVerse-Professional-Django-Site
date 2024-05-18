from django.http import  HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import RegistrationForm , EditedPassChangeForm,CreatePostForm,CommentForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout , update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404 
from .models import Contents, Comment, MsgFromAdmin, SayToMe, UserProfile, Category
from django.db.utils import IntegrityError
from django.db import models
from django.utils.html import strip_tags

def temp(request):
    return render(request, "temp.html")

def home(request):
    category = request.GET.get('category')
    search_query = request.GET.get('searchpost')

    if category:
        all_post = Contents.objects.filter(category__name=category).order_by('-uploaded_at')
        

    elif search_query:
        all_post = Contents.objects.filter(title__icontains=search_query).order_by('-uploaded_at')
    else:
        
        all_post = Contents.objects.all().order_by('-uploaded_at')

    if request.method == 'GET':
        posttitle = request.GET.get('searchpost')
        if posttitle != None :
            all_post = Contents.objects.filter(title__icontains = posttitle)
        elif posttitle =='' or posttitle=='#':
            all_post = Contents.objects.all().order_by('-uploaded_at')

    # filter_nm_exmpl = list(Contents.objects.values_list('title', flat=True))


    # ----- Available Category Name -----------
    cat = list(set(Contents.objects.values_list('category__name', flat=True)))
    # print(cat)
    
    # ---------- x -----------


    #------ LOGIC FOR FILTER OUT THE POPULER POSTS OF EACH CATEGORY ------
   
    top_posts = []
    
    for category in cat:
        top_post = Contents.objects.filter(category__name=category).order_by('-views').first()

        top_posts.append(top_post)
    
    
    # print(top_posts)

    # ------------------------------  X ---------------------------------

    for post in top_posts:
        post.total_comments = Comment.objects.filter(content=post).count()

        # ---------LOGIC To see get the PURE description and calculate time ----------
        descript_text = strip_tags(post.descript)
        lenis = descript_text.replace(' ', '')
        # print(lenis)
        to_read = str((len(lenis) * (15/100)/60)).split('.')
        timeneeds = (f"{to_read[0]}.{(to_read[1])[:1]} min")
        
        
        # (*** THIS WAY ANOTHER MODELS VALUE OR OWN MODEL VALUE CAN CALCULATE AND NEWLY PASS TO EACH POSTS . IMP***)
        
        post.read_time = timeneeds

    for post in all_post:
        post.total_comments = Comment.objects.filter(content=post).count()

    paginator = Paginator(all_post, 20)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    e_d = {}
    for item in cat:
        count = Contents.objects.filter(category__name=item).order_by('-uploaded_at').count()
        e_d[item] = count

    # -- checking if dictiory print perfect or not --
    # for item, count in e_d.items():
    #     print(item, count)

    try:
        mymsg = list(MsgFromAdmin.objects.all()[:2])
    except:
        mymsg = []

    recent_comment = Comment.objects.all().order_by("created_at")[:7]
    home_content = {
        "5_recent":all_post[:5],
        "page_obj": page_obj,
        "categories": e_d,
        "top_posts": top_posts,
        "headlinetoday": mymsg[0] if mymsg else None,
        "msgtwo": mymsg[1] if len(mymsg) > 1 else None,
        "recent_comment":recent_comment,
    }


    
    return render(request, "home/index.html", context=home_content  )


# DONE
def dynamic_option(request, option):
    
    if option == 'make_post':
        return make_post(request)
    elif option == 'your_posts':
        return your_posts(request)
    elif option == 'your_profile':
        return your_profile(request)
    elif option == 'change_password':
        return change_password(request)
    else:
        return render(request, 'index.html')  # Handle invalid options

# like, dislike 
def artical_view(request, the_artical):
    content = get_object_or_404(Contents, slug=the_artical)
    # logic for read time 
    descript_text = strip_tags(content.descript)
    lenis = descript_text.replace(' ', '')
    # ------------ print(len(timeneed))
    # 100 --- 15s
    # 1 -- 15/100
    # len=140 --140*(15/100)
    # min = x/60s
    to_read = str((len(lenis) * (15/100)/60)).split('.')
    #------------- print(f"{to_read[0]}.{(to_read[1])[:1]} min")
    timeneed = (f"{to_read[0]}.{(to_read[1])[:1]} min")

    # the most viewed post
    most_viewed_post = Contents.objects.all().order_by('-views')[:6]
    
    
    comments = Comment.objects.filter(content=content)
    # print(content.views)
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            the_form = form.save(commit=False)
            the_form.content = content
            the_form.save()
            return redirect(request.path)
        
    else:
        form = CommentForm()

    # Assuming there's only one UserProfile instance associated with the article
    user_profile = content.user.userprofile

    context = {
        'categories':Category.objects.all(),
        'content': content,
        'posts': most_viewed_post,
        'user_profile': user_profile,
        # Other than profile- for show comments in HTML
        'all_comment': comments,
        'read' : timeneed,
        'form' : form,
    }


    content.views += 1
    content.save()
    # print(content.views)

    return render(request, 'home/artical.html', context)


def all_posts(request):
    category = request.GET.get('category')
    search_query = request.GET.get('searchpost')

    if category:
        all_post = Contents.objects.filter(category__name=category).order_by('-uploaded_at')
        

    elif search_query:
        all_post = Contents.objects.filter(title__icontains=search_query).order_by('-uploaded_at')
    else:
        
        all_post = Contents.objects.all().order_by('-uploaded_at')
    

    paginator = Paginator(all_post, 20)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    categories = Category.objects.all()
    context = {
        "page_obj":page_obj,
        "categories":categories,
        "top_5": None,
    }
    return render(request, "home/posts.html", context )






# ================ ++++++++ AUTHORIZATION +++++++++ ==================

# DONE
def Registration(request):
    if request.user.is_authenticated:
        return redirect('homes')
    else:
        if request.method == 'POST':
            reg_form = RegistrationForm(request.POST)
            if reg_form.is_valid():
                try:
                    # Save the user
                    user = reg_form.save()

                    # Create a UserProfile for the user
                    user_profile = UserProfile(user=user)
                    user_profile.save()

                    messages.success(request, "Congrats! Your account was created successfully.")
                    return redirect('the_login')

                except IntegrityError:
                    messages.error(request, "Username already exists. Please choose a different username.")
                    return redirect('the_signup')

        else:
            reg_form = RegistrationForm()

        context = {'form': reg_form}
        return render(request, 'auth/registation.html', context)

# DONE
def the_login(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('homes')

    if request.method == 'POST':
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in.")
                print("LOGIN DONE")
                return redirect('homes')  # Redirect to a success page, e.g., home
            else:
                messages.error(request, "Invalid username or password.")   
                print("Invalid")         

        '''BELOW ONE ALSO WORK AND THIS IS IN-BUILT'''

        # the_form = AuthenticationForm(request=request, data=request.POST)
        # if the_form.is_valid():
        #     user = the_form.get_user()
        #     login(request, user)
        #     messages.success(request, f"Hey {user.username}! Welcome to the BlogVerse. You can now manage your posts.")
        #     return redirect("homes")
        # else:
        #     messages.error(request, "Invalid username or password")
        #     return redirect('the_login')
    # else:
    #     the_form = AuthenticationForm()

    return render(request, 'auth/login.html') 

# Works 
def the_logout(request):
    logout(request)
    
    messages.success(request, "You have successfully logged out! and you have no longer access to perform any operation")

    return redirect('homes')

# ===================== ++++++++++ DASHBOARD ++++++++++ =================
# DONE 
@login_required
def the_dashb(request):
    def viewer_in_format(num):
        magnitudes = ['', 'K', 'M', 'G', 'T', 'P']
        mag = 0
        if num < 1000:
            return str(num)
        while num >= 1000:
            mag += 1
            num /= 1000
        return f"{num}{magnitudes[mag]}"

# FORMAT ALL NUMBERS IN 1k, 1M, 1B etc -->
   
    t_p = Contents.objects.filter(user=request.user).count()
    t_l = Contents.objects.filter(user=request.user).aggregate(total_likes=models.Sum('likes'))['total_likes'] or 0
    t_t = Contents.objects.filter(user=request.user).aggregate(total_views=models.Sum('views'))['total_views'] or 0
    t_dl = Contents.objects.filter(user=request.user).aggregate(total_views=models.Sum('dislikes'))['total_views'] or 0


    t_pst = viewer_in_format(t_p)
    ttl_likes = viewer_in_format(t_l)
    t_v = viewer_in_format(t_t)
    
    # print(f'answer  {viewer_in_format(t_v)}') 
    # t_v = Contents.objects.all()
    # print(t_p)

    profile_data = {
    'user': request.user,
    'profile_picture': request.user.userprofile.profile_picture.url,
    'bio_data': request.user.userprofile.bio_data,
    # ---------------------
    'ttl_pst' : t_pst,
    't_lk' : ttl_likes,
    't_v' : t_v,
    'ttl_dslk' : t_dl,
    
    }
    return render(request, 'dashboard.html', {'profile' : profile_data})


# DONE

@login_required
def make_post(request):
    previous_page = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            category_name = request.POST.get('category')
            if category_name is None or category_name == '':
                default_category = get_object_or_404(Category, name='Others')
                post.category = default_category
           
            post.user = request.user
            
            post.save()
            messages.success(request, "Congrats! Your post has been uploaded successfully.")
            return redirect('the_dashb')
    else:
        form = CreatePostForm()
    return render(request, 'make_post.html', {'form': form, 'previous_page': previous_page})



# DONE
@login_required
def your_posts(request):
    
    user_posts = Contents.objects.filter(user=request.user)
    # descr = Contents.objects.values_list('descript', flat=True)

    # print(descr)
    content = {
        'user_posts': user_posts,
        'profile': {
            'user': request.user,
            'profile_picture': request.user.userprofile.profile_picture.url,
            'bio_data': request.user.userprofile.bio_data,
            }
            # ---------------------

    }

    return render(request, 'your_posts.html', context=content)

# DONE
@login_required
def your_profile(request):

    profile = request.user.userprofile
    
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio_data = request.POST.get('bio_data')
        profile_picture = request.FILES.get('profile_picture')  # Get the uploaded file
        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()
        # Update user profile data
        request.user.first_name = first_name
        request.user.last_name = last_name
        profile.bio_data = bio_data
        request.user.save()
        profile.save()


    profile_data = {
        'user': request.user,
        'profile_picture': profile.profile_picture.url,
        'bio_data': profile.bio_data,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }

    context = {
        'profile': profile_data,
        
    }

    return render(request, 'your_profile.html', context)

# DONE
@login_required
def change_password(request):

    previous_page = request.META.get('HTTP_REFERER')
    
    if request.method == 'POST':
        form = EditedPassChangeForm(user = request.user, data = request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "your password has been successfully changed ! ".title())
    else:
        form = EditedPassChangeForm(request.user)

    alllll = {'form' : form, 
              'previous_page': previous_page,
              'profile': {'user': request.user,
                          'profile_picture': request.user.userprofile.profile_picture.url,
                          'bio_data': request.user.userprofile.bio_data,
                            # ---------------------
                            
                          }
            }

    
    return render(request, 'change_password.html' , context=alllll )


# DONE
@login_required
def edit_post(request, key):
    content = Contents.objects.get(slug=key)

    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Your chnages has been updated !")
            return redirect('the_dashb')
    else:
        form = CreatePostForm(instance=content)

    return render(request, 'edit.html', {'form': form, 'current_picture': content.picture})


# DONE
@login_required
def delete_post(request, slug):
    post = get_object_or_404(Contents, slug=slug, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('your_posts')
    else:
        # Handle GET request if needed
        pass


# DONE
def feedback(request):
    if request.method == "POST":
        your_data = SayToMe(
            name_is=request.POST.get('name_is'),
            saying=request.POST.get('saying')
        )
        messages.success(request, "Your feedback or your message has reached us. Thank you.")
        your_data.save()
        return redirect('homes')
    return render(request, 'about.html')



def f404(request, slg):
    # print(slg)
    if slg == 'dashboard':
        return the_dashb(request)
    if slg == 'donttrytohackadminpagethis-is-the-universal-admin-panel-lol':
        return redirect('eha/donttrytohackadminpagethis-is-the-universal-admin-panel-lol/')
    if slg == 'logout':
        logout(request)
        messages.success(request, "You have successfully logged out! and you have no longer access to perform any operation")
        return redirect('homes')
    if slg == 'login':
        return the_login(request)
    if slg == 'registration':
        return Registration(request)
    if slg == 'contact':
        return feedback(request)
    else:
        return render(request, 'home/404.html', status=404)
    
# Below all are temprory for checking purpose


# This is old Edit post function, 
