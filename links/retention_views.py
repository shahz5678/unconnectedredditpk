import csv
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.models import User
from redis8 import report_section_wise_retention, retrieve_all_logged_actions, retention_clean_up, retrieve_retention_activity_raw_records,\
compile_activity_occurence_rows, compile_activity_frequency_rows
from redis4 import retrieve_retention_ids, retrieve_retention_data
from retention_experiments import EXPERIMENTS_CURRENTLY_BEING_RUN
from redis7 import in_defenders
from redis3 import exact_date
from actions import actions


def display_retention(request,variation):
	"""
	Displays retention of any ongoing experiment
	"""
	# raise Http404("This doesn't exist")
	is_defender, is_super_defender = in_defenders(request.user.id, return_super_status=True)
	if is_super_defender and variation in EXPERIMENTS_CURRENTLY_BEING_RUN:
		return render(request,"retention/section_retention.html",{'variation':variation,'retention_data':report_section_wise_retention(variation)})
	else:
		# such a variation does not exist
		raise Http404("This doesn't exist")


def export_retention_activity_raw_log(request):
	"""
	Exports retention activity log for analysis
	"""
	defender_id = request.user.id
	is_defender, is_super_defender = in_defenders(defender_id, return_super_status=True)
	if is_super_defender:
		data_to_write_to_csv = retrieve_retention_activity_raw_records()
		if data_to_write_to_csv:
			filename = 'retention_activity.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				columns = ['User ID','Which Cohort','Activity Time','Which Day','Activity Time (Human)','HTTP Method','Activity Type','Page #',\
				'Input Text','Img URL','Caption','Target User ID','Which Topic','Object Type','Num 1on1s']
				wtr.writerow(columns)
				# WATCH OUT: M5.e or S5.e are errors which, if encoutered in "Activity Type", could be the main culprit for var2's demise. This error was observed between 'mhb11' and 'lonnie_smith' IDs
				for activity_dict, cohort_id, user_id, which_day, activity_time in data_to_write_to_csv:
					to_write = [user_id, cohort_id, int(activity_time), which_day, exact_date(activity_time), activity_dict['m'], \
					activity_dict['act'], activity_dict.get('pg',''), activity_dict.get('tx','').encode('utf-8'),activity_dict.get('pi',''),\
					activity_dict.get('pc','').encode('utf-8'),activity_dict.get('tuid',''),activity_dict.get('url','').encode('utf-8'),\
					activity_dict.get('ot',''),activity_dict.get('nf','')]
					wtr.writerows([to_write])
		##########################################################
	raise Http404("Completed ;)")


