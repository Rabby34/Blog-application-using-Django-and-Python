from django.shortcuts import render

from app.models import Post,Comment,Tag,Profile,WebsiteMeta
from app.forms import CommentForm,SubscribeForm,NewUserForm

from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib import messages

from django.contrib.auth.models import User
from django.db.models import Count
# Create your views here.

from django.shortcuts import redirect
from django.contrib.auth import login

from django.shortcuts import get_object_or_404

def post_page(request,slug):
    post = Post.objects.get(slug=slug)
    comments=Comment.objects.filter(post=post,parent=None)
    form = CommentForm()

    # bookmark logic
    bookmarked=False
    if post.bookmarks.filter(id=request.user.id).exists():
        bookmarked=True
    is_bookmarked=bookmarked

    # like logic
    liked=False
    if post.likes.filter(id=request.user.id).exists():
        liked=True
    number_of_likes=post.number_of_likes()
    post_is_liked=liked

    if request.POST:
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid:
            parent_obj=None
            if request.POST.get('parent'):
                parent=request.POST.get('parent')
                parent_obj=Comment.objects.get(id=parent)
                if parent_obj:
                    comment_reply=comment_form.save(commit=False)
                    comment_reply.parent=parent_obj
                    comment_reply.post=post
                    comment_reply.save()
                    return HttpResponseRedirect(reverse('post_page',kwargs={'slug':slug}))

            else:
                comment=comment_form.save(commit=False)
                postid=request.POST.get("post_id")
                post=Post.objects.get(id=postid)
                comment.post=post
                comment.save()
                return HttpResponseRedirect(reverse('post_page',kwargs={'slug':slug}))
    
    if post.view_count is None:
        post.view_count=1
    else:
        post.view_count=post.view_count+1
    post.save()

    recent_posts = Post.objects.exclude(id=post.id).order_by('-last_updated')[0:3]
    top_authors =  User.objects.annotate(number=Count('post')).order_by('-number').exclude(number=0)
    tags  = Tag.objects.all()
    related_posts = Post.objects.exclude(id=post.id).filter(author=post.author)[0:3]

    context={'post':post,'form':form,'comments':comments,'is_bookmarked':is_bookmarked,'number_of_likes':number_of_likes,
             'post_is_liked':post_is_liked,'recent_posts':recent_posts,'top_authors':top_authors,'tags':tags,'related_posts':related_posts}
    return render(request,'app/post.html',context)

def index(request):
    posts = Post.objects.all()[0:3]
    top_posts = Post.objects.all().order_by('-view_count')[0:3]
    recent_posts = Post.objects.all().order_by('-last_updated')[0:3]
    subscribe_form = SubscribeForm()
    website_info = None

    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]

    featured_post = Post.objects.filter(is_featured=True)
    if featured_post:
        featured_post=featured_post.order_by('-last_updated')[0]

    if request.POST:
        subscribe_form = SubscribeForm(request.POST)
        if subscribe_form.is_valid:
            subscribe_form.save()
            request.session['subscribed']=True
            subscribe_form=SubscribeForm()
            messages.success(request,'Thank you for subscribing..')
            return HttpResponseRedirect(reverse('home_page'))

    else:
        subscribe_form=SubscribeForm()
    context = {'posts':posts,"top_posts":top_posts,'recent_posts':recent_posts,'subscribe_form':subscribe_form,'featured_post':featured_post,'website_info':website_info}
    return render(request,'app/index.html',context)


def tag_page(request,slug):
    tag = Tag.objects.get(slug=slug)
    top_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:2]
    recent_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-last_updated')[0:3]
    tags = Tag.objects.all()

    context={'tag':tag,'top_posts':top_posts,'recent_posts':recent_posts,'tags':tags}
    return render(request,'app/tag.html',context)

def author_page(request,slug):
    profile = Profile.objects.get(slug=slug)
    top_posts = Post.objects.filter(author=profile.user).order_by('-view_count')[0:2]
    recent_posts = Post.objects.filter(author=profile.user).order_by('-last_updated')[0:3]
    # top_posts = Post.objects.annotate(number=Count('view_count')).order_by('-number')[0:2]
    # recent_posts = Post.objects.order_by('-last_updated')[0:3]
    top_authors = User.objects.annotate(number=Count('post')).order_by('-number').exclude(number=0)


    context={'profile':profile,'top_posts':top_posts,'recent_posts':recent_posts,'top_authors':top_authors}
    return render(request,'app/author.html',context)

def search_posts(request):
    search_query=''
    if request.GET.get('q'):
        search_query = request.GET.get('q')
    posts = Post.objects.filter(title__icontains=search_query)
    context = {'posts':posts,'search_query':search_query}
    return render(request,'app/search.html',context)

def about(request):
    website_info = None

    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]

    context = {'website_info':website_info}
    return render(request,'app/about.html',context)

def register_user(request):
    form=NewUserForm()
    if request.method=="POST":
        form=NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("/")

    context={'form':form}
    return render(request,'registration/registration.html',context)

def bookmark_post(request,slug):
    post=get_object_or_404(Post,id=request.POST.get('post_id'))
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return HttpResponseRedirect(reverse('post_page',args=[str(slug)]))

def like_post(request,slug):
    post=get_object_or_404(Post,id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_page',args=[str(slug)]))

def all_bookmarked_posts(request):
    all_bookmarked_posts = Post.objects.filter(bookmarks=request.user)
    context={'all_bookmarked_posts':all_bookmarked_posts}
    return render(request,'app/all_bookmarked_posts.html',context)

def all_posts(request):
    all_posts = Post.objects.all()
    context={'all_posts':all_posts}
    return render(request,'app/all_posts.html',context)

def all_liked_posts(request):
    all_liked_posts = Post.objects.filter(likes=request.user)
    context={'all_liked_posts':all_liked_posts}
    return render(request,'app/all_liked_posts.html',context)