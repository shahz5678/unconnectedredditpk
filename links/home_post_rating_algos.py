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
	return int(epoch_time+(len(text)*3))-1500000000


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