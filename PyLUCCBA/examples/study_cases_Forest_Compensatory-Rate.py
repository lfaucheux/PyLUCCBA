# -*- coding: utf8 -*-

__authors__ = [
    "Marion Dupoux <marion.dupoux@u-paris10.fr>",
    "Laurent Faucheux <faucheux@centre-cired.fr>"
]

import constant_settings as cs
import PyLUCCBA as cc


scenarizer = lambda name : cc.CBACalculator(
    run_name               = 'Forest-Cropland_CP=%s'%name,
    project_horizon        = 20,
    T_so                   = 20,
    T_vg_diff              = 1,
    T_vg_unif              = 20,
    discount_rate          = .0,
    co2_prices_scenario    = name,
    initial_landuse        = 'FORESTLAND30',
    final_landuse          = 'wheat',
    input_flows_scenario   = 'CRISTANOL',
    **cs.other_parameters
)

co2_prices_scenarios = [
    'WEO2015-CPS',
    'WEO2015-NPS',
    'WEO2015-450S',
    'SPC'
]

objects = {}
for s_name in co2_prices_scenarios:    
    cba = scenarizer(s_name)
    cba = cc.CBAParametersEndogenizer(cba).ENDOGENOUS_discount_rate_which_equates_NPV_TOTAL_uniform_co2_flows_TO_NPV_TOTAL_differentiated_co2_flows
    cba.all_XLSXed
    objects[cba.run_name] = {'summary':cba.summary_args,'object':cba}



print u"""
*******************************************************************************
            ╔═╗┬ ┬┌┬┐┌┬┐┌─┐┬─┐┬┌─┐┌─┐                                         *
            ╚═╗│ │││││││├─┤├┬┘│├┤ └─┐                                         *
            ╚═╝└─┘┴ ┴┴ ┴┴ ┴┴└─┴└─┘└─┘                                         *
*******************************************************************************"""
for run_name, dico in objects.items():
    print dico['summary']