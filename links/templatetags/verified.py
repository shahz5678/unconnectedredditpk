# -*- coding: utf-8 -*-
from django import template
from django.db import models
from django.contrib.auth.models import User

register = template.Library()

# my_server = redis.Redis(connection_pool=POOL)
FEMALES = [u'Š0nîКa_Pārììï','Angel12345', 'cute...Ainy', '-KomaL-', 'Urooj-s','Ayesha._Rani.','zily','Princess_vini','HOoren-54','Hinaprincess','Mahamnoor','..HOOR..','AymanG','cuteangel77','Sehar..','angelzoha','jiya143', 'Naila..','Farahangel','fatima0000','Sit', 'Princes-shmmii', 'CINDERELA', 'PrincesMahi', 'whafa','Faiza_bb', 'Sweetyprincess', 'khush', 'ezaal', 'mishii', 'Hania_batooll', 'Pragya', 'masuma', 'sundarsundas', 'Mareena_Baloch', 'Arooj', 'gull33', 'Sana_Warriach', 'jiu', 'Maham-@', 'Fiza_Qureshi', 'Sunaina-Choudry', 'AS-g', 'Manoo_billi', 'Maahi', 'zarakhan', 'tania.pari', 'fasi', 'Aashii', 'Babydoll...', 'Mobina', 'natasha', 'hoorain', 'Pakiza', 'flaqnaaz', 'Mahikayani_12', 'Atia-', 'aashi', 'tamanna-@101', 'Sirf', 'dharkan', 'taabi', 'as', 'Laiba-paari', 'Palkzahra', 'rohi', 'maham_rani', 'Nabiha.Ch', 'Anuu', 'shono', 'fatima_CH', 'Arooj_Fatima', 'Harleen', 'poja', 'FaRyAaL_GoHaR', 'sangat', 'sumaira.khan','Seep', 'khazaen', 'Phool', 'Jannat_ch', 'Paari', 'Annu', 'Alveena_rani476', 'AnfaaL', 'Bisma.Azam', 'zahra', 'Anjilina', 'Aamina','Manhi', 'Aishmato', 'Shonni', 'Jaana', 'ayla', 'Maleenjaslee', 'Hoor', 'Tani_789', 'Sanam_khan', 'dipika', 'Pomi', 'July', 'Juhikhan', 'gori', 'samreen', 'AlinaNoor_786', 'SMIR', 'mehro', 'Sheeery', 'Maleenjalee','RimiShah','Remsha','sherikhokhar5','Roshni_malik_53','Rahat.com',]

@register.assignment_tag(takes_context=True)
def check_user_is_verified(context):
	user = context['request'].user
	return user and user.username in FEMALES