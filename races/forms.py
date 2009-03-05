#!/usr/bin/env python
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from fc3.races.models import Guess


attrs_dict = { 'class': 'required' }


class GuessForm(forms.ModelForm):
    class Meta:
        model = Guess
        fields = ('athlete',)

    def __init__(self, choices, label, *args, **kwargs):
        super(GuessForm, self).__init__(*args, **kwargs)
        self['athlete'].field.queryset = choices
        self['athlete'].field.label = label
