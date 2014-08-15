# -*- coding: utf-8 -*-
import operator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q
from .models import Votes, Councilors_Votes
from search.views import keyword_list, keyword_been_searched, keyword_normalize


def votes(request, election_year, county, index='normal'):
    result = None
    if index == 'conscience':
        query = Q(conflict=True)
    else:
        query = Q()
    #--> 依表決結果分類
    if 'result' in request.GET:
        result = request.GET['result']
        query = query & Q(result=result)
    #<--
    keyword = keyword_normalize(request.GET)
    if keyword:
        votes = Votes.objects.filter(query & reduce(operator.and_, (Q(content__icontains=x) for x in keyword.split()))).order_by('-date', 'vote_seq')
        if votes:
            keyword_been_searched(keyword, 'votes')
    else:
        votes = Votes.objects.filter(query).order_by('-date', 'vote_seq')
    return render(request,'votes/votes.html', {'election_year': election_year, 'county': county, 'votes': votes, 'index':index, 'keyword':keyword, 'result':result, 'keyword_hot': keyword_list('votes')})

def vote(request, vote_id):
    data = None
    vote = Councilors_Votes.objects.select_related().filter(vote_id=vote_id).order_by('-decision', 'councilor__party')
    try:
        data = dict(Votes.objects.get(uid=vote_id).results)
        data.pop('total', None)
    except Exception, e:
        print e
        return HttpResponseRedirect('/')
    return render(request,'votes/vote.html', {'vote':vote, 'data':data})
