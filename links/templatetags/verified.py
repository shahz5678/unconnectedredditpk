# -*- coding: utf-8 -*-
from django import template
from django.db import models
from django.contrib.auth.models import User

register = template.Library()

FEMALES = [u'Š0nîКa_Pārììï', 'Hania-Batool', 'AS-g', 'Manoo_billi', 'Maahi', 'zarakhan', 'dua-fatima', 'tania.pari', 'Appa', 'fasi', 'Danger_Kuri', 'SMIR','Rose_rajpoot', 'Mobina', 'natasha', 'sky', 'hoorain', 'Pakiza', 'flaqnaaz', 'Mahikayani_12', 'Atia-', 'aashi', 'tamanna-@101', 'Sirf', 'Sanam_ali', 'dharkan', 'taabi', 'Ramish.shahbaz', 'as', 'Laiba-paari', 'Palkzahra', 'rohi', 'Kandeel', 'maham_rani', 'Nabiha.Ch', 'Rafiaa7', 'Anuu', 'shono', 'fatima_CH', 'L..s', 'Faiza', 'Naema', 'Arooj_Fatima', 'Harleen', 'poja', 'FaRyAaL_GoHaR', 'sangat', 'sumaira.khan', 'Princess_asi', 'Aysha.khan', 'Seep', 'khazaen', 'noshihaider', 'Phool', 'Jannat_ch', 'hayakhan' , 'Paari', 'Annu', 't', 'Alveena_rani476', 'AnfaaL', 'Bisma.Azam', 'zahra', 'Anjilina', 'Aamina','Manhi','rabiaali', 'Sana', 'Aishmato', 'Shonni', 'Jaana', 'ayla', 'Maleenjaslee', 'Hoor', 'Tani_789', 'Sanam_khan', 'Esha-ali-subhani', 'dipika', 'Pomi', 'Hina', 'July', 'Juhikhan', 'gori', 'samreen', 'Farheen', 'pholi', 'AlinaNoor_786', 'rabika', 'mehro', 'Sheeery', 'Maleenjalee','RimiShah','Remsha','sherikhokhar5','Roshni_malik_53','Rahat',]

@register.assignment_tag(takes_context=True)
def check_user_is_verified(context):
	user = context['request'].user
	#print "user is %s" % user
	#print "user in females is %s" % (user.username in VIP)
	return user and user.username in FEMALES