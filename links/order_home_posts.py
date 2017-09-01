# Wilson Score Interval (source: http://www.evanmiller.org/how-not-to-sort-by-average-rating.html)

from math import sqrt

# this returns a rating-based score
def wilson_score(upvotes, downvotes):
    n = upvotes + downvotes
    if n < 1:
        return 0
    else:
	    z = 1.04 #1.04 = 70%, 1.44 = 85%, 1.96 = 95% (source: https://www.ltcconline.net/greenl/courses/201/Estimation/smallConfLevelTable.htm)
	    p_hat = float(upvotes) / n
	    return ((p_hat + z*z/(2*n) - z * sqrt((p_hat*(1-p_hat)+z*z/(4*n))/n))/(1+z*z/n))

# this returns a comment-count based score

#########################################################################################

from redis1 import retrieve_all_home_links_with_scores
from operator import itemgetter
from redis1 import set_best_posts_on_home

def get_upvotes_and_downvotes(post_and_votes):
	all_those_who_voted = []
	upvotes = 0
	downvotes = 0
	for username, vote_value in post_and_votes:
		# ensure double votes are not counted
		if username not in all_those_who_voted:
			if int(vote_value) < 0:
				# this is a downvote
				downvotes += 1
			else:
				upvotes += 1
		all_those_who_voted.append(username)
	return upvotes, downvotes

def score_home_posts(posts_with_cumm_upvotes_and_downvotes):
	scored_posts = []
	for post_id, upvotes, downvotes in posts_with_cumm_upvotes_and_downvotes:
		scored_posts.append((post_id,wilson_score(upvotes,downvotes)))
	return scored_posts

def sort_home_posts_acc_to_score(posts_with_scores):
	return sorted(posts_with_scores, key=itemgetter(1)) 

def strip_score(sorted_posts):
	# turning list of tuples into a simple, flat list using the first element of each tuple
	return map(itemgetter(0), sorted_posts)

def order_home_posts():
	result1, all_link_ids = retrieve_all_home_links_with_scores()
	counter, links_with_votes = 0, []
	for link_id in all_link_ids:
		if result1[counter]:
			upvotes, downvotes = get_upvotes_and_downvotes(result1[counter])
			links_with_votes.append((link_id,upvotes,downvotes))
		else:
			links_with_votes.append((link_id,0,0))
		counter += 1
	scored_posts = score_home_posts(links_with_votes)
	sorted_posts = sort_home_posts_acc_to_score(scored_posts)
	set_best_posts_on_home(strip_score(sorted_posts))