from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from fc3.fantasy.models import Series, Race, Athlete, Guess, Result

@login_required
def root(request):
    qs = Series.objects.all()
    c = RequestContext(request, {
        'series_list': qs,
    })
    return render_to_response('series_list.html', c)

@login_required
def series_edit(request, id=None):
    '''
    Create a new Series or edit an existing Series.
    
    '''
    from fantasy.forms import SeriesForm

    #scup = request.session.get('scup')
    #service_client = scup.service_client

    if id:
        series = get_object_or_404(Series, pk=id)
    else:
        series = Series(owner=request.user)

    if request.method == 'POST':
        series_form = SeriesForm(data=request.POST, instance=series)
        if series_form.is_valid():
            series = series_form.save(commit=False)
            series.owner = request.user
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
def series_detail(request, id):
    '''
    A list of races for the series, with winner if applicable, and user's current guess if applicable.
    
    '''
    series = get_object_or_404(Series, pk=id)
    qs = Race.objects.filter(series=series)
    races = []
    for race in qs:
        qs = Result.objects.filter(race=race, place=1)
        if not qs:
            winner = '?'
        elif len(qs) == 1:
            winner = str(qs[0].athlete)
        else:
            winner = ', '.join([str(result.athlete) for result in qs])
            
        try:
            guess = Guess.objects.get(race=race, user=request.user)
        except Guess.DoesNotExist:
            guess = None
        races.append({'race': race, 'winner': winner, 'guess': guess})
        
    c = RequestContext(request, {
        'series': series,
        'race_list': races,
        'is_admin': series.is_admin(request.user),
    })
    return render_to_response('race_list.html', c)

@login_required
def leaderboard(request, id):
    '''
    A list of user scores for races in the series.
    
    '''
    series = get_object_or_404(Series, pk=id)
    points_list = []
    users = User.objects.filter(guess__race__series=series)
    for u in users:
        guesses = Guess.objects.filter(race__series=series, user=u)
        points = 0
        for g in guesses:
            try:
                r = Result.objects.get(race=g.race, athlete=g.athlete)
                place = r.place
            except:
                place = 0
            points += F1Points(place)
        points_list.append({'name': str(u), 'points': points})
        
    import operator
    points_list.sort(key=operator.itemgetter('points'), reverse=True)
    c = RequestContext(request, {
        'series': series,
        'points_list': points_list,
    })
    return render_to_response('leaderboard.html', c)


F1PointMap = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
def F1Points(place):
    if place not in F1PointMap:
        return 0
    else:
        return F1PointMap[place]

@login_required
def athlete_list(request, id):
    '''
    List all athletes associated with this Series.
    
    '''
    series = get_object_or_404(Series, pk=id)
    qs = Athlete.objects.filter(series=series)
    c = RequestContext(request, {
        'series': series,
        'athlete_list': qs,
    })
    return render_to_response('athlete_list.html', c)

@login_required
def athlete_add(request, id):
    '''
    Add an athlete for the specified Series.
    
    '''
    from fantasy.forms import AthleteForm

    #scup = request.session.get('scup')
    #service_client = scup.service_client

    series = get_object_or_404(Series, pk=id)
    athlete = Athlete(series=series)

    if request.method == 'POST':
        athlete_form = AthleteForm(data=request.POST)
        if athlete_form.is_valid():
            athlete = athlete_form.save(commit=False)
            athlete.series = series
            athlete.save()
            next = request.GET.get('next', None)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('fantasy-athlete-list', args=[series.pk]))
    else:
        athlete_form = AthleteForm()

    c = RequestContext(request, {
        #'service_client': service_client,
        'athlete_form': athlete_form,
        'series': series,
        'athlete': athlete,
    })
    return render_to_response('athlete_edit.html', c)

