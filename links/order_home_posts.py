from operator import itemgetter
from home_post_rating_algos import wilson_score, aggregate_post_score
from redis1 import set_best_posts_on_home, retrieve_all_home_links_with_scores

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

def order_home_posts(urdu_only=False):
	result1, all_link_ids = retrieve_all_home_links_with_scores(score_type='votes',urdu_only=urdu_only)
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
	set_best_posts_on_home(link_ids=strip_score(sorted_posts),urdu_only=urdu_only)

def order_home_posts2(urdu_only=False):
	list_of_scores, list_of_ids = retrieve_all_home_links_with_scores(score_type='comments',urdu_only=urdu_only)
	links_with_comment_score = aggregate_post_score(list_of_scores, list_of_ids)
	sorted_posts = sort_home_posts_acc_to_score(links_with_comment_score)
	set_best_posts_on_home(link_ids=strip_score(sorted_posts),urdu_only=urdu_only)
