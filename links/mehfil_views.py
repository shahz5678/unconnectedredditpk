from django.views.generic.edit import FormView
from mehfil_forms import GroupHelpForm, ReinviteForm, OpenGroupHelpForm, ClosedGroupHelpForm

########################## Mehfil Help #########################

class GroupHelpView(FormView):
	"""
    Renders the help page for mehfils
    """
	form_class = GroupHelpForm
	template_name = "mehfil/group_help.html"

#################### Inviting users to mehfils #####################

class ReinviteView(FormView):
	"""
    Renders error message if someone tries to 'double-invite' a user to a public mehfil
    """
	form_class = ReinviteForm
	template_name = "mehfil/reinvite.html"

	def get_context_data(self, **kwargs):
		context = super(ReinviteView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.kwargs.get("slug")
			context["unique"] = unique
		return context

########################## Mehfil creation #########################

class OpenGroupHelpView(FormView):
	"""
    Renders form where user has to decide whether they are willing to pay the required price
    """
	form_class = OpenGroupHelpForm
	template_name = "mehfil/open_group_help.html"


class ClosedGroupHelpView(FormView):
	"""
    Renders form where user has to decide whether they are willing to pay the required price
    """
	form_class = ClosedGroupHelpForm
	template_name = "mehfil/closed_group_help.html"	