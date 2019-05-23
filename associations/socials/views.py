from socials.models import Social, Comment, Fav

from django.views import View
from django.views import generic
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.files.uploadedfile import InMemoryUploadedFile

from socials.util import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from socials.forms import CreateForm, CommentForm

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

class SocialView(OwnerListView):
    model=Social
    template_name="social.html"

class SocialListView(OwnerListView):
    model = Social
    template_name = "social_list.html"

class SocialDetailView(OwnerDetailView):
    model = Social
    template_name = "social_detail.html"

    def get(self, request, pk) :
        social = Social.objects.get(id=pk)
        comments = Comment.objects.filter(social=social).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'social' : social, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

# class SocialCreateView(OwnerCreateView):
#     model = Social
#     fields = ['title', 'text', 'price']
#     template_name = "social_form.html"

# class SocialUpdateView(OwnerUpdateView):
#     model = Social
#     fields = ['title', 'text']
#     template_name = "social_form.html"

class SocialDeleteView(OwnerDeleteView):
    model = Social
    template_name = "social_delete.html"

class SocialCreateView(LoginRequiredMixin, View):
    template = 'social_form.html'
    success_url = reverse_lazy('socials')
    def get(self, request, pk=None) :
        form = CreateForm()
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)

class SocialUpdateView(LoginRequiredMixin, View):
    template = 'social_form.html'
    success_url = reverse_lazy('socials')
    def get(self, request, pk) :
        pic = get_object_or_404(Social, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        pic = get_object_or_404(Social, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)

def stream_file(request, pk) :
    social = get_object_or_404(Social, id=pk)
    response = HttpResponse()
    response['Content-Type'] = social.content_type
    response['Content-Length'] = len(social.picture)
    response.write(social.picture)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Social, id=pk)
        comment_form = CommentForm(request.POST)

        comment = Comment(text=request.POST['comment'], owner=request.user, social=f)
        comment.save()
        return redirect(reverse_lazy('social_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        social = self.object.social
        return reverse_lazy('social_detail', args=[social.id])

class ThingListView(OwnerListView):
    model = Social
    template_name = "social_list.html"

    def get(self, request) :
        social_list = Social.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}]  (A list of rows)
            rows = request.user.favorite_socials.values('id')
            favorites = [ row['id'] for row in rows ]
        ctx = {'social_list' : social_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)


@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Social, id=pk)
        fav = Fav(user=request.user, social=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Social, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, social=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
