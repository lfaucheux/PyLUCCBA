# -*- coding: utf8 -*-
from __future__ import print_function
from PyLUCCBA.examples import studies_constant_settings as cs
import PyLUCCBA as cc


scenarizer = lambda name : cc.CBACalculator(
    run_name               = 'Grassland-Cropland_CP=%s'%name,
    project_horizon        = 20,
    T_so                   = 20,
    T_vg_diff              = 1,
    T_vg_unif              = 20,
    discount_rate          = .0,
    co2_prices_scenario    = name,
    initial_landuse        = 'improved grassland',
    final_landuse          = 'wheat',
    input_flows_scenario   = 'IFP',
    **cs.other_parameters
)

co2_prices_scenarios = [
    'WEO2018-CPS',
    'WEO2018-NPS',
    'WEO2018-SDS',
    'SPC2019',
    'OECD2018',
]

objects = {}
for s_name in co2_prices_scenarios:    
    cba = scenarizer(s_name)
    cba = cc.CBAParametersEndogenizer(cba).endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj
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
