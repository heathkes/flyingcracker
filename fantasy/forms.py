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
    series = forms.ModelChoiceField(queryset=Series.objects.all(), widget=forms.HiddenInput)
    
    class Meta:
        model = Athlete
        fields = ('name','series')
        
    def clean(self):
        name = self.cleaned_data.get('name')
        series = self.cleaned_data.get('series')
        if self.instance.pk:
            existing = Athlete.objects.filter(name__iexact=name, series=series).exclude(pk=self.instance.pk)
            if existing:
                raise forms.ValidationError, u'Athlete "%s" already exists for this series, try another name' % name
            else:
                return self.cleaned_data
        else:
            try:
                existing = Athlete.objects.get(name__iexact=name, series=series)
            except Athlete.DoesNotExist:
                return self.cleaned_data
            else:
                raise forms.ValidationError, u'Athlete "%s" already exists for this series, try another name' % name


class RaceForm(forms.ModelForm):
    series = forms.ModelChoiceField(queryset=Series.objects.all(), widget=forms.HiddenInput)
    
    class Meta:
        model = Race
        
    def clean(self):
        name = self.cleaned_data.get('name')
        series = self.cleaned_data.get('series')
        if self.instance.pk:
            existing = Race.objects.filter(name__iexact=name, series=series).exclude(pk=self.instance.pk)
            if existing:
                raise forms.ValidationError, u'Race "%s" already exists for this series, try another name' % name
            else:
                return self.cleaned_data
        else:
            try:
                existing = Race.objects.get(name__iexact=name, series=series)
            except Race.DoesNotExist:
                return self.cleaned_data
            else:
                raise forms.ValidationError, u'Race "%s" already exists for this series, try another name' % name


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
        self.athletes = kwargs.pop('athletes', None)
        super(ResultBaseFormset, self).__init__(*args, **kwargs)
    
    def _construct_form(self, i, **kwargs):
        kwargs["athletes"] = self.athletes
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
        athlete_list = kwargs.pop('athletes', None)
        super(ResultForm, self).__init__(*args, **kwargs)
        self['athlete'].field.choices = athlete_list

    def clean(self):
        place = self.cleaned_data.get('place', None)
        athlete = self.cleaned_data.get('athlete', None)
        if athlete and not place:
            raise forms.ValidationError, _(u'This athlete has no place!')
        return self.cleaned_data
    
