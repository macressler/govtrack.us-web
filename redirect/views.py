# -*- coding: utf-8 -*-
import re

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect

from common.decorators import render_to
from common.pagination import paginate

from person.models import Person
from committee.models import Committee
from bill.models import Bill, BillType, BillTerm, TermType

BILL_TOKEN_REGEXP = re.compile('^([a-z]+)(\d+)-(\d+)$')

def person_redirect(request):
    pk = request.GET.get('id', None)
    person = get_object_or_404(Person, pk=pk)
    return redirect(person, permanent=True)

def district_maps_redirect(request):
    url = "/congress/members"
    if "state" in request.GET: url += "/" + request.GET["state"]
    if "district" in request.GET: url += "/" + request.GET["district"]
    return HttpResponseRedirect(url)
    
def committee_redirect(request):
    pk = request.GET.get('id', None)
    if pk == None:
        return redirect("/congress/committees", permanent=True)
    elif len(pk) > 4:
        parent_pk = pk[:4]
        child_pk = pk[4:]
        committee = get_object_or_404(Committee, code=child_pk, committee__code=parent_pk)
    else:
        committee = get_object_or_404(Committee, code=pk)
    return redirect(committee, permanent=True)


def bill_redirect(request, istext=None):
    """
    Redirect requests to obsolete bill urls which look like:

        /congress/bill.xpd?bill=[type_code][congress_number]-[bill_num]
    """

    token = request.GET.get('bill', '')
    match = BILL_TOKEN_REGEXP.search(token)
    if not match:
        raise Http404()
    type_code, congress, number = match.groups()
    try:
        bill_type = BillType.by_xml_code(type_code)
    except BillType.NotFound:
        raise Http404()
    bill = get_object_or_404(Bill, bill_type=bill_type, congress=congress,
                             number=number)
    return redirect(bill.get_absolute_url() + ("" if not istext else "/text"), permanent=True)

def bill_search_redirect(request):
    return HttpResponseRedirect("/congress/bills/browse")

def subject_redirect(request):
    try:
        term = get_object_or_404(BillTerm, name=request.GET["term"], term_type=TermType.new)
    except:
        term = get_object_or_404(BillTerm, name=request.GET["term"], term_type=TermType.old)
    return redirect(term.get_absolute_url(), permanent=True)

def vote_redirect(request):
    a, roll = request.GET["vote"].split("-")
    chamber = a[0]
    session = a[1:]
    from us import get_all_sessions
    for cong, sess, start, end in get_all_sessions():
        if sess == session:
            return HttpResponseRedirect("/congress/votes/%s-%s/%s%s" % (cong, sess, chamber, roll))
    raise Http404()
