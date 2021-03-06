from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.db.models.functions import Lower
from django.http import JsonResponse

from .models import Video, Comment
from .forms import VideoForm, CommentForm
from .admin import CommentAdmin
from members.models import Member


@login_required
def training_videos(request):
    """This view renders the videos available to paid subscribers"""
    if request.user.member.subscription_package:
        if request.user.member.subscription_package.id == 1:
            videos = Video.objects.filter(premium=False)
        else:
            videos = Video.objects.all()
        query = None
        sort = None
        direction = None

        if request.GET:
            if 'sort' in request.GET:
                sortkey = request.GET['sort']
                sort = sortkey
                if sortkey == 'title':
                    sortkey == 'lower_title'
                    videos = videos.annotate(lower_title=Lower('title'))
                if 'direction' in request.GET:
                    direction = request.GET['direction']
                    if direction == 'desc':
                        sortkey = f'-{sortkey}'
                videos = videos.order_by(sortkey)

            if 'q' in request.GET:
                query = request.GET['q']
                user = request.user
                if not query:
                    messages.error(request, "You didn't enter any search "
                                   "terms")
                    return redirect(reverse('training_videos'))

                queries = Q(title__icontains=query) | Q(name__icontains=query) | Q(description__icontains=query)
                videos = videos.filter(queries)

        sort_by = f'{sort}_{direction}'

        context = {
            'videos': videos,
            'search_term': query,
            'sort_by': sort_by,
        }
        return render(request, 'videos/videos.html', context)
    else:
        messages.error(request, 'Sorry, you must have a subscription to view '
                       'this page.')
        return redirect(reverse('home'))


@login_required
def add_video(request):
    """This view lets the admin add a new video to the app for"""
    """paid subscribers to view"""
    if request.user.is_superuser:
        if request.method == 'POST':
            form = VideoForm(request.POST, request.FILES)
            if form.is_valid():
                user = request.user
                new_video = form.save()
                messages.success(request, f'Video "{new_video.title}" '
                                 'successfully created.')
                return redirect(reverse('video_details', args=[new_video.id]))
            else:
                messages.error(request, 'Sorry, there was an error updating '
                               'the information. Please ensure all fields '
                               'are filled out correctly.')
        else:
            form = VideoForm()
    else:
        messages.error(request, 'Sorry, you do not have permission to view '
                       'this page.')
        return redirect(reverse('home'))
    template = 'videos/add_video.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def video_details(request, video_id):
    if request.user.member.subscription_package:
        video = get_object_or_404(
            Video.objects.annotate(average_rating=Avg('rating')), pk=video_id)
        if video.premium:
            if request.user.member.subscription_package.id == 1:
                messages.error(request, 'Sorry, this video is only available '
                               'to premium members. Please purchase a '
                               'premium or VIP subscription to view this '
                               'video.')
                return redirect(reverse('training_videos'))

        comments = video.comments.filter(approved=True).order_by('-created_on')
        unapproved_comments = video.comments.filter(approved=False)
        new_comment = None
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.video = video
                new_comment.user = request.user
                new_comment.save()
                messages.success(request, 'Your comment was successfully '
                                 'submitted. It will appear beside the '
                                 'video once it has been approved by an '
                                 'administrator.')
            else:
                messages.error(request, 'Thre was an issue submitting your '
                               'comment. Please ensure you have filled '
                               'out the form correctly.')
        else:
            comment_form = CommentForm()

        template = 'videos/video_details.html'
        context = {
            'video': video,
            'new_comment': new_comment,
            'comments': comments,
            'unapproved_comments': unapproved_comments,
            'comment_form': comment_form,
        }
        return render(request, template, context)
    else:
        messages.error(request, 'Sorry, you are not authorised to view this '
                       'page.')
        return redirect(reverse('home'))


