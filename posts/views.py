from django.http import HttpResponse, HttpResponseRedirect, Http404
from urllib.parse import quote_plus
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from .models import Post
from .forms import PostForm
from comments.forms import CommentForm
from comments.models import Comment
from django.db.models import Q
from django.utils import translation




def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		messages.success(request, 'Post is Successfully created.')
		return HttpResponseRedirect(instance.get_absolute_url())
	elif form.errors:
		messages.error(request, 'Post is not successfully created.')
	else:
		pass
	context = {"form":form, "sub":"Create Post"}
	return render(request, "post_form.html", context)

def post_detail(request, slug=None):
	instance = get_object_or_404(Post, slug=slug)
	if instance.publish > timezone.now().date() or instance.draft:
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string = quote_plus(instance.content)

	initial_data = {
		"content_type":instance.get_content_type,
		"object_id":instance.id
	}

	form = CommentForm(request.POST or None, initial=initial_data)	
	if form.is_valid():
		c_type = form.cleaned_data.get("content_type")
		content_type = ContentType.objects.get(model=c_type)
		obj_id = form.cleaned_data.get("object_id")
		content_data = form.cleaned_data.get("content")
		new_comment, created = Comment.objects.get_or_create(
										user = request.user,
										content_type = content_type,
										object_id = obj_id,
										content = content_data
			)

	#content_type = ContentType.objects.get_for_model(Post)
	#obj_id = instance.id
	comments = instance.comments#Comment.objects.filter_by_instance(instance)
	comments_count = comments.count()

	context = {'title': instance.title, 'instance':instance, 'comments':comments, 'comments_count':comments_count, 'comment_form':form}#'share_string':share_string
	return render(request, "post_detail.html", context)

def post_list(request):
	'''
	if request.user.is_authenticated():
		context = {'title':'My user list'}
	else:
		'''
	today = timezone.now().date()
	query_list = Post.objects.active()#filter(publish__lte=timezone.now())#.order_by("-timestamp", "-updated")
	#lte = less than equal to # .active() see models 
	if request.user.is_staff or request.user.is_superuser:
		query_list = Post.objects.all()
	
#search fields
	q = request.GET.get('q')

	if q:
		query_list = query_list.filter(
			Q(title__icontains=q)|
			Q(content__icontains=q)|
			Q(user__first_name__icontains=q)|
			Q(user__last_name__icontains=q)
			).distinct()
#search fields
	paginator = Paginator(query_list, 5)
	page = request.GET.get('page')
	try:
	    query = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    query = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    query = paginator.page(paginator.num_pages)

	context = {'title':'List', 'queryset':query, 'today':today}	
	return render(request, "post_list.html", context)

def listing(request):
    contact_list = Contacts.objects.all()
    paginator = Paginator(contact_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'list.html', {'contacts': contacts})
	

def post_update(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser: 
		raise Http404
		#prevents user from doing anything if he is not admin or rergistered user
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, 'Post is Successfully updated and saved.')
		return HttpResponseRedirect(instance.get_absolute_url())
	elif form.errors:
		messages.error(request, 'Post is not updated or saved.')
	else:
		pass
	context = {"title":instance.title, "form":form, "instance":instance, "sub":"Update Post"}	
	return render(request, "post_form.html", context)

def post_delete(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, 'Post is successfully deleted.')
	return redirect("posts:list")