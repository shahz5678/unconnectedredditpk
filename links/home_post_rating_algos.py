from math import sqrt, log

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
	# give text size 3X importance. The following will work till September 13, 2020 (Pakistan Time)
	# return int(epoch_time+(len(text)*3))-1500000000
	length_of_text = len(text) if len(text) < 201 else 200
	return int(epoch_time+(1.15**length_of_text))-1500000000

# this returns a score based on diversity of comments, recency of comments, length of comments
# store user_ids and epoch_time_of_posting+comment_length in a sorted set. Cardinality will give diversity of comments, aggregate zscore will give recency
def aggregate_post_score(list_of_scores, list_of_ids):
	counter, links_with_comment_score = 0, []
	for link_id in list_of_ids:
		if list_of_scores[counter]:
			diversity_score_of_post = len(list_of_scores[counter]) #i.e. how many different users commented on the post
			if diversity_score_of_post == 1:
				diversity_score_of_post = log(1.9,2) #this is log to the base 2
			else:
				diversity_score_of_post = log(diversity_score_of_post,2) #this is log to the base 2
			recency_and_length_score_of_post = sum(tup[1] for tup in list_of_scores[counter]) 
			recency_and_length_score_of_post = log(recency_and_length_score_of_post,10) #this is log to the base 10
			links_with_comment_score.append((link_id,diversity_score_of_post+recency_and_length_score_of_post))
		else:
			links_with_comment_score.append((link_id,0))
		counter += 1
	return links_with_comment_score


# def set_rank(self): # it seems this is run ONLY when validating models is called (pressing ctrl S after changin code)
# 		# Based on reddit ranking algo at http://amix.dk/blog/post/19588
# 		epoch = datetime(1970, 1, 1).replace(tzinfo=None)
# 		netvotes = self.visible_score # 'NONE' votes are messing up netvotes amount.
# 		if netvotes == None:
# 			netvotes = 0
# 		order = log(max(abs(netvotes), 1), 10) #0.041392685 for zero votes, log 1 = 0
# 		sign = 1 if netvotes > 0 else -1 if netvotes < 0 else 0
# 		unaware_submission = self.upload_time.replace(tzinfo=None)
# 		td = unaware_submission - epoch 
# 		epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
# 		secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
# 		self.invisible_score = round(sign * order + secs / 45000, 8)
# 		score = self.invisible_score
# 		#self.save() # this persists the invisible_score in the database
# 		return score
# 		# the score doesn't decay as time goes by, but newer stories get a higher score over time. 