def export_retention_activity_occurrence_log(request):
	"""
	Exports retention activity occurrence logs, for analysis
	"""
	defender_id = request.user.id
	is_defender, is_super_defender = in_defenders(defender_id, return_super_status=True)
	if is_super_defender:
		data_header, data_details, variation_strings = compile_activity_occurence_rows()
		if data_header and data_details:
			filename = 'occurrence_data.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				actions.sort()
				columns = ['Cohort Number','Which Day', 'User ID', 'User Variations']+actions+['Total Actions']
				wtr.writerow(columns)
				for header in data_header:
					user_id = header[2]
					header_key = str(header[0])+":"+'d'+str(header[1])+":"+str(user_id)
					set_of_user_actions = data_details[header_key]
					which_day = 'd'+str(header[1])
					credentials = [header[0],which_day,user_id,variation_strings.get(user_id,'')]
					acts = [1 if actions[0] in set_of_user_actions else 0,\
					1 if actions[1] in set_of_user_actions else 0,1 if actions[2] in set_of_user_actions else 0,\
					1 if actions[3] in set_of_user_actions else 0,1 if actions[4] in set_of_user_actions else 0,\
					1 if actions[5] in set_of_user_actions else 0,1 if actions[6] in set_of_user_actions else 0,\
					1 if actions[7] in set_of_user_actions else 0,1 if actions[8] in set_of_user_actions else 0,\
					1 if actions[9] in set_of_user_actions else 0,1 if actions[10] in set_of_user_actions else 0,\
					1 if actions[11] in set_of_user_actions else 0,1 if actions[12] in set_of_user_actions else 0,\
					1 if actions[13] in set_of_user_actions else 0,1 if actions[14] in set_of_user_actions else 0,\
					1 if actions[15] in set_of_user_actions else 0,1 if actions[16] in set_of_user_actions else 0,\
					1 if actions[17] in set_of_user_actions else 0,1 if actions[18] in set_of_user_actions else 0,\
					1 if actions[19] in set_of_user_actions else 0,1 if actions[20] in set_of_user_actions else 0,\
					1 if actions[21] in set_of_user_actions else 0,1 if actions[22] in set_of_user_actions else 0,\
					1 if actions[23] in set_of_user_actions else 0,1 if actions[24] in set_of_user_actions else 0,\
					1 if actions[25] in set_of_user_actions else 0,1 if actions[26] in set_of_user_actions else 0,\
					1 if actions[27] in set_of_user_actions else 0,1 if actions[28] in set_of_user_actions else 0,\
					1 if actions[29] in set_of_user_actions else 0,1 if actions[30] in set_of_user_actions else 0,\
					1 if actions[31] in set_of_user_actions else 0,1 if actions[32] in set_of_user_actions else 0,\
					1 if actions[33] in set_of_user_actions else 0,1 if actions[34] in set_of_user_actions else 0,\
					1 if actions[35] in set_of_user_actions else 0,1 if actions[36] in set_of_user_actions else 0,\
					1 if actions[37] in set_of_user_actions else 0,1 if actions[38] in set_of_user_actions else 0,\
					1 if actions[39] in set_of_user_actions else 0,1 if actions[40] in set_of_user_actions else 0,\
					1 if actions[41] in set_of_user_actions else 0,1 if actions[42] in set_of_user_actions else 0,\
					1 if actions[43] in set_of_user_actions else 0,1 if actions[44] in set_of_user_actions else 0,\
					1 if actions[45] in set_of_user_actions else 0,1 if actions[46] in set_of_user_actions else 0,\
					1 if actions[47] in set_of_user_actions else 0,1 if actions[48] in set_of_user_actions else 0,\
					1 if actions[49] in set_of_user_actions else 0,1 if actions[50] in set_of_user_actions else 0,\
					1 if actions[51] in set_of_user_actions else 0,1 if actions[52] in set_of_user_actions else 0,\
					1 if actions[53] in set_of_user_actions else 0,1 if actions[54] in set_of_user_actions else 0,\
					1 if actions[55] in set_of_user_actions else 0,1 if actions[56] in set_of_user_actions else 0,\
					1 if actions[57] in set_of_user_actions else 0,1 if actions[58] in set_of_user_actions else 0,\
					1 if actions[59] in set_of_user_actions else 0,1 if actions[60] in set_of_user_actions else 0,\
					1 if actions[61] in set_of_user_actions else 0,1 if actions[62] in set_of_user_actions else 0,\
					1 if actions[63] in set_of_user_actions else 0,1 if actions[64] in set_of_user_actions else 0,\
					1 if actions[65] in set_of_user_actions else 0,1 if actions[66] in set_of_user_actions else 0,\
					1 if actions[67] in set_of_user_actions else 0,1 if actions[68] in set_of_user_actions else 0,\
					1 if actions[69] in set_of_user_actions else 0,1 if actions[70] in set_of_user_actions else 0,\
					1 if actions[71] in set_of_user_actions else 0,1 if actions[72] in set_of_user_actions else 0,\
					1 if actions[73] in set_of_user_actions else 0,1 if actions[74] in set_of_user_actions else 0,\
					1 if actions[75] in set_of_user_actions else 0,1 if actions[76] in set_of_user_actions else 0,\
					1 if actions[77] in set_of_user_actions else 0,1 if actions[78] in set_of_user_actions else 0,\
					1 if actions[79] in set_of_user_actions else 0,1 if actions[80] in set_of_user_actions else 0,\
					1 if actions[81] in set_of_user_actions else 0,1 if actions[82] in set_of_user_actions else 0,\
					1 if actions[83] in set_of_user_actions else 0,1 if actions[84] in set_of_user_actions else 0,\
					1 if actions[85] in set_of_user_actions else 0,1 if actions[86] in set_of_user_actions else 0,\
					1 if actions[87] in set_of_user_actions else 0,1 if actions[88] in set_of_user_actions else 0,\
					1 if actions[89] in set_of_user_actions else 0,1 if actions[90] in set_of_user_actions else 0,\
					1 if actions[91] in set_of_user_actions else 0,1 if actions[92] in set_of_user_actions else 0,\
					1 if actions[93] in set_of_user_actions else 0,1 if actions[94] in set_of_user_actions else 0,\
					1 if actions[95] in set_of_user_actions else 0,1 if actions[96] in set_of_user_actions else 0,\
					1 if actions[97] in set_of_user_actions else 0,1 if actions[98] in set_of_user_actions else 0,\
					1 if actions[99] in set_of_user_actions else 0,1 if actions[100] in set_of_user_actions else 0,\
					1 if actions[101] in set_of_user_actions else 0,1 if actions[102] in set_of_user_actions else 0,\
					1 if actions[103] in set_of_user_actions else 0,1 if actions[104] in set_of_user_actions else 0,\
					1 if actions[105] in set_of_user_actions else 0,1 if actions[106] in set_of_user_actions else 0,\
					1 if actions[107] in set_of_user_actions else 0,1 if actions[108] in set_of_user_actions else 0,\
					1 if actions[109] in set_of_user_actions else 0,1 if actions[110] in set_of_user_actions else 0,\
					1 if actions[111] in set_of_user_actions else 0,1 if actions[112] in set_of_user_actions else 0,\
					1 if actions[113] in set_of_user_actions else 0,1 if actions[114] in set_of_user_actions else 0,\
					1 if actions[115] in set_of_user_actions else 0,1 if actions[116] in set_of_user_actions else 0,\
					1 if actions[117] in set_of_user_actions else 0,1 if actions[118] in set_of_user_actions else 0,\
					1 if actions[119] in set_of_user_actions else 0,1 if actions[120] in set_of_user_actions else 0,\
					1 if actions[121] in set_of_user_actions else 0,1 if actions[122] in set_of_user_actions else 0,\
					1 if actions[123] in set_of_user_actions else 0,1 if actions[124] in set_of_user_actions else 0,\
					1 if actions[125] in set_of_user_actions else 0,1 if actions[126] in set_of_user_actions else 0,\
					1 if actions[127] in set_of_user_actions else 0,1 if actions[128] in set_of_user_actions else 0,\
					1 if actions[129] in set_of_user_actions else 0,1 if actions[130] in set_of_user_actions else 0,\
					1 if actions[131] in set_of_user_actions else 0,1 if actions[132] in set_of_user_actions else 0,\
					1 if actions[133] in set_of_user_actions else 0,1 if actions[134] in set_of_user_actions else 0,\
					1 if actions[135] in set_of_user_actions else 0,1 if actions[136] in set_of_user_actions else 0,\
					1 if actions[137] in set_of_user_actions else 0,1 if actions[138] in set_of_user_actions else 0,\
					1 if actions[139] in set_of_user_actions else 0,1 if actions[140] in set_of_user_actions else 0,\
					1 if actions[141] in set_of_user_actions else 0,1 if actions[142] in set_of_user_actions else 0,\
					1 if actions[143] in set_of_user_actions else 0,1 if actions[144] in set_of_user_actions else 0,\
					1 if actions[145] in set_of_user_actions else 0,1 if actions[146] in set_of_user_actions else 0,\
					1 if actions[147] in set_of_user_actions else 0,1 if actions[148] in set_of_user_actions else 0,\
					1 if actions[149] in set_of_user_actions else 0,1 if actions[150] in set_of_user_actions else 0,\
					1 if actions[151] in set_of_user_actions else 0,1 if actions[152] in set_of_user_actions else 0,\
					1 if actions[153] in set_of_user_actions else 0,1 if actions[154] in set_of_user_actions else 0,\
					1 if actions[155] in set_of_user_actions else 0,1 if actions[156] in set_of_user_actions else 0,\
					1 if actions[157] in set_of_user_actions else 0,1 if actions[158] in set_of_user_actions else 0,\
					1 if actions[159] in set_of_user_actions else 0,1 if actions[160] in set_of_user_actions else 0,\
					1 if actions[161] in set_of_user_actions else 0,1 if actions[162] in set_of_user_actions else 0,\
					1 if actions[163] in set_of_user_actions else 0,1 if actions[164] in set_of_user_actions else 0,\
					1 if actions[165] in set_of_user_actions else 0,1 if actions[166] in set_of_user_actions else 0,\
					1 if actions[167] in set_of_user_actions else 0,1 if actions[168] in set_of_user_actions else 0,\
					1 if actions[169] in set_of_user_actions else 0,1 if actions[170] in set_of_user_actions else 0,\
					1 if actions[171] in set_of_user_actions else 0,1 if actions[172] in set_of_user_actions else 0,\
					1 if actions[173] in set_of_user_actions else 0,1 if actions[174] in set_of_user_actions else 0,\
					1 if actions[175] in set_of_user_actions else 0,1 if actions[176] in set_of_user_actions else 0,\
					1 if actions[177] in set_of_user_actions else 0,1 if actions[178] in set_of_user_actions else 0,\
					1 if actions[179] in set_of_user_actions else 0,1 if actions[180] in set_of_user_actions else 0,\
					1 if actions[181] in set_of_user_actions else 0,1 if actions[182] in set_of_user_actions else 0,\
					1 if actions[183] in set_of_user_actions else 0,1 if actions[184] in set_of_user_actions else 0,\
					1 if actions[185] in set_of_user_actions else 0,1 if actions[186] in set_of_user_actions else 0,\
					1 if actions[187] in set_of_user_actions else 0,1 if actions[188] in set_of_user_actions else 0,\
					1 if actions[189] in set_of_user_actions else 0,1 if actions[190] in set_of_user_actions else 0,\
					1 if actions[191] in set_of_user_actions else 0,1 if actions[192] in set_of_user_actions else 0,\
					1 if actions[193] in set_of_user_actions else 0,1 if actions[194] in set_of_user_actions else 0,\
					1 if actions[195] in set_of_user_actions else 0,1 if actions[196] in set_of_user_actions else 0,\
					1 if actions[197] in set_of_user_actions else 0,1 if actions[198] in set_of_user_actions else 0,\
					1 if actions[199] in set_of_user_actions else 0,1 if actions[200] in set_of_user_actions else 0,\
					1 if actions[201] in set_of_user_actions else 0,1 if actions[202] in set_of_user_actions else 0,\
					1 if actions[203] in set_of_user_actions else 0,1 if actions[204] in set_of_user_actions else 0,\
					1 if actions[205] in set_of_user_actions else 0,1 if actions[206] in set_of_user_actions else 0,\
					1 if actions[207] in set_of_user_actions else 0,1 if actions[208] in set_of_user_actions else 0,\
					1 if actions[209] in set_of_user_actions else 0,1 if actions[210] in set_of_user_actions else 0,\
					1 if actions[211] in set_of_user_actions else 0,1 if actions[212] in set_of_user_actions else 0,\
					1 if actions[213] in set_of_user_actions else 0,1 if actions[214] in set_of_user_actions else 0,\
					1 if actions[215] in set_of_user_actions else 0,1 if actions[216] in set_of_user_actions else 0,\
					1 if actions[217] in set_of_user_actions else 0,1 if actions[218] in set_of_user_actions else 0,\
					1 if actions[219] in set_of_user_actions else 0,1 if actions[220] in set_of_user_actions else 0,\
					1 if actions[221] in set_of_user_actions else 0,1 if actions[222] in set_of_user_actions else 0,\
					1 if actions[223] in set_of_user_actions else 0,1 if actions[224] in set_of_user_actions else 0,\
					1 if actions[225] in set_of_user_actions else 0,1 if actions[226] in set_of_user_actions else 0,\
					1 if actions[227] in set_of_user_actions else 0,1 if actions[228] in set_of_user_actions else 0,\
					1 if actions[229] in set_of_user_actions else 0,1 if actions[230] in set_of_user_actions else 0,\
					1 if actions[231] in set_of_user_actions else 0,1 if actions[232] in set_of_user_actions else 0,\
					1 if actions[233] in set_of_user_actions else 0]
					total = [sum(acts)]
					to_write = credentials+acts+total
					wtr.writerows([to_write])
		##########################################################
	raise Http404("Completed ;)")


