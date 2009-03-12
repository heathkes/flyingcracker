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
def series_detail(request, id):
    '''
    A list of races for the series, with winner if applicable, and user's current guess if applicable.
    
    '''
    series = get_object_or_404(Series, pk=id)
    qs = Race.objects.filter(series=series)
    races = []
    for race in qs:
        try:
            winner = Result.objects.get(race=race, place=1)
        except Result.DoesNotExist:
            winner = '?'
        try:
            guess = Guess.objects.get(race=race, user=request.user)
        except Guess.DoesNotExist:
            guess = None
        races.append({'race': race, 'winner': winner, 'guess': guess})
    c = RequestContext(request, {
        'series': series,
        'race_list': races,
    })
    return render_to_response('race_list.html', c)

@login_required
def race_detail(request, id):
    '''
    A list of athletes competing in a race.
    User chooses one in a form.
    
    '''
    race = get_object_or_404(Race, pk=id)
    qs = Result.objects.filter(race=race)
    try:
        winner = Result.objects.get(race=race, place=1)
    except Result.DoesNotExist:
        winner = None
    try:
        guess = Guess.objects.get(race=race, user=request.user)
    except Guess.DoesNotExist:
        guess = None

    '''
    form
    
    '''
    athletes = Athlete.objects.filter(series=race.series)
    from forms import GuessForm

    if request.method == 'POST':
        form = GuessForm(athletes, race.series.athlete_label, data=request.POST, instance=guess)
        if form.is_valid():
            guess = form.save(commit=False)
            guess.race = race
            guess.result = 1
            guess.user = request.user
            guess.save()
            return HttpResponseRedirect(reverse('fantasy-series-detail', args=[race.series.pk]))
    else:
        form = GuessForm(athletes, race.series.athlete_label, instance=guess)

    c = RequestContext(request, {
        'series': race.series,
        'race': race,
        'form': form,
    })
    return render_to_response('race_guess.html', c)

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
                r = Result.objects.get(race__series=series, athlete=g.athlete)
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
    