@login_required
def athlete_edit(request, id):
    '''
    Edit the specified Athlete.
    
    '''
    from fantasy.forms import AthleteForm

    #scup = request.session.get('scup')
    #service_client = scup.service_client

    athlete = get_object_or_404(Athlete, pk=id)
    series = athlete.series

    if request.method == 'POST':
        athlete_form = AthleteForm(data=request.POST, instance=athlete)
        if athlete_form.is_valid():
            athlete_form.save()
            return HttpResponseRedirect(reverse('fantasy-athlete-list', args=[series.pk]))
    else:
        athlete_form = AthleteForm(instance=athlete)

    c = RequestContext(request, {
        #'service_client': service_client,
        'athlete_form': athlete_form,
        'series': series,
        'athlete': athlete,
    })
    return render_to_response('athlete_edit.html', c)


@login_required
def race_add(request, id):
    '''
    Add a new race to the specified Series.
    
    '''
    from fantasy.forms import RaceForm

    #scup = request.session.get('scup')
    #service_client = scup.service_client

    series = get_object_or_404(Series, pk=id)
    race = Race(series=series)

    if request.method == 'POST':
        race_form = RaceForm(data=request.POST)
        if race_form.is_valid():
            race = race_form.save(commit=False)
            race.series = series
            race.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[series.pk]))
    else:
        race_form = RaceForm()

    c = RequestContext(request, {
        #'service_client': service_client,
        'race_form': race_form,
        'series': series,
        'race': race,
    })
    return render_to_response('race_edit.html', c)

@login_required
def race_edit(request, id):
    '''
    Edit the specified Race.
    
    '''
    from fantasy.forms import RaceForm

    #scup = request.session.get('scup')
    #service_client = scup.service_client

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
    })
    return render_to_response('race_edit.html', c)

@login_required
def race_detail(request, id):
    '''
    Shows either the results of a race
    or
    Allows user to select an Athlete he thinks will win the race
    or possibly enter a new Athlete.
    
    '''
    race = get_object_or_404(Race, pk=id)
    series = race.series
    
    from datetime import datetime
    start_time = datetime(race.date.year, race.date.month, race.date.day, race.start_time.hour, race.start_time.minute)
    if start_time < datetime.now():
        return race_result(request, id)
    
    qs = Result.objects.filter(race=race)
    try:
        guess = Guess.objects.get(race=race, user=request.user)
    except Guess.DoesNotExist:
        guess = None

    athletes = Athlete.objects.filter(series=race.series)
    from fantasy.forms import GuessForm

    if request.method == 'POST':
        guess_form = GuessForm(athletes, race.series.athlete_label, data=request.POST, instance=guess)
        if guess_form.is_valid():
            guess = guess_form.save(commit=False)
            guess.race = race
            guess.result = 1
            guess.user = request.user
            guess.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[race.series.pk]))
    else:
        guess_form = GuessForm(athletes, race.series.athlete_label, instance=guess)

    add_athlete_ok = series.users_enter_athletes
    
    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'guess_form': guess_form,
        'add_athlete_ok': add_athlete_ok,
    })
    return render_to_response('race_guess.html', c)

@login_required
def race_result(request, id):
    '''
    Shows the results of a race.
    
    '''
    race = get_object_or_404(Race, pk=id)
    series = race.series
    qs = Result.objects.filter(race=race)
    result_list = []
    for result in qs:
        guesses = Guess.objects.filter(user=request.user, athlete=result.athlete, race=race)
        picked_by = ', '.join([str(g.user) for g in guesses])
        result_list.append({'place': result.place, 'athlete': result.athlete, 'picked_by': picked_by})
        
    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'result_list': result_list,
        'is_admin': series.is_admin(request.user),
    })
    return render_to_response('race_result.html', c)

@login_required
def result_edit(request, id):
    '''
    Edit the results for a race.
    
    '''
    from django.forms.models import modelformset_factory
    
    race = get_object_or_404(Race, pk=id)
    series = race.series
    
    ResultFormSet = modelformset_factory(Result, fields=('athlete', 'place'), max_num=8, extra=8)

    if request.method == 'POST':
        formset = ResultFormSet(request.POST, queryset=Result.objects.filter(race=race))
        if formset.is_valid():
            results = formset.save(commit=False)
            for result in results:
                result.race = race
                result.save()
            return HttpResponseRedirect(reverse('fantasy-race-detail', args=[race.pk]))
    else:
        formset = ResultFormSet(queryset=Result.objects.filter(race=race))

    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'formset': formset,
    })
    return render_to_response('result_edit.html', c)
