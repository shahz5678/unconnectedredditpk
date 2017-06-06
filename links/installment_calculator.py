from django.shortcuts import render
from installment_forms import CalculatorForm
from redis4 import get_historical_calcs

def calculator(request,*args,**kwargs):
	if request.method == 'POST':
		form = CalculatorForm(request.POST)
		if form.is_valid():
			base_price = form.cleaned_data.get("base_price",None)
			time_period_in_months = form.cleaned_data.get("time_period_in_months",None)
			CAGR = 0.6
			num_of_years = time_period_in_months/12.0
			ending_value = ((CAGR+1)**num_of_years)*base_price
			monthly_installment = ending_value/time_period_in_months
			history = get_historical_calcs(base_price, time_period_in_months, monthly_installment, ending_value)
			if history is not None:
				sorted(history,key=lambda x: x['id'])
			return render(request,"installment_calculator.html",{'form':form,'installment':monthly_installment,'months':time_period_in_months,\
				'history':history})	
		else:
			history = get_historical_calcs()
			if history is not None:
				sorted(history,key=lambda x: x['id'])
			return render(request,"installment_calculator.html",{'form':form, 'history':history})	
	else:
		form = CalculatorForm()
		history = get_historical_calcs()
		if history is not None:
			sorted(history,key=lambda x: x['id'])
		return render(request,"installment_calculator.html",{'form':form, 'history':history})