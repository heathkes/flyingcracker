from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.contrib.contenttypes.models import ContentType
from fc3.fantasy.models import Series, Event, Competitor, Guess, Result
from serviceclient.models import ServiceClient, ServiceClientUserProfile as SCUP
from serviceclient.decorators import set_scup, get_scup

def root(request):
    if request.user.is_authenticated():
        scup = get_scup(request)
        service_client = scup.service_client
        if scup and scup.user.is_staff:
            qs = Series.objects.all()
        else:
            qs = Series.objects.filter(~Q(status=Series.HIDDEN_STATUS) | Q(owner=scup)).distinct()
    else:
        scup = None
        service_client = None
        qs = Series.objects.filter(~Q(status=Series.HIDDEN_STATUS)).distinct()
    
    # BUGBUG
    # filter to:
    #   series for which I am admin
    # plus
    #   series which have 1+ associated Event and 2+ associated Athletes
    c = RequestContext(request, {
        'series_list': qs,
        'scup': scup,
    })
    return render_to_response('series_list.html', c)

@login_required
@set_scup
def series_edit(request, id=None):
    '''
    Create a new Series or edit an existing Series.
    
    '''
    from fc3.fantasy.forms import SeriesForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    if id:
        series = get_object_or_404(Series, pk=id)
        if not series.is_admin(scup):
            # cannot edit Series if you're not an admin
            return HttpResponseRedirect(reverse('fantasy-root'))
    else:
        series = Series(owner=scup)

    if request.method == 'POST':
        series_form = SeriesForm(data=request.POST, instance=series)
        if series_form.is_valid():
            series = series_form.save(commit=False)
            series.owner = scup
            series.save()
            return HttpResponseRedirect(reverse('fantasy-root'))
    else:
        series_form = SeriesForm(instance=series)

    c = RequestContext(request, {
        #'service_client': service_client,
        'series_form': series_form,
        'series': series,
    })
    return render_to_response('series_edit.html', c)

