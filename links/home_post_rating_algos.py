from math import sqrt, log
from operator import itemgetter
from redis3 import get_global_verified_users

# this returns a voting-based score
# Wilson Score Interval (source: http://www.evanmiller.org/how-not-to-sort-by-average-rating.html)
def wilson_score(upvotes, downvotes):
    n = upvotes + downvotes
    if n < 1:
        return 0
    else:
	    z = 1.04 #1.04 = 70%, 1.44 = 85%, 1.96 = 95% (source: https://www.ltcconline.net/greenl/courses/201/Estimation/smallConfLevelTable.htm)
	    p_hat = float(upvotes) / n
	    return ((p_hat + z*z/(2*n) - z * sqrt((p_hat*(1-p_hat)+z*z/(4*n))/n))/(1+z*z/n))

# this returns a score based on recency and length of comments (the -1500000000 part will work till September 13, 2020 Pakistan Time)
def recency_and_length_score(epoch_time, text):
	# give text size 1.15** importance. The following will work till September 13, 2020 (Pakistan Time)
	# return int(epoch_time+(len(text)*3))-1500000000
	length_of_text = len(text) if len(text) < 201 else 200
	return int(epoch_time+(1.15**length_of_text))-1500000000


def unpack_list_of_lists(list_of_scores):
	id_pairs = set()
	for list_ in list_of_scores:
		id_pairs.update(list(map(itemgetter(0), list_)))
	return unpack_ids(id_pairs)

def unpack_ids(id_pairs,distinct_writer=False):
	ids = set()	
	if distinct_writer:
		writer_id = id_pairs[0].split(":")[1]
	for pair in list(id_pairs):
		pair_list = pair.split(":")
		ids.add(pair_list[0])
		ids.add(pair_list[1])
	if distinct_writer:
		ids.remove(writer_id)
		return writer_id, ids
	else:
		return ids


def calc_verification_score(list_of_tup, verified_set_of_ids):
	score = 0
	list_of_id_pairs = list(map(itemgetter(0), list_of_tup))
	writer_id, replier_ids = unpack_ids(list_of_id_pairs,distinct_writer=True)
	if writer_id in verified_set_of_ids:
		score += 100
	for replier_id in list(replier_ids):
		if replier_id in verified_set_of_ids:
			score += 10
	return score

# this returns a score based on diversity of comments, recency of comments, length of comments
# store user_ids and epoch_time_of_posting+comment_length in a sorted set. Cardinality will give diversity of comments, aggregate zscore will give recency
def aggregate_post_score(list_of_scores, list_of_ids):
	counter, links_with_comment_score = 0, []
	user_id_set = unpack_list_of_lists(list_of_scores)
	verified_subset = user_id_set.intersection(set(get_global_verified_users()))
	for link_id in list_of_ids:
		if list_of_scores[counter]:
			diversity_score_of_post = len(list_of_scores[counter]) #i.e. how many different users commented on the post
			###### Taking Log to squeeze scores (normalize) into a comparable range ######
			if diversity_score_of_post == 1:
				pass
			else:
				diversity_score_of_post = log(diversity_score_of_post,1.5) #this is log to the base 1.5
			recency_and_length_score_of_post = sum(tup[1] for tup in list_of_scores[counter]) 
			recency_and_length_score_of_post = log(recency_and_length_score_of_post,10) #this is log to the base 10
			verification_score_of_post = calc_verification_score(list_of_scores[counter], verified_subset)
			if verification_score_of_post:
				verification_score_of_post = log(verification_score_of_post,10) #this is log to the base 10
			links_with_comment_score.append((link_id,diversity_score_of_post+recency_and_length_score_of_post))
		else:
			links_with_comment_score.append((link_id,0))
		counter += 1
	return links_with_comment_score