@login_required
def edit_video(request, video_id):
    """This view lets the admin make changes to a video in the app"""
    """such as changing its name, description or the file itself"""
    if request.user.is_superuser:
        video = get_object_or_404(Video, pk=video_id)
        if request.method == 'POST':
            form = VideoForm(request.POST, request.FILES, instance=video)
            user = request.user
            if form.is_valid():
                form.save()
                messages.success(request, 'The video information was '
                                 'successfully updated.')
                return redirect(reverse('training_videos'))
            else:
                messages.error(request, 'Sorry, there was an error updating '
                               'the information. Please ensure all fields '
                               'are filled out correctly.')
        else:
            form = VideoForm(instance=video)
    else:
        messages.error(request, 'Sorry, you do not have permission to view '
                       'this page.')
        return redirect(reverse('home'))

    template = 'videos/edit_video.html'
    context = {
        'form': form,
        'video': video,
    }
    return render(request, template, context)


@login_required
def delete_video(request, video_id):
    """This view lets the admin delete a video from the app"""
    if request.user.is_superuser:
        user = request.user
        video = get_object_or_404(Video, pk=video_id)
        video.delete()
        messages.success(request, f'Successfully deleted "{video.title}" ')
        return redirect(reverse('training_videos'))
    else:
        messages.error('Sorry, you do not have permission to view this page.')
        return redirect(reverse('home'))


def videos_autocomplete(request):
    if request.is_ajax():
        query = request.GET.get('term', '')
        videos = Video.objects.filter(title__icontains=query)
        video_suggestions = []
        for video in videos:
            place_json = video.title
            video_suggestions.append(place_json)
        data = json.dumps(video_suggestions)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@login_required
def rate_video(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        value = request.POST.get('val')
        video = Video.objects.get(id=video_id)
        video.rating = value
        video.save()
        return JsonResponse({'success': 'true', 'rating': value}, safe=False)
    return JsonResponse({'success': 'false'})


@login_required
def approve_comment(request, comment_id, video_id):
    if request.user.is_superuser:
        comment = get_object_or_404(Comment, pk=comment_id)
        video = get_object_or_404(Video, pk=video_id)
        comment.approved = True
        comment.save()
        messages.success(request, 'Successfully approved comment.')
        return redirect(reverse('video_details', args=[video.id]))
    else:
        messages.error(request, 'Sorry, you do not have permission to '
                       'perform this action.')
        return redirect(reverse('home'))


@login_required
def reject_comment(request, comment_id, video_id):
    if request.user.is_superuser:
        comment = get_object_or_404(Comment, pk=comment_id)
        video = Video.objects.get(id=video_id)
        comment.delete()
        messages.success(request, 'The comment was successfully rejected.')
        return redirect(reverse('video_details', args=[video.id]))
    else:
        messages.error(request, 'Sorry, you do not have permission to '
                       'perform that action.')
        return redirect(reverse('home'))


@login_required
def update_comment(request, comment_id, video_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    video = get_object_or_404(Video, pk=video_id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES, instance=comment)
        if comment_form.is_valid():
            updated_comment = comment_form.save(commit=False)
            updated_comment.approved = False
            updated_comment.save()
            messages.success(request, 'Your comment was successfully updated.'
                             ' All edited comments must be re-approved by '
                             'administrators. Your comment will re-appear '
                             'on the page once it has been approved.')
            return redirect(reverse('video_details', args=[video.id]))
        else:
            messages.error(request, 'Sorry, there was an error updating '
                           'your comment. Please ensure everything is '
                           'filled out correctly.')
            return redirect(reverse('video_details', args=[video.id]))
    else:
        comment_form = CommentForm(instance=comment)

    template = 'videos/edit_comment.html'
    context = {
        'comment_form': comment_form,
        'comment': comment,
        'video': video,
    }
    return render(request, template, context)


@login_required
def delete_comment(request, comment_id, video_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user.is_superuser:
        video = Video.objects.get(id=video_id)
        comment.delete()
        messages.success(request, 'The comment was successfully deleted.')
        return redirect(reverse('video_details', args=[video.id]))
    elif comment.user == request.user:
        video = Video.objects.get(id=video_id)
        comment.delete()
        messages.success(request, 'Your comment was successfully deleted.')
        return redirect(reverse('video_details', args=[video.id]))
    else:
        messages.error(request, 'Sorry, you do not have permission to '
                       'perform that action.')
        return redirect(reverse('home'))