def export_retention_activity_frequency_log(request):
	"""
	Exports retention activity occurrence logs, for analysis
	"""
	defender_id = request.user.id
	is_defender, is_super_defender = in_defenders(defender_id, return_super_status=True)
	if is_super_defender:
		data_header, data_details, variation_strings = compile_activity_frequency_rows()
		if data_header and data_details:
			filename = 'frequency_data.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				actions.sort()
				columns = ['Cohort Number','Which Day', 'User ID', 'User Variations']+actions+['Total Actions']
				wtr.writerow(columns)
				for header in data_header:
					user_id = header[2]
					header_key = str(header[0])+":"+'d'+str(header[1])+":"+str(user_id)
					dict_of_user_actions = data_details[header_key]
					which_day = 'd'+str(header[1])
					credentials = [header[0],which_day,user_id,variation_strings.get(user_id,'')]
					acts = [dict_of_user_actions.get(actions[0],0),dict_of_user_actions.get(actions[1],0),\
					dict_of_user_actions.get(actions[2],0),dict_of_user_actions.get(actions[3],0),\
					dict_of_user_actions.get(actions[4],0),dict_of_user_actions.get(actions[5],0),\
					dict_of_user_actions.get(actions[6],0),dict_of_user_actions.get(actions[7],0),\
					dict_of_user_actions.get(actions[8],0),dict_of_user_actions.get(actions[9],0),\
					dict_of_user_actions.get(actions[10],0),dict_of_user_actions.get(actions[11],0),\
					dict_of_user_actions.get(actions[12],0),dict_of_user_actions.get(actions[13],0),\
					dict_of_user_actions.get(actions[14],0),dict_of_user_actions.get(actions[15],0),\
					dict_of_user_actions.get(actions[16],0),dict_of_user_actions.get(actions[17],0),\
					dict_of_user_actions.get(actions[18],0),dict_of_user_actions.get(actions[19],0),\
					dict_of_user_actions.get(actions[20],0),dict_of_user_actions.get(actions[21],0),\
					dict_of_user_actions.get(actions[22],0),dict_of_user_actions.get(actions[23],0),\
					dict_of_user_actions.get(actions[24],0),dict_of_user_actions.get(actions[25],0),\
					dict_of_user_actions.get(actions[26],0),dict_of_user_actions.get(actions[27],0),\
					dict_of_user_actions.get(actions[28],0),dict_of_user_actions.get(actions[29],0),\
					dict_of_user_actions.get(actions[30],0),dict_of_user_actions.get(actions[31],0),\
					dict_of_user_actions.get(actions[32],0),dict_of_user_actions.get(actions[33],0),\
					dict_of_user_actions.get(actions[34],0),dict_of_user_actions.get(actions[35],0),\
					dict_of_user_actions.get(actions[36],0),dict_of_user_actions.get(actions[37],0),\
					dict_of_user_actions.get(actions[38],0),dict_of_user_actions.get(actions[39],0),\
					dict_of_user_actions.get(actions[40],0),dict_of_user_actions.get(actions[41],0),\
					dict_of_user_actions.get(actions[42],0),dict_of_user_actions.get(actions[43],0),\
					dict_of_user_actions.get(actions[44],0),dict_of_user_actions.get(actions[45],0),\
					dict_of_user_actions.get(actions[46],0),dict_of_user_actions.get(actions[47],0),\
					dict_of_user_actions.get(actions[48],0),dict_of_user_actions.get(actions[49],0),\
					dict_of_user_actions.get(actions[50],0),dict_of_user_actions.get(actions[51],0),\
					dict_of_user_actions.get(actions[52],0),dict_of_user_actions.get(actions[53],0),\
					dict_of_user_actions.get(actions[54],0),dict_of_user_actions.get(actions[55],0),\
					dict_of_user_actions.get(actions[56],0),dict_of_user_actions.get(actions[57],0),\
					dict_of_user_actions.get(actions[58],0),dict_of_user_actions.get(actions[59],0),\
					dict_of_user_actions.get(actions[60],0),dict_of_user_actions.get(actions[61],0),\
					dict_of_user_actions.get(actions[62],0),dict_of_user_actions.get(actions[63],0),\
					dict_of_user_actions.get(actions[64],0),dict_of_user_actions.get(actions[65],0),\
					dict_of_user_actions.get(actions[66],0),dict_of_user_actions.get(actions[67],0),\
					dict_of_user_actions.get(actions[68],0),dict_of_user_actions.get(actions[69],0),\
					dict_of_user_actions.get(actions[70],0),dict_of_user_actions.get(actions[71],0),\
					dict_of_user_actions.get(actions[72],0),dict_of_user_actions.get(actions[73],0),\
					dict_of_user_actions.get(actions[74],0),dict_of_user_actions.get(actions[75],0),\
					dict_of_user_actions.get(actions[76],0),dict_of_user_actions.get(actions[77],0),\
					dict_of_user_actions.get(actions[78],0),dict_of_user_actions.get(actions[79],0),\
					dict_of_user_actions.get(actions[80],0),dict_of_user_actions.get(actions[81],0),\
					dict_of_user_actions.get(actions[82],0),dict_of_user_actions.get(actions[83],0),\
					dict_of_user_actions.get(actions[84],0),dict_of_user_actions.get(actions[85],0),\
					dict_of_user_actions.get(actions[86],0),dict_of_user_actions.get(actions[87],0),\
					dict_of_user_actions.get(actions[88],0),dict_of_user_actions.get(actions[89],0),\
					dict_of_user_actions.get(actions[90],0),dict_of_user_actions.get(actions[91],0),\
					dict_of_user_actions.get(actions[92],0),dict_of_user_actions.get(actions[93],0),\
					dict_of_user_actions.get(actions[94],0),dict_of_user_actions.get(actions[95],0),\
					dict_of_user_actions.get(actions[96],0),dict_of_user_actions.get(actions[97],0),\
					dict_of_user_actions.get(actions[98],0),dict_of_user_actions.get(actions[99],0),\
					dict_of_user_actions.get(actions[100],0),dict_of_user_actions.get(actions[101],0),\
					dict_of_user_actions.get(actions[102],0),dict_of_user_actions.get(actions[103],0),\
					dict_of_user_actions.get(actions[104],0),dict_of_user_actions.get(actions[105],0),\
					dict_of_user_actions.get(actions[106],0),dict_of_user_actions.get(actions[107],0),\
					dict_of_user_actions.get(actions[108],0),dict_of_user_actions.get(actions[109],0),\
					dict_of_user_actions.get(actions[110],0),dict_of_user_actions.get(actions[111],0),\
					dict_of_user_actions.get(actions[112],0),dict_of_user_actions.get(actions[113],0),\
					dict_of_user_actions.get(actions[114],0),dict_of_user_actions.get(actions[115],0),\
					dict_of_user_actions.get(actions[116],0),dict_of_user_actions.get(actions[117],0),\
					dict_of_user_actions.get(actions[118],0),dict_of_user_actions.get(actions[119],0),\
					dict_of_user_actions.get(actions[120],0),dict_of_user_actions.get(actions[121],0),\
					dict_of_user_actions.get(actions[122],0),dict_of_user_actions.get(actions[123],0),\
					dict_of_user_actions.get(actions[124],0),dict_of_user_actions.get(actions[125],0),\
					dict_of_user_actions.get(actions[126],0),dict_of_user_actions.get(actions[127],0),\
					dict_of_user_actions.get(actions[128],0),dict_of_user_actions.get(actions[129],0),\
					dict_of_user_actions.get(actions[130],0),dict_of_user_actions.get(actions[131],0),\
					dict_of_user_actions.get(actions[132],0),dict_of_user_actions.get(actions[133],0),\
					dict_of_user_actions.get(actions[134],0),dict_of_user_actions.get(actions[135],0),\
					dict_of_user_actions.get(actions[136],0),dict_of_user_actions.get(actions[137],0),\
					dict_of_user_actions.get(actions[138],0),dict_of_user_actions.get(actions[139],0),\
					dict_of_user_actions.get(actions[140],0),dict_of_user_actions.get(actions[141],0),\
					dict_of_user_actions.get(actions[142],0),dict_of_user_actions.get(actions[143],0),\
					dict_of_user_actions.get(actions[144],0),dict_of_user_actions.get(actions[145],0),\
					dict_of_user_actions.get(actions[146],0),dict_of_user_actions.get(actions[147],0),\
					dict_of_user_actions.get(actions[148],0),dict_of_user_actions.get(actions[149],0),\
					dict_of_user_actions.get(actions[150],0),dict_of_user_actions.get(actions[151],0),\
					dict_of_user_actions.get(actions[152],0),dict_of_user_actions.get(actions[153],0),\
					dict_of_user_actions.get(actions[154],0),dict_of_user_actions.get(actions[155],0),\
					dict_of_user_actions.get(actions[156],0),dict_of_user_actions.get(actions[157],0),\
					dict_of_user_actions.get(actions[158],0),dict_of_user_actions.get(actions[159],0),\
					dict_of_user_actions.get(actions[160],0),dict_of_user_actions.get(actions[161],0),\
					dict_of_user_actions.get(actions[162],0),dict_of_user_actions.get(actions[163],0),\
					dict_of_user_actions.get(actions[164],0),dict_of_user_actions.get(actions[165],0),\
					dict_of_user_actions.get(actions[166],0),dict_of_user_actions.get(actions[167],0),\
					dict_of_user_actions.get(actions[168],0),dict_of_user_actions.get(actions[169],0),\
					dict_of_user_actions.get(actions[170],0),dict_of_user_actions.get(actions[171],0),\
					dict_of_user_actions.get(actions[172],0),dict_of_user_actions.get(actions[173],0),\
					dict_of_user_actions.get(actions[174],0),dict_of_user_actions.get(actions[175],0),\
					dict_of_user_actions.get(actions[176],0),dict_of_user_actions.get(actions[177],0),\
					dict_of_user_actions.get(actions[178],0),dict_of_user_actions.get(actions[179],0),\
					dict_of_user_actions.get(actions[180],0),dict_of_user_actions.get(actions[181],0),\
					dict_of_user_actions.get(actions[182],0),dict_of_user_actions.get(actions[183],0),\
					dict_of_user_actions.get(actions[184],0),dict_of_user_actions.get(actions[185],0),\
					dict_of_user_actions.get(actions[186],0),dict_of_user_actions.get(actions[187],0),\
					dict_of_user_actions.get(actions[188],0),dict_of_user_actions.get(actions[189],0),\
					dict_of_user_actions.get(actions[190],0),dict_of_user_actions.get(actions[191],0),\
					dict_of_user_actions.get(actions[192],0),dict_of_user_actions.get(actions[193],0),\
					dict_of_user_actions.get(actions[194],0),dict_of_user_actions.get(actions[195],0),\
					dict_of_user_actions.get(actions[196],0),dict_of_user_actions.get(actions[197],0),\
					dict_of_user_actions.get(actions[198],0),dict_of_user_actions.get(actions[199],0),\
					dict_of_user_actions.get(actions[200],0),dict_of_user_actions.get(actions[201],0),\
					dict_of_user_actions.get(actions[202],0),dict_of_user_actions.get(actions[203],0),\
					dict_of_user_actions.get(actions[204],0),dict_of_user_actions.get(actions[205],0),\
					dict_of_user_actions.get(actions[206],0),dict_of_user_actions.get(actions[207],0),\
					dict_of_user_actions.get(actions[208],0),dict_of_user_actions.get(actions[209],0),\
					dict_of_user_actions.get(actions[210],0),dict_of_user_actions.get(actions[211],0),\
					dict_of_user_actions.get(actions[212],0),dict_of_user_actions.get(actions[213],0),\
					dict_of_user_actions.get(actions[214],0),dict_of_user_actions.get(actions[215],0),\
					dict_of_user_actions.get(actions[216],0),dict_of_user_actions.get(actions[217],0),\
					dict_of_user_actions.get(actions[218],0),dict_of_user_actions.get(actions[219],0),\
					dict_of_user_actions.get(actions[220],0),dict_of_user_actions.get(actions[221],0),\
					dict_of_user_actions.get(actions[222],0),dict_of_user_actions.get(actions[223],0),\
					dict_of_user_actions.get(actions[224],0),dict_of_user_actions.get(actions[225],0),\
					dict_of_user_actions.get(actions[226],0),dict_of_user_actions.get(actions[227],0),\
					dict_of_user_actions.get(actions[228],0),dict_of_user_actions.get(actions[229],0),\
					dict_of_user_actions.get(actions[230],0),dict_of_user_actions.get(actions[231],0),\
					dict_of_user_actions.get(actions[232],0),dict_of_user_actions.get(actions[233],0)]
					total = [sum(acts)]
					to_write = credentials+acts+total			
					wtr.writerows([to_write])
		##########################################################
	raise Http404("Completed ;)")


###############################################################################################################

def export_logged_actions(request):
	"""
	Exports all logged actions into a CSV file for analysis
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		data_to_write_to_csv = retrieve_all_logged_actions()# list of lists (where each list is a list of dictionaries)
		if data_to_write_to_csv:
			filename = 'action_data.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				#  payload = str(user_id)+":"+user_age+":"+action_categ+":"+action_sub_categ+":"+action_liq+":"+str(time_of_action)
				columns = ["User ID","hours since segment init","parent category","sub category","action liquidity","time of logging"]
				wtr.writerow(columns)
				for action_data in data_to_write_to_csv:
					data_list = action_data.split(":")
					user_id, hrs_since_segment_init, action_categ, action_sub_categ, liquidity, time_of_action = data_list[0],\
					data_list[1],data_list[2],data_list[3], data_list[4], data_list[5]
					to_write = [user_id, hrs_since_segment_init, action_categ, action_sub_categ, liquidity, exact_date(float(time_of_action))]
					wtr.writerows([to_write])
	raise Http404("Completed logging ;)")


