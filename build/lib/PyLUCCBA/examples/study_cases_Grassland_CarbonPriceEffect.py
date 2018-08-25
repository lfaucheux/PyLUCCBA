# -*- coding: utf8 -*-
from __future__ import print_function
from PyLUCCBA.examples import studies_constant_settings as cs
import PyLUCCBA as cc


scenarizer = lambda name : cc.CBACalculator(
    run_name               = 'Grassland-Cropland_DR=0_CP=%s'%name,
    project_horizon        = 20,
    T_so                   = 20,
    T_vg_diff              = 1,
    T_vg_unif              = 20,
    discount_rate          = .0,
    co2_prices_scenario    = name,
    initial_landuse        = 'improved grassland',
    final_landuse          = 'wheat',
    input_flows_scenario   = 'CRISTANOL',
    **cs.other_parameters
)

co2_prices_scenarios = ['O', 'A', 'B', 'C', 'SPC']

objects = {}
for s_name in co2_prices_scenarios:    
    cba = scenarizer(s_name)
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
