#!/usr/bin/env python
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from fc3.fantasy.models import Series, Race, Athlete, Guess


attrs_dict = { 'class': 'required' }


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        exclude = ('owner', 'invite_only', 'only_members_can_view')


class AthleteForm(forms.ModelForm):
    class Meta:
        model = Athlete
        fields = ('name',)


class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        exclude  = ('series',)


class GuessForm(forms.ModelForm):
    class Meta:
        model = Guess
        fields = ('athlete',)

    def __init__(self, choices, label, *args, **kwargs):
        super(GuessForm, self).__init__(*args, **kwargs)
        self['athlete'].field.queryset = choices
        self['athlete'].field.label = label
        self['athlete'].field.help_text = 'My pick to win'
