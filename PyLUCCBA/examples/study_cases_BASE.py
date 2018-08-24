# -*- coding: utf8 -*-
from __future__ import print_function
from PyLUCCBA.examples import studies_constant_settings as cs
import PyLUCCBA as cc


objects = {}
cba = cc.CBACalculator(
    run_name               = 'Grassland-Cropland_DR=0.03_CP=C_TH=XX',
    project_horizon        = 20,
    T_so                   = 20,
    T_vg_diff              = 1,
    T_vg_unif              = 20,
    discount_rate          = .03,
    co2_prices_scenario    = 'SPC',
    initial_landuse        = ['FORESTLAND30','improved grassland','annual cropland','degraded grassland'][2],
    final_landuse          = ['wheat','miscanthus'][1],
    input_flows_scenario   = ['CRISTANOL','DOE'][1],
    **cs.other_parameters
)
##cba = cc.CBAParametersEndogenizer(cba).ENDOGENOUS_disc_rate_which_equates_NPV_total_unif_co2_flows_TO_NPV_total_diff_co2_flows  
cba.all_XLSXed
cba.all_charts
objects[cba.run_name] = {'summary':cba.summary_args,'object':cba}

print(u"""
*******************************************************************************
            ╔═╗┬ ┬┌┬┐┌┬┐┌─┐┬─┐┬┌─┐┌─┐                                         *
            ╚═╗│ │││││││├─┤├┬┘│├┤ └─┐                                         *
            ╚═╝└─┘┴ ┴┴ ┴┴ ┴┴└─┴└─┘└─┘                                         *
*******************************************************************************""")
for run_name, dico in objects.items():
    print(dico['summary'])
