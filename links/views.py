# Create your views here.
import re
from .models import Link, Vote, UserProfile
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from .forms import UserProfileForm, LinkForm, VoteForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest
#from registration.backends.simple.views import RegistrationView

#class MyRegistrationView(RegistrationView):
#    def get_success_url(self, request, user):
#        return '/'

class LinkDetailView(DetailView):
    model = Link

class LinkListView(ListView):
    model = Link
    queryset = Link.with_votes.all() #by default, query_set was equal to: Link.objects.all(). We're overriding that to call "with_votes defined in models.py"
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super(LinkListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            voted = Vote.objects.filter(voter=self.request.user) #all links user voted on
            links_in_page = [link.id for link in context["object_list"]]
            voted = voted.filter(link_id__in=links_in_page)
            voted = voted.values_list('link_id', flat=True)
            context["voted"] = voted
        return context

class LinkUpdateView(UpdateView):
    model = Link
    form_class = LinkForm

class LinkDeleteView(DeleteView):
    model = Link
    success_url = reverse_lazy("home")

class UserProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = "username"
    template_name = "user_detail.html"

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user

class UserProfileEditView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "edit_profile.html"

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        return reverse("profile", kwargs={'slug': self.request.user})

class LinkCreateView(CreateView):
    model = Link
    form_class = LinkForm

    def form_valid(self, form): #this processes the form before it gets saved to the database
        f = form.save(commit=False)
        f.rank_score = 0.0
        f.submitter = self.request.user
        f.with_votes = 0
        f.category = '1'
        f.save()
        return super(CreateView, self).form_valid(form)

class VoteFormView(FormView): #corresponding view for the form for Vote we created in forms.py
    form_class = VoteForm

    def form_valid(self, form): #this function is always to be defined in views created for forms
        link = get_object_or_404(Link, pk=form.data["link"]) #this gets the primary key from the form the user submitted
        user = self.request.user
        if self.request.method == 'POST':
            btn = self.request.POST.get("val")
        if btn == u"\u2191":
            val = 1
        elif btn == u"\u2193":
            val = -1
        else:
            val = 0
        prev_votes = Vote.objects.filter(voter=user, link=link) #has the user already voted? If so, we'll find out via this
        has_voted = (prev_votes.count() > 0)
        if not has_voted: #this only works if the user has NOT voted before
            # add vote
            Vote.objects.create(voter=user, link=link, value=val) #if user hasn't voted, add the up or down vote in the DB.
        else:
            # delete vote
            prev_votes[0].delete() #if user has previously voted, simply delete previous vote
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form): #this function is also always to be defined for views created for forms
        return redirect("home")
	
def LinkAutoCreate(user, content):   
    link = Link()
    content = content.replace('#',' ') 
    link.description = content
    #urls = re.findall(r'(https?://\S+)', content)
     #r = re.compile(r'(https?://[^ ]+)')
    #r = re.findall("#(\w+)",content)
    #if urls:
    #    link.url = urls[0] 
     #link.description = r.sub(r'<a href="\1">\1</a>', content)
    #link.description = content
    #for link in urls:
    #    link.sub()
    link.submitter = user
    link.rank_score = 0.0
    link.with_votes = 0
    link.category = '1'
    link.save()
    user.userprofile.previous_retort = content
    user.userprofile.save()
