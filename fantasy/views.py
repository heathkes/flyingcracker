from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from fc3.fantasy.models import Series, Race, Competitor, Guess, Result
from serviceclient.models import ServiceClient, ServiceClientUserProfile as SCUP
from serviceclient.decorators import set_scup

@login_required
@set_scup
def root(request):
    scup = request.session.get('scup')
    service_client = scup.service_client
    
    qs = Series.objects.all()
    # BUGBUG
    # filter to:
    #   series for which I am admin
    # plus
    #   series which have 1+ associated Race and 2+ associated Athletes
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

@login_required
@set_scup
def series_detail(request, id):
    '''
    A list of races for the series, with winner if applicable, and user's current guess if applicable.
    
    '''
    scup = request.session.get('scup')
    service_client = scup.service_client
    
    series = get_object_or_404(Series, pk=id)
    qs = Race.objects.filter(series=series)
    races = []
    for race in qs:
        qs = Result.objects.filter(race=race, place=1)
        if not qs:
            winner = '?'
        else:
            winner = ', '.join([str(result.competitor) for result in qs])
            
        qs = Guess.objects.filter(race=race, user=scup)
        if not qs:
            guesses = None
        else:
            guesses = [str(guess.competitor) for guess in qs]
        races.append({'race': race, 'winner': winner, 'guesses': guesses})
        
    c = RequestContext(request, {
        'series': series,
        'race_list': races,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('race_list.html', c)

def series_points_list(series):
    points_list = []
    users = SCUP.objects.filter(guess__race__series=series).distinct()
    for u in users:
        guesses = Guess.objects.filter(race__series=series, user=u)
        points = 0
        for g in guesses:
            try:
                r = Result.objects.get(race=g.race, competitor=g.competitor)
                place = r.place
            except:
                place = 0
            points += series.scoring_system.points(place)
        points_list.append({'name': str(u.user.username), 'points': points})
        
    import operator
    points_list.sort(key=operator.itemgetter('points'), reverse=True)
    
    # Return an empty list if there are no points
    if points_list and points_list[0]['points'] == 0:
        points_list = []
    return points_list
    
@login_required
@set_scup
def leaderboard(request, id):
    '''
    A list of user scores for races in the series.
    
    '''
    scup = request.session.get('scup')
    service_client = scup.service_client

    series = get_object_or_404(Series, pk=id)
    points_list = series_points_list(series)
    user_list = SCUP.objects.filter(guess__race__series=series).distinct()
    c = RequestContext(request, {
        'series': series,
        'points_list': points_list,
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
def race_add(request, id):
    '''
    Add a new race to the specified Series.
    
    '''
    from fc3.fantasy.forms import RaceForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    series = get_object_or_404(Series, pk=id)
    race = Race(series=series)

    if request.method == 'POST':
        race_form = RaceForm(data=request.POST, instance=race)
        if race_form.is_valid():
            race = race_form.save(commit=False)
            race.series = series
            race.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[series.pk]))
    else:
        race_form = RaceForm(instance=race)

    c = RequestContext(request, {
        #'service_client': service_client,
        'race_form': race_form,
        'series': series,
        'race': race,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('race_edit.html', c)

@login_required
@set_scup
def race_edit(request, id):
    '''
    Edit the specified Race.
    
    '''
    from fc3.fantasy.forms import RaceForm

    scup = request.session.get('scup')
    service_client = scup.service_client

    race = get_object_or_404(Race, pk=id)
    series = race.series

    if request.method == 'POST':
        race_form = RaceForm(data=request.POST, instance=race)
        if race_form.is_valid():
            race = race_form.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[series.pk]))
    else:
        race_form = RaceForm(instance=race)

    c = RequestContext(request, {
        #'service_client': service_client,
        'race_form': race_form,
        'series': series,
        'race': race,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('race_edit.html', c)

@login_required
@set_scup
def race_delete(request, id):
    '''
    Delete the specified Race from the Series.
    
    '''
    scup = request.session.get('scup')
    service_client = scup.service_client

    race = get_object_or_404(Race, pk=id)
    series = race.series

    results = Result.objects.filter(race=race)
    if results:
        c = RequestContext(request, {
            'series': series,
            'race': race,
            'result_list': results,
            'is_admin': series.is_admin(scup),
        })
        return render_to_response('race_delete.html', c)
    else:
        race.delete()
        return HttpResponseRedirect(series.get_absolute_url)

@login_required
@set_scup
def race_detail(request, id):
    '''
    Shows either the results of a race
    or
    Allows user to select an Competitor he thinks will win the race
    or possibly enter a new Competitor.
    
    '''
    from fc3.fantasy.forms import CompetitorForm

    scup = request.session.get('scup')
    service_client = scup.service_client
    
    race = get_object_or_404(Race, pk=id)
    series = race.series
    competitor = Competitor(series=series)
    
    from datetime import datetime
    start_time = datetime(race.date.year, race.date.month, race.date.day, race.start_time.hour, race.start_time.minute)
    #
    #  If Race start time has passed don't allow guessing
    #
    if start_time < datetime.now():
        return race_result(request, id)

    #
    #  Otherwise, solicit guess(es).
    #
    from fc3.fantasy.forms import GuessForm, GuessAndResultBaseFormset
    from django.forms.formsets import formset_factory

    GuessFormset = formset_factory(GuessForm, GuessAndResultBaseFormset,
                                    max_num=series.num_guesses, extra=series.num_guesses)

    competitor_choices = [('', '------')]
    competitor_choices.extend([(a.pk, str(a)) for a in Competitor.objects.filter(series=series)])
    
    curr_guesses = Guess.objects.filter(race=race, user=scup)
    guesses = [{'competitor': r.competitor.pk} for r in curr_guesses]

    if request.method == 'POST':
        formset = GuessFormset(request.POST, initial=guesses, competitors=competitor_choices)
        competitor_form = CompetitorForm(data=request.POST, instance=competitor)
        
        if request.POST.get('guess', None) != u'Submit Picks':
            if competitor_form.is_valid():
                competitor = competitor_form.save(commit=False)
                competitor.series = series
                competitor.save()
                return HttpResponseRedirect(reverse('fantasy-race-detail', args=[race.pk]))
        else:
            if formset.is_valid():
                curr_guesses.delete()   # delete all existing guesses for this race
                for guess in formset.cleaned_data:
                    if guess.get('competitor', None):
                        g = Guess(race=race,
                                  user=scup,
                                  competitor=Competitor.objects.get(pk=guess['competitor']))
                        g.save()
                return HttpResponseRedirect(reverse('fantasy-series-detail', args=[race.series.pk]))
    else:
        formset = GuessFormset(initial=guesses, competitors=competitor_choices)
        competitor_form = CompetitorForm(instance=competitor)

    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'points_list': series_points_list(series)[:10],
        'competitor_form': competitor_form,
        'formset': formset,
        'add_competitor_ok': series.users_enter_competitors,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('race_guess.html', c)

@login_required
@set_scup
def race_result(request, id):
    '''
    Shows the results of a race.
    
    '''
    scup = request.session.get('scup')
    service_client = scup.service_client
    
    race = get_object_or_404(Race, pk=id)
    series = race.series
    qs = Result.objects.filter(race=race)
        
    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'result_list': qs,
        'points_list': series_points_list(series)[:10],
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('race_result.html', c)

@login_required
@set_scup
def result_edit(request, id):
    '''
    Edit the results for a race.
    
    '''
    from fc3.fantasy.forms import ResultForm, GuessAndResultBaseFormset
    from django.forms.formsets import formset_factory
    
    scup = request.session.get('scup')
    service_client = scup.service_client
    
    race = get_object_or_404(Race, pk=id)
    series = race.series

    ResultFormset = formset_factory(ResultForm, GuessAndResultBaseFormset,
                                    max_num=series.scoring_system.num_places)

    competitor_choices = [('', '------')]
    competitor_choices.extend([(a.pk, str(a)) for a in Competitor.objects.filter(series=series)])
    
    curr_results = Result.objects.filter(race=race)
    if not curr_results:
        results = [{'place': i} for i in range(1, series.scoring_system.num_places+1)]
    else:
        results = [{'place': r.place, 'competitor': r.competitor.pk} for r in curr_results]
        results.extend([{'place': ''} for i in range(0, series.scoring_system.num_places - len(curr_results))])
        
    if request.method == 'POST':
        formset = ResultFormset(request.POST, initial=results, competitors=competitor_choices)
        if formset.is_valid():
            curr_results.delete()   # delete all existing results for this race
            for result in formset.cleaned_data:
                if result['place'] and result['competitor']:
                    r = Result(race=race,
                               place=result['place'],
                               competitor=Competitor.objects.get(pk=result['competitor']))
                    r.save()
            return HttpResponseRedirect(reverse('fantasy-race-detail', args=[race.pk]))
    else:
        formset = ResultFormset(initial=results, competitors=competitor_choices)

    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'formset': formset,
        'is_admin': series.is_admin(scup),
    })
    return render_to_response('result_edit.html', c)
