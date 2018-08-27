# -*- coding: utf8 -*-
from __future__ import print_function
from PyLUCCBA.examples import studies_constant_settings as cs
import PyLUCCBA as cc


objects = {}
cba = cc.CBACalculator(
    run_name               = 'Example-1',
    project_horizon        = 20,
    T_so                   = 20,
    T_vg_diff              = 1,
    T_vg_unif              = 20,
    discount_rate          = .03,
    co2_prices_scenario    = 'SPC',
    initial_landuse        = ['FORESTLAND30','improved grassland','annual cropland','degraded grassland'][1],
    final_landuse          = ['wheat','miscanthus'][0],
    input_flows_scenario   = ['IFP','DOE'][0],
    **cs.other_parameters
)
##cba = cc.CBAParametersEndogenizer(cba).endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj
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
    dico['object'].all_XLSXed
