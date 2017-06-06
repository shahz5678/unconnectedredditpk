from django import forms

class CalculatorForm(forms.Form):
	base_price = forms.IntegerField()
	time_period_in_months = forms.IntegerField()

	def __init__(self,*args,**kwargs):
		super(CalculatorForm, self).__init__(*args,**kwargs)
		self.fields['base_price'].widget.attrs['autocomplete'] = 'off'
		self.fields['time_period_in_months'].widget.attrs['autocomplete'] = 'off'

	# def clean_base_price(self):
	# 	base_price = self.cleaned_data.get("base_price")
	# 	base_price = base_price.strip()
	# 	return base_price

	# def clean_time_period_in_months(self):
	# 	time_period_in_months = self.cleaned_data.get("time_period_in_months")
	# 	time_period_in_months = time_period_in_months.strip()
	# 	return time_period_in_months