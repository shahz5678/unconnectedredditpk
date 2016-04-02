# -*- coding: utf-8 -*-
from django import template
from django.db import models
from django.contrib.auth.models import User

register = template.Library()

FEMALES = [u'Š0nîКa_Pārììï', 'Ayesha_Rani', 'Faiza_bb', 'Sweetyprincess', 'khush', 'ezaal', 'mishii', 'Pragya', 'masuma', 'Hania_batooll', 'Mareena_Baloch', 'Sunaina-Choudry', 'AS-g', 'Manoo_billi', 'Maahi', 'zarakhan', 'dua-fatima', 'tania.pari', 'Appa', 'fasi', 'Danger_Kuri', 'SMIR', 'Mobina', 'natasha', 'sky', 'hoorain', 'Pakiza', 'flaqnaaz', 'Mahikayani_12', 'Atia-', 'aashi', 'tamanna-@101', 'Sirf', 'dharkan', 'taabi', 'Ramish.shahbaz', 'as', 'Laiba-paari', 'Palkzahra', 'rohi', 'Kandeel', 'maham_rani', 'Nabiha.Ch', 'Rafiaa7', 'Anuu', 'shono', 'fatima_CH', 'sundarsundas', 'L..s', 'Naema', 'Arooj_Fatima', 'Harleen', 'poja', 'FaRyAaL_GoHaR', 'sangat', 'Arooj', 'Sana_Warriach', 'gull33', 'Maham-@', 'Fiza_Qureshi', 'jiu', 'Bebbo', 'Babydoll...', 'Aashii', 'sumaira.khan', 'Princess_asi', 'Aysha.khan', 'Seep', 'khazaen', 'noshihaider', 'Phool', 'Jannat_ch', 'Paari', 'Annu', 't', 'Alveena_rani476', 'AnfaaL', 'Bisma.Azam', 'zahra', 'Anjilina', 'Aamina','Manhi','rabiaali', 'Aishmato', 'Shonni', 'Jaana', 'ayla', 'Maleenjaslee', 'Hoor', 'Tani_789', 'Sanam_khan', 'Esha-ali-subhani', 'dipika', 'Pomi', 'July', 'Juhikhan', 'gori', 'samreen', 'AlinaNoor_786', 'mehro', 'Sheeery', 'Maleenjalee','RimiShah','Remsha','sherikhokhar5','Roshni_malik_53','Rahat.com',]

@register.assignment_tag(takes_context=True)
def check_user_is_verified(context):
	user = context['request'].user
	#print "user is %s" % user
	#print "user in females is %s" % (user.username in VIP)
	return user and user.username in FEMALES