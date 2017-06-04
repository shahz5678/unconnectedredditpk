from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from .redis1 import clean_up_feedback, get_website_feedback, save_website_feedback_user_details, save_website_feedback, first_time_feedbacker, \
add_website_feedbacker
from .website_feedback_form import WebsiteDescriptiveFeedbackForm, WebsiteFeedbackUserDetailsForm, WebsiteChoicesFeedbackForm

@csrf_protect
def see_website_feedback(request,*args,**kwargs):
	if request.method == 'POST':
		delete = request.POST.get('delete',None)
		if delete == 'Delete All':
			clean_up_feedback()
		return redirect("see_website_feedback")
	else:
		total_feedback = get_website_feedback()
		total_feedback.sort(key=lambda k : k['time_of_feedback'])
		count = len(total_feedback)
		return render(request,"see_website_feedback.html",{'total_feedback':total_feedback,'count':count})

###################################################################################################################

@csrf_protect
def website_choices_feedback(request,*args,**kwargs):
	if request.method == 'POST':
		if first_time_feedbacker(request.user.id):
			add_website_feedbacker(request.user.id)
			return render(request,"website_feedback_tutorial.html",{})
		else:
			answered = request.POST.get('answered',None)
			if answered == '1':
				form = WebsiteChoicesFeedbackForm(request.POST)
				if form.is_valid():
					pass
				else:
					pass
			elif answered == '2':
				form = WebsiteFeedbackUserDetailsForm(request.POST)
				if form.is_valid():
					pass
				else:
					pass
			else:
				context = {}
				context["form"] = WebsiteChoicesFeedbackForm()
				context["question1"] = "1) Aap ko Home pe ziyada acha kia lagta hai?"
				context["question2"] = "2) Aap ko ziada kia pasand hai?"
				context["question3"] = "3) Damadam ke buray users tang kahan kartay hain?"
				context["question4"] = "4) Agar ap Damadam main kuch niya dalo to wo kia ho?"
				context["question5"] = "5) Home ki sab se boring baat kia hia?"
				context["question6"] = "6) Damadam pe sab se asani se dost kaisey bante hain?"
				return render(request,"website_choices_feedback.html",context)
	else:
		return render(request,"404.html",{})

###################################################################################################################

@csrf_protect
def website_feedback(request,*args,**kwargs):
	if request.method == 'POST':
		if first_time_feedbacker(request.user.id):
			add_website_feedbacker(request.user.id)
			return render(request,"website_feedback_tutorial.html",{})
		else:
			answered = request.POST.get('answered',None)
			if answered == '1':
				form = WebsiteDescriptiveFeedbackForm(request.POST)
				question1 = request.POST.get("question1")
				question2 = request.POST.get("question2")
				question3 = request.POST.get("question3")
				question4 = request.POST.get("question4")
				question5 = request.POST.get("question5")
				if form.is_valid():
					data = {} 
					data["question1"] = question1
					data["question2"] = question2
					data["question3"] = question3
					data["question4"] = question4
					data["question5"] = question5
					data["feedback1"] = form.cleaned_data.get("feedback1")
					data["feedback2"] = form.cleaned_data.get("feedback2")
					data["feedback3"] = form.cleaned_data.get("feedback3")
					data["feedback4"] = form.cleaned_data.get("feedback4")
					data["feedback5"] = form.cleaned_data.get("feedback5")
					data["username"] = request.user.username
					data["user_id"] = request.user.id
					data["score"] = request.user.userprofile.score
					data["date_joined"] = request.user.date_joined
					data["time_of_feedback"] = time.time()
					if request.is_feature_phone:
						data["device"] = '1'
					elif request.is_phone:
						data["device"] = '2'
					elif request.is_tablet:
						data["device"] = '4'
					elif request.is_mobile:
						data["device"] = '5'
					else:
						data["device"] = '3'
					data_saved = save_website_feedback(data)
					if data_saved:
						form = WebsiteFeedbackUserDetailsForm()
						return render(request,"website_feedback_thanks.html",{'form':form})
					else:
						return redirect("home")
				else:
					context = {}
					context["form"] = form
					context["question1"] = question1
					context["question2"] = question2
					context["question3"] = question3
					context["question4"] = question4
					context["question5"] = question5
					return render(request,"website_descriptive_feedback.html",context)
			elif answered == '2':
				form = WebsiteFeedbackUserDetailsForm(request.POST)
				if form.is_valid():
					data = {}
					data["user_id"] = request.user.id
					data["mobile"] = form.cleaned_data.get("mobile")
					data["gender"] = form.cleaned_data.get("gender")
					data["city"] = form.cleaned_data.get("loc")
					data["age"] = form.cleaned_data.get("age")
					save_website_feedback_user_details(data)
					return redirect("home")
				else:
					return render(request,"website_feedback_thanks.html",{'form':form})
			else:
				context = {}
				context["form"] = WebsiteDescriptiveFeedbackForm()
				context["question1"] = "Aap ko Home pe sab se acha kia lagta hai?"
				context["question2"] = "Aap ko ziada kia pasand hai?"
				context["question3"] = "Damadam ke buray users tang kaisay kartay hain?"
				context["question4"] = "Agar ap Damadam main kuch niya dalo to wo kia ho?"
				context["question5"] = "Home ki sab se boring baat kia hia?"
				context["question6"] = "Damadam pe sab se asani se dost kaisey bante hain?"
				return render(request,"website_descriptive_feedback.html",context)
	else:
		return render(request,"404.html",{})

# Survey 2:

# "1) Agr ap ke koi dost Damadam chur ke gaye hain tu us ki kiya waja thi?"
# "2) Damadam mein kon si aisee cheez badli hai jo ap ko buri lagi ho?"
# "3) Ap Damadam mein kiya shamil kerna chaho ge?"
# "4) Damadam mein ap ko kis cheez ka sub se zada faida hota hai?"
# "5) Damadam ki sub se boring cheez kiya lagti hai, aur kiun?"

# Survey 1:

# "1) Agr ap Damadam choro, tou kis wajah se choro ge?"
# "2) Ap Damadam mein sab se ziyada kiya istimal kartey ho?"
# "3) Damadam mein aisa kuch hai jo Facebook mein nahi?"
# "4) Damadam mein aisa kuch hai jo Whatsapp mein nahi?"
# "5) Damadam ki sab se ziyada mazedar baat kiya hai?"