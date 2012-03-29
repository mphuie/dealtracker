# Create your views here.

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from deals.models import Deal, IgnoreList

def index(request):
	# deals = Deal.objects.all().order_by('-post_date')
	deals = Deal.objects.extra(where=["Deals_deal.id NOT IN (SELECT deal_id FROM deals_IgnoreList)"]).order_by('-last_post_date')[0:50]
	return render_to_response('index.html', { 'deals': deals }, context_instance=RequestContext(request))

def ignore(request, post_id):
	ignore = IgnoreList()
	ignore.deal = Deal.objects.get(post_id__exact=int(post_id))
	ignore.save()
	return HttpResponse(post_id)