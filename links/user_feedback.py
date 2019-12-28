import time
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from website_feedback_form import WebsiteDescriptiveFeedbackForm, WebsiteFeedbackUserDetailsForm, WebsiteChoicesFeedbackForm
from utilities import convert_to_epoch
from models import HellBanList

############################################## Nicknames extractor ################################################


def retrieve_hell_banned_nicknames():
	"""
	Populates hell_banned nicknames in a sorted set (sorted by joining time)
	"""
	hell_banned_user_and_times = HellBanList.objects.all().values('condemned_id','when')
	hell_banned_user_ids = []
	nicks_and_ban_times = {}
	for dictionary in hell_banned_user_and_times:
		banned_id, ban_time = dictionary['condemned_id'], dictionary['when']
		hell_banned_user_ids.append(dictionary['condemned_id'])
		nicks_and_ban_times[banned_id] = convert_to_epoch(ban_time)
	hell_banned_users = User.objects.filter(id__in=hell_banned_user_ids).values('id','username','date_joined')
	banned_usernames_and_ban_times = []
	for user in hell_banned_users:
		user_id = user['id']
		username = user['username']
		date_joined = user['date_joined']
		banned_usernames_and_ban_times.append({'username':username,'user_id':user_id,'date_joined':date_joined})
	return banned_usernames_and_ban_times


def retrieve_regular_nicknames(how_many='all'):
	"""
	Populates hell_banned nicknames in a sorted set (sorted by joining time)
	"""
	hell_banned_user_ids = HellBanList.objects.all().values_list('condemned_id',flat=True)
	if how_many == 'all':
		# get all nicknames
		regular_users = User.objects.order_by('-id').values_list('id','username','date_joined')
	else:
		regular_users = User.objects.order_by('-id').values_list('id','username','date_joined')[:how_many]
	usernames_and_joining_time = []
	for user_id, username, date_joined in regular_users:
		if user_id not in hell_banned_user_ids:
			usernames_and_joining_time.append({'username':username,'user_id':user_id,'date_joined':date_joined})
	return usernames_and_joining_time


def export_nicknames_csv(request):
	"""
	Retrieve all hell-banned usernames for parsing into "good" and "bad"
	"""
	# hell_banned_users = retrieve_hell_banned_nicknames()
	regular_users = retrieve_regular_nicknames()#43000)
	
	# if hell_banned_users:
	# 	import csv
	# 	filename = 'hell_banned_nicks_'+str(int(time.time()))+'.csv'
	# 	with open(filename,'wb') as f:
	# 		wtr = csv.writer(f)
	# 		columns = "user_id date_joined username".split()
	# 		wtr.writerow(columns)
	# 		for user in hell_banned_users:
	# 			user_id = user['user_id']
	# 			username = user['username'].encode('utf-8')
	# 			date_joined = user['date_joined']
	# 			to_write = [user_id,date_joined,username]
	# 			wtr.writerows([to_write])
	if regular_users:
		import csv
		filename = 'regular_nicks_'+str(int(time.time()))+'.csv'
		with open(filename,'wb') as f:
			wtr = csv.writer(f)
			columns = "user_id date_joined username".split()
			wtr.writerow(columns)
			for user in regular_users:
				user_id = user['user_id']
				username = user['username'].encode('utf-8')
				date_joined = user['date_joined']
				to_write = [user_id,date_joined,username]
				wtr.writerows([to_write])
	return render(request,"404.html",{})

###################################################################################################################

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
					data = {}
					data["question1"] = request.POST.get("question1",None)
					data["feedback1"] = form.cleaned_data.get("feedback1",None)
					data["question2"] = request.POST.get("question2",None)
					data["feedback2"] = form.cleaned_data.get("feedback2",None)
					data["question3"] = request.POST.get("question3",None)
					data["feedback3"] = form.cleaned_data.get("feedback3",None)
					data["question4"] = request.POST.get("question4",None)
					data["feedback4"] = form.cleaned_data.get("feedback4",None)
					data["question5"] = request.POST.get("question5",None)
					data["feedback5"] = form.cleaned_data.get("feedback5",None)
					data["question6"] = request.POST.get("question6",None)
					data["feedback6"] = form.cleaned_data.get("feedback6",None)
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
					context = {'form':form}
					context["question1"] = request.POST.get("question1",None)
					context["question2"] = request.POST.get("question2",None)
					context["question3"] = request.POST.get("question3",None)
					context["question4"] = request.POST.get("question4",None)
					context["question5"] = request.POST.get("question5",None)
					context["question6"] = request.POST.get("question6",None)
					return render(request,"website_choices_feedback.html",context)
			elif answered == '2':
				form = WebsiteFeedbackUserDetailsForm(request.POST)
				if form.is_valid():
					pass
				else:
					pass
			else:
				context = {}
				context["form"] = WebsiteChoicesFeedbackForm()
				context["question1"] = "1) Aap ko Damadam mein ziada kia pasand hai?"
				context["question2"] = "2) Aap ko Home pe ziada kia pasand hai?"
				context["question3"] = "3) Damadam ke buray users logon ko kahan tang kartay hain?"
				context["question4"] = "4) Agar ap Damadam main kuch neya dalo to wo kia ho?"
				context["question5"] = "5) Home ki sab se boring baat kia hia?"
				context["question6"] = "6) Damadam pe sab se asani se dost kahan bante hain?"
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