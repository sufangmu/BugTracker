#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: widgets.py
from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):
    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'
