# -*- coding: utf8 -*-
from __future__ import print_function
from PyLUCCBA.examples import studies_constant_settings as cs
import PyLUCCBA as cc


scenarizer = lambda name : cc.CBACalculator(
    run_name               = 'Grassland-Cropland_DR=0.03_CP=%s_PbLookup'%name,
    project_horizon        = 150,
    T_so                   = 20,
    T_vg_diff              = 1,
    T_vg_unif              = 20,
    discount_rate          = .03,
    co2_prices_scenario    = name,
    initial_landuse        = 'improved grassland',
    final_landuse          = 'wheat',
    input_flows_scenario   = 'IFP',
    **cs.other_parameters
)

co2_prices_scenarios = [
    'WEO2015-CPS',
    'WEO2015-NPS',
    'WEO2015-450S',
    'SPC',
    'O'
]

objects = {}
for s_name in co2_prices_scenarios:    
    cba = scenarizer(s_name)
    #cba.all_charts
    objects[cba.run_name] = {'summary':cba.summary_args,'object':cba}



print(u"""
*******************************************************************************
            ╔═╗┬ ┬┌┬┐┌┬┐┌─┐┬─┐┬┌─┐┌─┐                                         *
            ╚═╗│ │││││││├─┤├┬┘│├┤ └─┐                                         *
            ╚═╝└─┘┴ ┴┴ ┴┴ ┴┴└─┴└─┘└─┘                                         *
*******************************************************************************""")
for run_name, dico in objects.items():
    print(dico['summary'])
    dico['object'].all_XLSXed

