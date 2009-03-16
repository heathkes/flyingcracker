#!/usr/bin/env python
import datetime
from django import forms
from django.forms import formsets
from django.utils.translation import ugettext_lazy as _
from fc3.fantasy.models import Series, Race, Athlete, Guess, Result


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

class ResultBaseFormset(formsets.BaseFormSet):
    def __init__(self, *args, **kwargs):
        results = kwargs.pop("results", None)
        if results:
            self.results = list(results)
        else:
            self.results = None
        self.extra = 8
        super(ResultBaseFormset, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        if self.results:
            kwargs["result"] = self.results[i]
        return super(ResultBaseFormset, self)._construct_form(i, **kwargs)

    def clean(self):
        super(ResultBaseFormset,self).clean()
        if self.is_valid() and self.cleaned_data:
            athletes = [dct['athlete'] for dct in self.cleaned_data if dct['athlete']]
            if len(athletes) is not len(set(athletes)):
                raise forms.ValidationError, u'Duplicate competitor.'

class ResultForm(forms.Form):
    place = forms.IntegerField(required=False)
    athlete = forms.ChoiceField(choices=[], required=False)
    
    def __init__(self, *args, **kwargs):
        result = kwargs.pop("result", None)
        super(ResultForm, self).__init__(*args, **kwargs)
        if result:
            self['place'].field.value = result['place']
            self['athlete'].field.widget.choices = result['athletes']
            if result.get('choice', None):
                self['athlete'].field.selected = result['choice']