def series_detail(request, id):
    '''
    A list of events for the series, with winner if applicable, and user's current guess if applicable.
    
    '''
    if request.user.is_authenticated():
        scup = get_scup(request)
        service_client = scup.service_client
    else:
        scup = None
        service_client = None
    
    series = get_object_or_404(Series, pk=id)
    qs = Event.objects.filter(series=series)
    events = []
    row_class = 'race-complete'
    for event in qs:
        results = Result.objects.filter(event=event)
        if event.start_time_elapsed() and results and event.result_locked:
            row_class = 'race-complete'
        else:
            if not series.guess_once_per_series and event.guess_deadline_elapsed():
                row_class = 'guess-deadline'
            else:
                row_class = 'race-future'
            
        if scup:
            ctype, obj_id = event.guess_generics()
            picks = Competitor.objects.filter(guess__content_type=ctype, guess__object_id=obj_id, guess__user=scup)
            if not picks:
                guesses = None
            else:
                guesses = []
                for pick in picks:
                    result_qs = Result.objects.filter(event=event, competitor=pick)
                    if not result_qs:
                        guesses.append(pick)
                    else:
                        result_text = ' & '.join([r.result for r in result_qs])
                        guesses.append(u'(%s) ' % result_text + unicode(pick))
            events.append({'event': event, 'guesses': guesses, 'row_class': row_class})
        else:
            events.append({'event': event, 'guesses': None, 'row_class': row_class})
        
    c = RequestContext(request, {
        'series': series,
        'event_list': events,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('event_list.html', c)
    
def series_points_list(series):
    '''
    Returns a list of usernames and their accumulated points in a Series.
    
    '''
    import copy
    
    points_list = []
    
    scoresys_results = series.scoring_system.results()
    result_blank = dict.fromkeys(scoresys_results, 0)
    
    event_blank = {}
    # create a list of dictionaries of all events, ordered by date
    # where the key is the event itself and the value is either
    # zero (for events that have occurred) or some other character.
    events = Event.objects.filter(series=series)
    for event in events:
        if event.guess_deadline_elapsed():
            event_blank[event] = 0
        else:
            event_blank[event] = '-'
        
    result_keys = result_blank.keys()
    result_keys.sort()
    event_keys = events # Event queryset should already be properly sorted

    user_list = series.guesser_list()
    for u in user_list:
        
        if series.guess_once_per_series:
            result_qs = Result.objects.filter(event__result_locked=True,
                                              event__series=series,
                                              event__series__guesses__user=u,
                                              event__series__guesses__competitor=F('competitor'))
        else:
            result_qs = Result.objects.filter(event__result_locked=True,
                                              event__series=series,
                                              event__guesses__user=u,
                                              event__guesses__competitor=F('competitor'))
        points = 0
        result_totals = copy.copy(result_blank)
        event_points = copy.copy(event_blank)
        for r in result_qs:
            result_points = series.scoring_system.points(r.result)
            points += result_points
            
            # number of times user's guess resulted in points for each place
            if r.result in scoresys_results:
                result_totals[r.result] += 1
                
            # total points for each event
            event_points[r.event] += result_points
            
        points_list.append({'name': str(u.user.username),
                            'points': points,
                            'place_totals': [{'key':key, 'val':result_totals[key]} for key in result_keys],
                            'event_points': [{'key':key, 'val':event_points[key]} for key in event_keys]}
                                             )
        
    import operator
    points_list.sort(key=operator.itemgetter('points'), reverse=True)
    
    # Return an empty list if there are no points
    if points_list and points_list[0]['points'] == 0:
        points_list = []
    return points_list
    
def leaderboard(request, id):
    '''
    A list of user scores for events in the series.
    
    '''
    if request.user.is_authenticated():
        scup = get_scup(request)
        service_client = scup.service_client
    else:
        scup = None
        service_client = None

    series = get_object_or_404(Series, pk=id)
    user_list = series.guesser_list()
    scoresys_results = series.scoring_system.results()
    #scoresys_results = sorted(series.scoring_system.results(), key=int)
    c = RequestContext(request, {
        'series': series,
        'points_list': series_points_list(series),
        'scoresys_results': scoresys_results,
        'user_list': user_list,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('leaderboard.html', c)

@login_required
@set_scup
def competitor_list(request, id):
    '''
    List all competitors associated with this Series.
    
    '''
    from fc3.fantasy.forms import CompetitorForm
    
    scup = request.session.get('scup')
    service_client = scup.service_client
    
    series = get_object_or_404(Series, pk=id)
    if not series.is_admin(scup):
        # cannot edit Series data if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))
    competitor = Competitor(series=series)

    if request.method == 'POST':
        competitor_form = CompetitorForm(data=request.POST, instance=competitor)
        if competitor_form.is_valid():
            competitor = competitor_form.save(commit=False)
            competitor.series = series
            competitor.save()
            next = request.GET.get('next', None)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('fantasy-competitor-list', args=[series.pk]))
            
    else:
        competitor_form = CompetitorForm(instance=competitor)
    
    qs = Competitor.objects.filter(series=series)
    c = RequestContext(request, {
        'series': series,
        'competitor_list': qs,
        'competitor_form': competitor_form,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('competitor_list.html', c)

@login_required
@set_scup
def competitor_add(request, id):
    '''
    Add a competitor for the specified Series.
    
    '''
    from fc3.fantasy.forms import CompetitorForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    series = get_object_or_404(Series, pk=id)
    if not series.is_admin(scup) and not series.users_enter_competitors:
        # cannot edit Series if you're not an admin and users not allowed to enter competitors
        return HttpResponseRedirect(reverse('fantasy-root'))
    competitor = Competitor(series=series)

    if request.method == 'POST':
        competitor_form = CompetitorForm(data=request.POST, instance=competitor)
        if competitor_form.is_valid():
            competitor = competitor_form.save(commit=False)
            competitor.series = series
            competitor.save()
            next = request.GET.get('next', None)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('fantasy-competitor-list', args=[series.pk]))
            
    else:
        competitor_form = CompetitorForm(instance=competitor)

    c = RequestContext(request, {
        'competitor_form': competitor_form,
        'series': series,
        'competitor': competitor,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('competitor_edit.html', c)

@login_required
@set_scup
def competitor_edit(request, id):
    '''
    Edit the specified Competitor.
    
    '''
    from fc3.fantasy.forms import CompetitorForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    competitor = get_object_or_404(Competitor, pk=id)
    series = competitor.series
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))

    if request.method == 'POST':
        competitor_form = CompetitorForm(data=request.POST, instance=competitor, initial={'series_pk': series.pk})
        if competitor_form.is_valid():
            competitor_form.save()
            return HttpResponseRedirect(reverse('fantasy-competitor-list', args=[series.pk]))
    else:
        competitor_form = CompetitorForm(instance=competitor, initial={'series_pk': series.pk})

    c = RequestContext(request, {
        'competitor_form': competitor_form,
        'series': series,
        'competitor': competitor,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('competitor_edit.html', c)

@login_required
@set_scup
def competitor_delete(request, id):
    '''
    Delete the specified Competitor from its Series.
    
    '''
    scup = request.session.get('scup')
    service_client = scup.service_client

    competitor = get_object_or_404(Competitor, pk=id)
    series = competitor.series
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))

    results = Result.objects.filter(competitor=competitor)
    if results:
        c = RequestContext(request, {
            'series': series,
            'competitor': competitor,
            'result_list': results,
            'is_admin': series.is_admin(scup),
        })
        return render_to_response('competitor_delete.html', c)
    else:
        competitor.delete()
        return HttpResponseRedirect(reverse('fantasy-competitor-list', args=[series.pk]))

@login_required
@set_scup
def competitor_export(request, id):
    '''
    Export all competitors associated with this Series.
    
    '''
    import csv
    from django.utils.encoding import smart_str, smart_unicode

    scup = request.session.get('scup')
    service_client = scup.service_client
    
    series = get_object_or_404(Series, pk=id)
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=competitor_list_series_%d.csv' % series.pk
    writer = csv.writer(response)
    
    writer.writerow(['name'])
    qs = Competitor.objects.filter(series=series)
    for competitor in qs:
        writer.writerow([smart_str(competitor.name)])
    return response

@login_required
@set_scup
def competitor_import(request, id):
    '''
    Import Competitors from other Series into the specified Series.
    
    '''
    from fc3.fantasy.forms import CompetitorImportForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    series = get_object_or_404(Series, pk=id)
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))

    qs = Series.objects.filter(only_members_can_view=False)
    #
    # BUGBUG - Add private Series, for which I am admin, to this queryset
    #
    if request.method == 'POST':
        import_form = CompetitorImportForm(data=request.POST, series_qs=qs)
        if import_form.is_valid():
            import_series = import_form.cleaned_data['series']
            if import_series:
                my_comps = Competitor.objects.filter(series=series)
                my_names = [c.name.lower() for c in my_comps]
                import_comps = Competitor.objects.filter(series=import_series)
                new_names = [c.name for c in import_comps if c.name.lower() not in my_names]
                for name in new_names:
                    new_competitor = Competitor(name=name, series=series)
                    new_competitor.save()
                c = RequestContext(request, {
                    'series': series,
                    'competitor_list': Competitor.objects.filter(name__in=new_names, series=series),
                    'is_admin': series.is_admin(scup),
                })
                return render_to_response('competitors_imported.html', c)
            else:
                return HttpResponseRedirect(reverse('fantasy-competitor-list', args=[series.pk]))
    else:
        import_form = CompetitorImportForm(series_qs=qs)

    c = RequestContext(request, {
        'import_form': import_form,
        'series': series,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('competitor_import.html', c)

@login_required
@set_scup
def event_add(request, series_id):
    '''
    Add a new event to the specified Series.
    
    '''
    from fc3.fantasy.forms import EventForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    series = get_object_or_404(Series, pk=series_id)
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))
    event = Event(series=series)

    if request.method == 'POST':
        event_form = EventForm(data=request.POST, instance=event)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.series = series
            event.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[series.pk]))
    else:
        event_form = EventForm(instance=event)

    c = RequestContext(request, {
        #'service_client': service_client,
        'event_form': event_form,
        'series': series,
        'event': event,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('event_edit.html', c)

@login_required
@set_scup
def event_edit(request, id):
    '''
    Edit the specified Event.
    
    '''
    from fc3.fantasy.forms import EventForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    event = get_object_or_404(Event, pk=id)
    series = event.series
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))

    if request.method == 'POST':
        event_form = EventForm(data=request.POST, instance=event)
        if event_form.is_valid():
            event = event_form.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[series.pk]))
    else:
        event_form = EventForm(instance=event)

    c = RequestContext(request, {
        #'service_client': service_client,
        'event_form': event_form,
        'series': series,
        'event': event,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('event_edit.html', c)

@login_required
@set_scup
def event_delete(request, id):
    '''
    Delete the specified Event from the Series.
    
    '''
    scup = request.session.get('scup')
    service_client = scup.service_client

    event = get_object_or_404(Event, pk=id)
    series = event.series
    if not series.is_admin(scup):
        # cannot edit Series if you're not an admin
        return HttpResponseRedirect(reverse('fantasy-root'))

    results = Result.objects.filter(event=event)
    if results:
        c = RequestContext(request, {
            'series': series,
            'event': event,
            'result_list': results,
            'points_list': series_points_list(series)[:10],
            'is_admin': series.is_admin(scup),
        })
        return render_to_response('event_delete.html', c)
    else:
        event.delete()
        return HttpResponseRedirect(series.get_absolute_url)

def event_detail(request, id):
    '''
    Shows either the results of a event
    or
    Allows user to select one or more Competitors he thinks will
    perform well, or possibly enter a new Competitor.
    
    '''
    from fc3.fantasy.forms import CompetitorForm

    if request.user.is_authenticated():
        scup = get_scup(request)
        service_client = scup.service_client
    else:
        scup = None
        service_client = None

    event = get_object_or_404(Event, pk=id)
    series = event.series
    # Create un-saved instance for adding a new Competitor
    competitor = Competitor(series=series)
    
    #
    #  If Event start time has passed don't allow guessing
    #
    if event.guess_deadline_elapsed():
        # if request.method == 'POST': redirect to some "sorry, you submitted your guess after the race start time (HH:MM UTC)." page.
        return event_result(request, id)

    #
    #  Otherwise, solicit guess(es).
    #
    from fc3.fantasy.forms import GuessForm, GuessAndResultBaseFormset
    from django.forms.formsets import formset_factory

    GuessFormset = formset_factory(GuessForm, GuessAndResultBaseFormset,
                                    max_num=series.num_guesses,
                                    extra=series.num_guesses)

    competitor_choices = [('', '------')]
    competitor_choices.extend([(a.pk, str(a)) for a in Competitor.objects.filter(series=series)])
    
    ctype, obj_id = event.guess_generics()
    curr_guesses = Guess.objects.filter(content_type=ctype, object_id=obj_id, user=scup)
    guesses = [{'competitor': r.competitor.pk} for r in curr_guesses]

    if request.method == 'POST':
        formset = GuessFormset(request.POST, initial=guesses, competitors=competitor_choices)
        competitor_form = CompetitorForm(data=request.POST, instance=competitor)
        
        # BUGBUG 7/2/09
        # Replace this method of determining which button was pressed.
        # Use code from eTrack entry_edit(), hidden field, javascript.
        if request.POST.get('guess', None) != u'Submit Picks':
            if competitor_form.is_valid():
                competitor = competitor_form.save(commit=False)
                competitor.series = series
                competitor.save()
                return HttpResponseRedirect(reverse('fantasy-event-detail', args=[event.pk]))
        else:
            if formset.is_valid():
                curr_guesses.delete()   # delete all existing guesses for this event
                for guess in formset.cleaned_data:
                    if guess.get('competitor', None):
                        g = Guess(content_type=ctype,
                                  object_id=obj_id,
                                  user=scup,
                                  competitor=Competitor.objects.get(pk=guess['competitor']))
                        g.save()
                return HttpResponseRedirect(reverse('fantasy-series-detail', args=[event.series.pk]))
    else:
        formset = GuessFormset(initial=guesses, competitors=competitor_choices)
        competitor_form = CompetitorForm(instance=competitor)

    guessers = event.guesser_list()

    c = RequestContext(request, {
        'series': event.series,
        'event': event,
        'points_list': series_points_list(series)[:10],
        'competitor_form': competitor_form,
        'formset': formset,
        'add_competitor_ok': series.users_enter_competitors,
        'is_admin': series.is_admin(scup),
        'guessers': guessers,
    })
    return render_to_response('event_guess.html', c)

def event_result(request, id):
    '''
    Shows the results of a event.
    
    '''
    if request.user.is_authenticated():
        scup = get_scup(request)
        service_client = scup.service_client
    else:
        scup = None
        service_client = None
    
    event = get_object_or_404(Event, pk=id)
    series = event.series

    if not event.guess_deadline_elapsed():
    # if request.method == 'POST': redirect to some "sorry, the race has not yet started." page.
        return HttpResponseRedirect(reverse('fantasy-root'))

    result_qs = Result.objects.filter(event=event, result__in=series.scoring_system.results())

    # Get the content_type and object_id for referencing guesses made for this Event.
    ctype, obj_id = event.guess_generics()

    bad_guess_list = []
    # list of results for this event where the place yielded no points.
    no_points_list = Result.objects.filter(~Q(result__in=series.scoring_system.results()), event=event).order_by('result')
    for result in no_points_list:
        guessers = Guess.objects.filter(content_type=ctype, object_id=obj_id, competitor=result.competitor)
        bad_guess_list.append({'competitor': result.competitor, 'place': result.result, 'guessers': [g.user for g in guessers ]})

    # list of competitors guessed for this event who have no result FOR THE EVENT
    all_guesses_qs = Competitor.objects.filter(guess__content_type=ctype, guess__object_id=obj_id).distinct()
    no_result_list = all_guesses_qs.exclude(result__event=event)
    for bad_guess in no_result_list:
        guessers = Guess.objects.filter(content_type=ctype, object_id=obj_id, competitor=bad_guess)
        bad_guess_list.append({'competitor': bad_guess, 'place': '?', 'guessers': [g.user for g in guessers ]})

    event_points_list = []
    user_list = series.guesser_list()
    for u in user_list:
        if series.guess_once_per_series:
            all_result_qs = Result.objects.filter(event=event,
                                              event__series__guesses__user=u,
                                              event__series__guesses__competitor=F('competitor'))
        else:
            all_result_qs = Result.objects.filter(event__result_locked=True,
                                              event__guesses__user=u,
                                              event__guesses__competitor=F('competitor'))
        points = 0
        for r in all_result_qs:
            result_points = series.scoring_system.points(r.result)
            points += result_points
            
        event_points_list.append({'name': str(u.user.username),
                            'points': points,
                                             })
        
    import operator
    event_points_list.sort(key=operator.itemgetter('points'), reverse=True)

    c = RequestContext(request, {
        'series': event.series,
        'event': event,
        'event_points_list': event_points_list,
        'result_list': result_qs,
        'points_list': series_points_list(series)[:10],
        'bad_guess_list': bad_guess_list,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('event_result.html', c)

@login_required
@set_scup
def result_edit(request, id):
    '''
    Edit the results for a event.
    
    '''
    from fc3.fantasy.forms import ResultForm, GuessAndResultBaseFormset, EventOptionsForm
    from django.forms.formsets import formset_factory
    
    scup = request.session.get('scup')
    service_client = scup.service_client
    
    event = get_object_or_404(Event, pk=id)
    series = event.series
    if (not series.is_admin(scup) and event.result_locked) or \
       not event.guess_deadline_elapsed():
        return HttpResponseRedirect(reverse('fantasy-root'))
    
    all_competitors = Competitor.objects.filter(series=series)
    competitor_choices = [('', '------')]
    competitor_choices.extend([(a.pk, str(a)) for a in all_competitors])
    
    curr_results = Result.objects.filter(event=event)
    
    all_result_list = series.scoring_system.results()
    ResultFormset = formset_factory(ResultForm, GuessAndResultBaseFormset,
                            max_num=len(all_result_list))

    # Create a list of results for this Event
    if not curr_results:
        results = [{'result': s} for s in all_result_list]
    else:
        results = [{'result': r.result, 'competitor': r.competitor.pk} for r in curr_results]
        curr_result_list = [r.result for r in curr_results]
        unassigned_results = list(set(all_result_list) - set(curr_result_list))
        unassigned_results.sort()
        results.extend([{'result': s} for s in unassigned_results])
        
    if request.method == 'POST':
        formset = ResultFormset(request.POST, initial=results, competitors=competitor_choices)
        options_form = EventOptionsForm(data=request.POST, instance=event)
        if formset.is_valid() and options_form.is_valid():
            event = options_form.save()
            curr_results.delete()   # delete all existing results for this event
            for result in formset.cleaned_data:
                if result['result'] and result['competitor']:
                    r = Result(event=event,
                               result=result['result'],
                               competitor=Competitor.objects.get(pk=result['competitor']),
                               entered_by=scup)
                    r.save()
            return HttpResponseRedirect(reverse('fantasy-event-detail', args=[event.pk]))
    else:
        formset = ResultFormset(initial=results, competitors=competitor_choices)
        options_form = EventOptionsForm(instance=event)

    c = RequestContext(request, {
        'series': event.series,
        'event': event,
        'formset': formset,
        'options_form': options_form,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('result_edit.html', c)
