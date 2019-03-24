# -*- coding: utf8 -*-
from __future__ import print_function, absolute_import

__pyLUCCBA__ =\
u"""
*****************************************************************************************************                                                                                                  *
*          ___       __   __  _______________  ___                                  * ╦╔═╗╔═╗┌─┐┌┐┌ *
*         / _ \__ __/ /  / / / / ___/ ___/ _ )/ _ |                                 * ║╠╣ ╠═╝├┤ │││ *
*        / ___/ // / /__/ /_/ / /__/ /__/ _  / __ |                                 * ╩╚  ╩  └─┘┘└┘ *
*       /_/   \_, /____/\____/\___/\___/____/_/ |_|                                 *****************
*            /___/                                                                                  *
*                                                                                                   *
* Conceived by Marion Dupoux                                                                        *
* Institut Français du Pétrole et des Énergies Nouvelles (IFPEN)                                    *
* marion.dupoux@gu.se                                                                               *
*****************************************************************************************************
* Coded by Laurent Faucheux                                                         * ╔═╗╦╦═╗╔═╗╔╦╗ *
* Centre International de Recherche sur l'Environnement et le Développement (CIRED) * ║  ║╠╦╝║╣  ║║ *
* laurent.faucheux@hotmail.fr                                                       * ╚═╝╩╩╚═╚═╝═╩╝ *
*****************************************************************************************************
"""

__authors__ = [
    "Marion Dupoux <marion.dupoux@gu.se>",
    "Laurent Faucheux <laurent.faucheux@hotmail.fr>"
]
__all__ = [
    '__authors__',
    '__pyLUCCBA__',
    'BlackOutputAndSubstitutesSpecificities',
    'CBACalculator',
    'CBAParametersEndogenizer',
    'CarbonAndCo2FlowsAnnualizer',
    'Co2Prices',
    'folder_copier',
    'GlobalWarmingPotential',
    'InputFlows',
    'LandSurfaceFlows',
    'OutputFlows',
    'VGCAndSOCDeltas',
    'VegetationsAndSoilSpecificities',
]

import os
import copy
import pprint as pp
import warnings;warnings.filterwarnings('ignore')
import numpy as np;np.seterr(divide='ignore', invalid='ignore')
if __name__ == '__main__':
    import tools as ts
else:
    from . import tools as ts

VERBOSE        = True
VERBOSE_SOLVER = True
VERBOSE_DTESTS = False

##******************************************
##    ╔╗ ┬  ┌─┐┌─┐┬┌─╔═╗┬ ┬┌┬┐┌─┐┬ ┬┌┬┐╔═╗┌┐┌┌┬┐╔═╗┬ ┬┌┐ ┌─┐┌┬┐┬┌┬┐┬ ┬┌┬┐┌─┐┌─┐╔═╗┌─┐┌─┐┌─┐┬┌─┐┬┌─┐┬┌┬┐┬┌─┐┌─┐
##    ╠╩╗│  ├─┤│  ├┴┐║ ║│ │ │ ├─┘│ │ │ ╠═╣│││ ││╚═╗│ │├┴┐└─┐ │ │ │ │ │ │ ├┤ └─┐╚═╗├─┘├┤ │  │├┤ ││  │ │ │├┤ └─┐
##    ╚═╝┴─┘┴ ┴└─┘┴ ┴╚═╝└─┘ ┴ ┴  └─┘ ┴ ╩ ╩┘└┘─┴┘╚═╝└─┘└─┘└─┘ ┴ ┴ ┴ └─┘ ┴ └─┘└─┘╚═╝┴  └─┘└─┘┴└  ┴└─┘┴ ┴ ┴└─┘└─┘
class BlackOutputAndSubstitutesSpecificities(object):
    """ Class object representing specificities of fuel and of its
    substitues."""
    
    @property
    def tonne_to_MJs(self):
        """ Megajoules (MJs) per tonne of final product."""
        return {
            'ETH': 26708.86076,
            'OIL': 45513.51351,
        }

    def tonnes_to_MJs_computer(self, key, val_in_tonnes):
        """ Method which computes the conversion from tonnes to megajoules
        (based on self.tonne_to_MJs)."""
        return val_in_tonnes*self.tonne_to_MJs[key]

    def MJs_to_tonnes_computer(self, key, val_in_MJs):
        """ Method which computes the conversion from megajoules to tonnes
        (based on self.tonne_to_MJs)."""
        return val_in_MJs/self.tonne_to_MJs[key]

    @property
    def co2eq_emissions_per_MJ(self):
        """ Co2equivalent tonnes per MJ of final product. In an economic point
        of view, note the sign, negative. An emission is seen as a social cost.
        """
        return {
            'ETH': '[!!!] CO2eq DEDUCED FROM CBA RESULTS [!!!]',
            'OIL': -87.3*1.e-6,
        }


##******************************************
##    ╦  ╦┌─┐┌─┐┌─┐┌┬┐┌─┐┌┬┐┬┌─┐┌┐┌┌─┐╔═╗┌┐┌┌┬┐╔═╗┌─┐┬┬  ╔═╗┌─┐┌─┐┌─┐┬┌─┐┬┌─┐┬┌┬┐┬┌─┐┌─┐
##    ╚╗╔╝├┤ │ ┬├┤  │ ├─┤ │ ││ ││││└─┐╠═╣│││ ││╚═╗│ │││  ╚═╗├─┘├┤ │  │├┤ ││  │ │ │├┤ └─┐
##     ╚╝ └─┘└─┘└─┘ ┴ ┴ ┴ ┴ ┴└─┘┘└┘└─┘╩ ╩┘└┘─┴┘╚═╝└─┘┴┴─┘╚═╝┴  └─┘└─┘┴└  ┴└─┘┴ ┴ ┴└─┘└─┘
class VegetationsAndSoilSpecificities(ts.Cache):
    """ Class object representing specificities of vegetations (VEG) and soil (SO)."""

    def __init__(self, **kwargs):
        super(VegetationsAndSoilSpecificities, self).__init__(
            verbose=kwargs.pop('verbose', VERBOSE), **kwargs
        )
        self.resources = ts.DataReader(**kwargs).resources['dluc']

    @property
    def delay_between_luc_and_production(self):
        """ Index of the year at which first ghg emissions occur. """
        return {
            'MISCANTHUS' : 1,
            'SWITCHGRASS': 1,
            'WHEAT'      : 1,
            'CORN'       : 1,
            'SUGARBEET'  : 1,

            'DEBUG'      : 1,
        }
    @property
    def biomass_share_translating_in_ghg_flow(self):
        """ Share of biomass which translates in ghg flow.
        Recalling that flow can be either emissions (positive)
        or sequestration (negative).
        """
        return  {
            'ANNUAL CROPLAND'               :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'DEGRADED GRASSLAND'            :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'FORESTLAND30'                  :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'FORESTPLANTATIONS>20YRS'       :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'FORESTPLANTATIONS>20YRS'       :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'IMPROVED GRASSLAND'            :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'MISCANTHUS'                    :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'PERENNIAL CROPLAND'            :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'SWITCHGRASS'                   :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'SUGARBEET'                     :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'WHEAT'                         :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'WHEATSTRAW'                    :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'WOODR'                         :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},
            'WOODRESIDUES'                  :{'vg':{'emi':.9, 'seq':1.}, 'so':{'emi':.3, 'seq':.3}},

            'DEBUG'                         :{'vg':{'emi':1., 'seq':1.}, 'so':{'emi':1., 'seq':1.}},
        }

    @property
    def ghgs_emissions_per_tonne_of_eth(self):
        """ GHGs tonnes per tonne of ethanol, related to a given production
        phase. In an economic point of view, note the sign, which is negative.
        I.e. an emission is seen as a social cost.
        """
        return {
            'process':{
                'CORN'            :{'CO2':-0.901518987, 'N2O':-0          , 'CH4':-0.0024},
                'CORNSTOVER'      :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'CORNSTRAW'       :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'MISCANTHUS'      :{'CO2':-0.20566    , 'N2O':-0          , 'CH4':-0},
                'POPLAR'          :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'RAPESEEDSTRAW'   :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'SUGARBEET'       :{'CO2':-0.95644    , 'N2O':-0          , 'CH4':-0.00267},
                'SUNFLOWERSTRAW'  :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'SWITCHGRASS'     :{'CO2':-0.400632911, 'N2O':-0          , 'CH4':-0},
                'TRITICALE'       :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'TRITICALESTRAW'  :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'WHEAT'           :{'CO2':-0.82958    , 'N2O':-0          , 'CH4':-0.0024},
                'ANNUAL CROPLAND' :{'CO2':-0.82958    , 'N2O':-0          , 'CH4':-0.0024},
                'WHEATSTRAW'      :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'WILLOW'          :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'WOODR'           :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},
                'WOODRESIDUES'    :{'CO2':-0.5        , 'N2O':-0          , 'CH4':-0},

                'DEBUG'           :{'CO2':-1.         , 'N2O':-0          , 'CH4':-0},
            },
            'culture':{
                'CORN'            :{'CO2':-0.827974684, 'N2O':-0.000576938, 'CH4':-0},
                'CORNSTOVER'      :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'CORNSTRAW'       :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'MISCANTHUS'      :{'CO2':-0.04006    , 'N2O':-0.00027    , 'CH4':-0},
                'POPLAR'          :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'RAPESEEDSTRAW'   :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'SUGARBEET'       :{'CO2':-0.19204    , 'N2O':-0.0008     , 'CH4':-0.00027},
                'SUNFLOWERSTRAW'  :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'SWITCHGRASS'     :{'CO2':-0.34721519 , 'N2O':-0.000185647, 'CH4':-0},
                'TRITICALE'       :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'TRITICALESTRAW'  :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'WHEAT'           :{'CO2':-0.46313    , 'N2O':-0.00187    , 'CH4':-0.0008},
                'WHEATSTRAW'      :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'WILLOW'          :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'WOODR'           :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},
                'WOODRESIDUES'    :{'CO2':-0.05       , 'N2O':-0          , 'CH4':-0},

                'DEBUG'           :{'CO2':-1.         , 'N2O':-0          , 'CH4':-0},
            },
        }

    @ts.Cache._property
    def carbon_stock_specificities(self):
        """ Carbon stocks specificities.

        Example
        -------
        >>> o = VegetationsAndSoilSpecificities(
        ...     country = 'france',
        ...     verbose = False,
        ... )
        >>> soc_spec = o.carbon_stock_specificities['soc']
        >>> soc_spec['infos']
        {'unit': 'Tonne/ha'}
        >>> soc_spec['values']['DEBUG']
        51.33333333
        """
        return ts.InMindWithCorrespondingUnit(
            u"", self.resources['CS_yields']
        ).values_and_infos_per_key
    
    @ts.Cache._property
    def soil_carbon_stock_specificities(self):
        """ Carbon stocks specificities of soil """
        return self.carbon_stock_specificities['soc']
    
    @property
    def vegetation_carbon_stock_specificities(self):
        """ Carbon stocks specificities of vegetation """
        return self.carbon_stock_specificities['cveg']


##******************************************
##    ╔═╗┬  ┌─┐┌┐ ┌─┐┬  ╦ ╦┌─┐┬─┐┌┬┐┬┌┐┌┌─┐╔═╗┌─┐┌┬┐┌─┐┌┐┌┌┬┐┬┌─┐┬  
##    ║ ╦│  │ │├┴┐├─┤│  ║║║├─┤├┬┘││││││││ ┬╠═╝│ │ │ ├┤ │││ │ │├─┤│  
##    ╚═╝┴─┘└─┘└─┘┴ ┴┴─┘╚╩╝┴ ┴┴└─┴ ┴┴┘└┘└─┘╩  └─┘ ┴ └─┘┘└┘ ┴ ┴┴ ┴┴─┘
class GlobalWarmingPotential(ts.Cache):
    """
    References
    ----------
    .. [1] Solomon S., D. Qin, M. Manning, Z. Chen, M. Marquis, K.B. Averyt, M. Tignor, H.L. Miller (2007)
        "Climate Change 2007: The Physical Science Basis. Contribution of Working Group I to the Fourth Assessment
        Report of the Intergovernmental Panel on Climate Change".
        Cambridge University Press 2007, Chapter 2, Section 2.10.2, Table 2.14, pp 211-213.
    .. [2] Annie Levasseur, Pascal Lesage, Manuele Margni, Louise Deschênes, Réjean Samson (2010)
        "Considering Time in LCA: Dynamic LCA and Its Application to Global Warming Impact Assessments".
        Environmental Science & Technology, 2010, 44 (8), pp 3169–3174.
    """
    def __init__(self,
            first_year=2020, project_horizon=20, GWP_horizon=None, static=True,
            **kwargs
        ):
        super(GlobalWarmingPotential, self).__init__(
            verbose=kwargs.pop('verbose', VERBOSE), **kwargs
        )
        self.first_year       = first_year
        self.project_horizon  = project_horizon
        self.last_year        = first_year + self.project_horizon
        self.GWP_horizon      = float(GWP_horizon) if GWP_horizon\
                                else float(self.project_horizon)
        self.other_ghgs       = ['N2O', 'CH4']
        self.static           = static
        # --------------------#
        self.biomass_ghgs_specificities = VegetationsAndSoilSpecificities()\
                                          .ghgs_emissions_per_tonne_of_eth

    @ts.Cache._property
    def ghgs_specificities(self):
        """ Greenhouse gases (computed) specificities.

        Example
        -------
        >>> o = GlobalWarmingPotential(
        ...     GWP_horizon=20,
        ...     first_year=2017,
        ...     verbose=False
        ... )
        >>> o.ghgs_specificities['CH4']['trajectories']['GWP'][2017]
        72.22098319799206
        >>> o.ghgs_specificities['N2O']['trajectories']['GWP'][2017]
        292.3363728242806
        >>> o.ghgs_specificities['CO2']['trajectories']['GWP'][2017]
        1.0

        Note that results, once computed are cached. Thus, for a different set
        of parameters, one has to play with another instance of
        `GlobalWarmingPotential`. Let's call it `o2`.
        >>> o2 = GlobalWarmingPotential(
        ...     GWP_horizon=20,
        ...     first_year=2017,
        ...     static=False,
        ...     verbose=False
        ... )
        >>> o2.ghgs_specificities['CO2']['trajectories']['GWP'][2017]
        1.0
        >>> o2.ghgs_specificities['CO2']['trajectories']['GWP'][2018]
        0.9576408083306349
        """
            
        _ck = {
            'CO2': {
                'a'           :{0:0.217, 1:0.259, 2:0.338, 3:0.186},
                'tau'         :{1:172.9, 2:18.51, 3:1.186},
                'GWP100'      :1.,
                'AGWP100'     :8.69e-14,
                'trajectories':{'AGWP':{},'GWP':{}},
            },
            'N2O': {
                'tau'         :{'i':114.},
                'GWP100'      :298.,
                'trajectories':{'AGWP':{},'GWP':{}},
            },
            'CH4': {
                'tau'         :{'i':12.},
                'GWP100'      :25.,
                'trajectories':{'AGWP':{},'GWP':{}},
            },
        }

        _ph = self.project_horizon
        _st = self.static
        _gh = self.GWP_horizon

        # < AGWPs >
        for ghg in self.other_ghgs:
            _ck[ghg]['AGWP100'] = _ck['CO2']['AGWP100']*_ck[ghg]['GWP100']

        _ck['CO2']['integral100'] = _ck['CO2']['a'][0]*(1e2-1) + sum([
            _ck['CO2']['a'][i]*_ck['CO2']['tau'][i]*(
                1 - np.exp(-1e2/_ck['CO2']['tau'][i])
            ) for i in range(1, 3+1)
        ])
        # < INTEGRALS >
        for ghg in self.other_ghgs:
            _ck[ghg]['integral100'] = _ck[ghg]['tau']['i']*(
                1 - np.exp(-1e2/_ck[ghg]['tau']['i'])
            )
        # < ais >
        for ghg in _ck.keys():
            _ck[ghg]['ai100'] = _ck[ghg]['AGWP100']/_ck[ghg]['integral100']

        # < AGWPi(t) (W/m2/kg) >
        for _t_ in range(0, _ph)[:(1 if _st else None)]:
            year = self.first_year + _t_
            _ck['CO2']['trajectories']['AGWP'][year] = _ck['CO2']['ai100']*(
                _ck['CO2']['a'][0]*(_gh - _t_ - 1) + sum([
                    _ck['CO2']['a'][i]*_ck['CO2']['tau'][i]*(
                        1 - np.exp((_t_ - _gh)/_ck['CO2']['tau'][i])
                    ) for i in range(1, 3+1)
                ])
            )
            for ghg in self.other_ghgs:
                _ck[ghg]['trajectories']['AGWP'][year]\
                  = _ck[ghg]['ai100']*_ck[ghg]['tau']['i']*(
                    1 - np.exp(((_t_ - _gh)/_ck[ghg]['tau']['i']))
                )
            for ghg in _ck.keys():
                _ck[ghg]['trajectories']['GWP'][year]\
                  = _ck[ghg]['trajectories']['AGWP'][year]\
                  /_ck['CO2']['trajectories']['AGWP'][self.first_year]
                
        if self.verbose and not self._cache.get('endogenizing', False):
            print(50*"~", 'ghgs_specificities')
            for ghg in _ck.keys():
                _r_ = _ck[ghg]['trajectories']
                print(
                    'AGWP%s_%s_traj'%(
                        int(_gh), ghg
                    ), ts.dict_time_serie_as_row_array(_r_['AGWP'])
                )
                print(
                    'GWP%s_%s_traj'%(
                        int(_gh), ghg
                    ), ts.dict_time_serie_as_row_array(_r_['GWP'])
                )
                
        return _ck

    def co2eq_yields_GWP_traj_computer(self, ghgs_yield):
        """
        Method which computes the total quantity of CO2eq associated with each
        GHG emission tonne per tonne of ethanol.
        Cf "ghgs_emissions_per_tonne_of_eth"
          NB : if `self.static` is `True`, conversions coefficients from tonne of
          GHG to co2eq tonnes are not time-variables, but simply based on the
          first year conversion factors.

        Example
        -------
        >>> o = GlobalWarmingPotential(
        ...     GWP_horizon=20,
        ...     first_year=2017,
        ...     verbose=False
        ... )
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':1., 'N2O':.0, 'CH4':.0})[2017]
        1.0
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':2., 'N2O':.0, 'CH4':.0})[2017]
        2.0
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':.0, 'N2O':1., 'CH4':.0})[2017]
        292.3363728242806
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':.0, 'N2O':.0, 'CH4':1.})[2017]
        72.22098319799206
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':.0, 'N2O':1., 'CH4':1.})[2017]
        364.55735602227264
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':1., 'N2O':1., 'CH4':1.})[2017]
        365.55735602227264
        
        >>> o = GlobalWarmingPotential(
        ...     GWP_horizon=50,
        ...     first_year=2019,
        ...     verbose=False
        ... )
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':.0, 'N2O':1., 'CH4':.0})[2019]
        308.6772331491366
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':.0, 'N2O':.0, 'CH4':1.})[2019]
        41.94663086333451
        >>> o.co2eq_yields_GWP_traj_computer({'CO2':.0, 'N2O':1., 'CH4':1.})[2019]
        350.62386401247113
        """
        _c_ = {}
        _y0 = self.first_year
        _gs = self.ghgs_specificities
        _st = self.static
        for _t_ in range(0, self.project_horizon):
            # < GWPi(t) (kgCO2eq/kgi) & CO2eq(t) >
            year      = _y0 + _t_
            _c_[year] = 0
            _y_       = _y0 if _st else year
            for ghg in self.ghgs_specificities.keys():
                _c_[year] += _gs[ghg]['trajectories']['GWP'][_y_]*ghgs_yield[ghg]
        return _c_

##******************************************
##    ╦  ╦╔═╗╔═╗╔═╗┌┐┌┌┬┐╔═╗╔═╗╔═╗╔╦╗┌─┐┬ ┌┬┐┌─┐┌─┐
##    ╚╗╔╝║ ╦║  ╠═╣│││ ││╚═╗║ ║║   ║║├┤ │  │ ├─┤└─┐
##     ╚╝ ╚═╝╚═╝╩ ╩┘└┘─┴┘╚═╝╚═╝╚═╝═╩╝└─┘┴─┘┴ ┴ ┴└─┘
class VGCAndSOCDeltas(ts.Cache):

    def __init__(self, initial_landuse, final_landuse, **kwargs):
        super(VGCAndSOCDeltas, self).__init__(**kwargs)
        self.vegetations_and_so_specificities = VegetationsAndSoilSpecificities(**kwargs)
        self.initial_landuse                  = initial_landuse.upper()
        self.final_landuse                    = final_landuse.upper()

    @ts.Cache._property
    def vegetation_carbon_stock_infos(self):
        """ Vegetation carbon stocks infos.

        Example
        -------
        >>> o = VGCAndSOCDeltas(
        ...     country         = 'france',
        ...     initial_landuse = 'FORESTLAND30',
        ...     final_landuse   = 'wheat',
        ...     verbose         = False
        ... )
        >>> o.vegetation_carbon_stock_infos
        {'unit': 'Tonne/ha'}

        """
        return self.vegetations_and_so_specificities\
        .vegetation_carbon_stock_specificities['infos']
    
    @ts.Cache._property
    def soil_carbon_stock_infos(self):
        """ Soil carbon stocks infos.

        Example
        -------
        >>> o = VGCAndSOCDeltas(
        ...     country         = 'france',
        ...     initial_landuse = 'FORESTLAND30',
        ...     final_landuse   = 'none',
        ...     verbose         = False
        ... )

        Note the value set for `final_landuse`. This is set so simply to
        show that the value is actually not involved within the present example.
        
        >>> o.soil_carbon_stock_infos
        {'unit': 'Tonne/ha'}
        """
        return self.vegetations_and_so_specificities\
        .soil_carbon_stock_specificities['infos']

    @ts.Cache._property
    def initial_vg_carbon_stock_value(self):
        """ Carbon stocks numerical values of the specified initial landuse
        related to vegetation.

        Example
        -------
        >>> base_kwargs = {
        ...     'country'      : 'france',
        ...     'final_landuse': 'none',
        ...     'verbose'      : False,
        ... }

        Note the value set for `final_landuse`. This is set so simply to
        show that the value is actually not involved within the present example.

        >>> VGCAndSOCDeltas(
        ...     initial_landuse = 'FORESTLAND30',
        ...     **base_kwargs
        ... ).initial_vg_carbon_stock_value
        84.0

        >>> VGCAndSOCDeltas(
        ...     initial_landuse = 'improved grassland',
        ...     **base_kwargs
        ... ).initial_vg_carbon_stock_value
        5.566666667
        """
        return float(
            self.vegetations_and_so_specificities\
            .vegetation_carbon_stock_specificities['values'][self.initial_landuse]
        )
    
    @ts.Cache._property
    def initial_so_carbon_stock_value(self):
        """ Carbon stocks numerical values of the specified initial landuse
        related to soil.

        Example
        -------
        >>> base_kwargs = {
        ...     'country'      : 'france',
        ...     'final_landuse': 'none',
        ...     'verbose'      : False,
        ... }

        Note the value set for `final_landuse`. This is set so simply to
        show that the value is actually not involved within the present example.

        >>> VGCAndSOCDeltas(
        ...     initial_landuse = 'FORESTLAND30',
        ...     **base_kwargs
        ... ).initial_so_carbon_stock_value
        71.33333333

        >>> VGCAndSOCDeltas(
        ...     initial_landuse = 'improved grassland',
        ...     **base_kwargs
        ... ).initial_so_carbon_stock_value
        90.2652
        """
        return float(
            self.vegetations_and_so_specificities\
            .soil_carbon_stock_specificities['values'][self.initial_landuse]
        )
    
    @ts.Cache._property
    def final_vg_carbon_stock_value(self):
        """ Carbon stocks numerical values of the specified final landuse
        related to vegetation."""
        return float(
            self.vegetations_and_so_specificities\
            .vegetation_carbon_stock_specificities['values'][self.final_landuse]
        )
    
    @ts.Cache._property
    def final_so_carbon_stock_value(self):
        """ Carbon stocks numerical values of the specified final landuse
        related to soil."""
        return float(
            self.vegetations_and_so_specificities\
            .soil_carbon_stock_specificities['values'][self.final_landuse]
        )
    
    @ts.Cache._property
    def absolute_VGC_differential(self):
        """ Absolute vegetation carbon stock differential between final and
        initial landuse related to vegetation."""
        return self.final_vg_carbon_stock_value\
               - self.initial_vg_carbon_stock_value
    
    @ts.Cache._property
    def absolute_SOC_differential(self):
        """ Absolute vegetation carbon stock differential between final and
        initial landuse related to soil."""
        return self.final_so_carbon_stock_value\
               - self.initial_so_carbon_stock_value

##******************************************
##    ╔═╗┌─┐┬─┐┌┐ ┌─┐┌┐┌╔═╗┌┐┌┌┬┐╔═╗┌─┐┌─┐╔═╗┬  ┌─┐┬ ┬┌─┐╔═╗┌┐┌┌┐┌┬ ┬┌─┐┬  ┬┌─┐┌─┐┬─┐
##    ║  ├─┤├┬┘├┴┐│ ││││╠═╣│││ ││║  │ │┌─┘╠╣ │  │ ││││└─┐╠═╣│││││││ │├─┤│  │┌─┘├┤ ├┬┘
##    ╚═╝┴ ┴┴└─└─┘└─┘┘└┘╩ ╩┘└┘─┴┘╚═╝└─┘└─┘╚  ┴─┘└─┘└┴┘└─┘╩ ╩┘└┘┘└┘└─┘┴ ┴┴─┘┴└─┘└─┘┴└─
class CarbonAndCo2FlowsAnnualizer(ts.Cache):
    def __init__(self,
            delta_soc, delta_vgc, project_horizon, final_landuse,
            T_so=None, T_vg_diff=None, T_vg_unif=None,
            **kwargs
        ):
        super(CarbonAndCo2FlowsAnnualizer, self).__init__(**kwargs)
        self.delta_soc       = delta_soc
        self.delta_vgc       = delta_vgc
        self.project_horizon = float(project_horizon)
        self.final_landuse   = final_landuse.upper()
        self.vg_and_so_spec  = VegetationsAndSoilSpecificities(
            verbose=kwargs.pop('verbose', VERBOSE)
        )
        self.T_so_diff       = T_so or self.project_horizon
        self.T_vg_diff       = T_vg_diff or self.project_horizon
        self.T_so_unif       = T_so or self.project_horizon
        self.T_vg_unif       = T_vg_unif or self.project_horizon
        self.Delay_so_diff   = 0
        self.Delay_vg_diff   = 0
        self.Delay_so_unif   = 0
        self.Delay_vg_unif   = 0

    @ts.Cache._property
    def T_so_years_after_LUC(self):
        """ Instrumental row-vector consisting of t expononents used for calcu-
        lation of the soil flows profile. Only concerned if the differentiated
        computation case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 10,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.
        
        >>> o.T_so_years_after_LUC
        array([[ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10.]])
        """
        return np.arange(0., self.T_so_diff+1)[None, :]

    @ts.Cache._property
    def T_vg_years_after_LUC(self):
        """ Instrumental row-vector consisting of t expononents used for calcu-
        lation of the vegetation flows profile. Only concerned if the differen-
        tiated computation case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 5,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.
        
        >>> o.T_vg_years_after_LUC
        array([[0., 1., 2., 3., 4., 5.]])
        """
        return np.arange(0., self.T_vg_diff+1)[None, :]

    """**[SOC-SPECIFIC]****************************************************************************"""

    @ts.Cache._property
    def so_emitting(self):
        """ Boolean specifying whether carbon is emitted (True) or sequestered
        (False). Returns `None` if the delta is null."""
        return None if self.delta_soc == 0 else self.delta_soc < 0
    
    @ts.Cache._property
    def soc_unit_unif_flows_traj(self):
        """ Soil carbon flows per HA of land in the uniform annualization case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 5,
        ...     T_so            = 2,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> o.soc_unit_unif_flows_traj
        array([[-3.29789641, -3.29789641,  0.        ,  0.        ,  0.        ]])
        """
        _D_ = self.Delay_so_unif if self.so_emitting else 0
        return ts.redim_row_array(
            np.hstack((
                np.zeros((1, _D_)),
                self.delta_soc*np.ones((1, int(self.T_so_unif))) / self.T_so_unif
            )),
            self.T_so_unif,
            self.project_horizon
        )[:, :(-_D_ if _D_ else None)]

    def soc_POEPLAU_et_al_eq7_p2418(self, _a_):
        """ C.Poeplau et al equation which computes the stock evolution of carbon
        emissions as a function of time t, i.e. as a solution of a differential
        equation.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 6,
        ...     T_so            = 6,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> o.soc_POEPLAU_et_al_eq7_p2418(.5)
        array([[-0.        , -5.70314932, -6.47498665, -6.57944347, -6.59358017,
                -6.59549336, -6.59575228]])
                
        >>> o.soc_POEPLAU_et_al_eq7_p2418(.75)
        array([[-0.        , -4.8571607 , -6.13749436, -6.47498665, -6.56394865,
                -6.58739878, -6.59358017]])
        """
        return self.delta_soc*(1. - np.exp(-self.T_so_years_after_LUC/_a_) )

    def soc_DUPOUX(self, _a_):
        """ Dupoux equation which computes the stock evolution of carbon
        sequestrations as a function of time t.
        """
        return self.delta_soc*( 1.- np.exp(-self.T_so_years_after_LUC/_a_) )

    @property
    def soc_chosen_CRF(self):
        """ Carbon response function (CRF) which is chosen to describe the
        evolution of the stock.
          `self.soc_POEPLAU_et_al_eq7_p2418` in the emission case
          `self.soc_DUPOUX`                  in the sequestration case
        """
        return self.soc_POEPLAU_et_al_eq7_p2418 if self.so_emitting else\
               self.soc_DUPOUX

    @ts.Cache._property
    def soc_chosen_CRF_constrained(self):
        """ Chosen CRF constrained such that _a_ must equate (i) to (ii)
          (i)  the soil carbon stock variation due the LUC : `self.delta_soc`.
          (ii) the sum of annually emitted flows."""
        return lambda _a_ : -self.delta_soc + np.sum(
            self.soc_chosen_CRF(_a_)[:, 1:] - self.soc_chosen_CRF(_a_)[:, :-1]
        )

    @ts.Cache._property
    def a_parameter_which_solves_soc_chosen_CRF_constrained(self):
        """ Parameter a which sastifies the chosen soil CRF constraint.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 3,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> a = o.a_parameter_which_solves_soc_chosen_CRF_constrained
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.07902303]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> a
        0.07902303425105699
        >>> o.soc_POEPLAU_et_al_eq7_p2418(a)
        array([[-0.        , -6.59577175, -6.59579281, -6.59579281]])
        """
        return ts.solver_ND(
            VERBOSE_SOLVER,
            'a_parameter_which_solves_soc_chosen_CRF_constrained',
            self.soc_chosen_CRF_constrained,
            [1.],
            bforce=True
        )[0]

    @ts.Cache._property
    def soc_unit_stock_traj(self):
        """ Evolution trajectory of the soil carbon stock.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 3,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> a = 0.0795301617017074
        >>> o.soc_chosen_CRF(a)
        array([[-0.        , -6.59576998, -6.59579281, -6.59579281]])
        >>> o.soc_unit_stock_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.07902303]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-0.        , -6.59577175, -6.59579281, -6.59579281]])
        """
        return self.soc_chosen_CRF(
            self.a_parameter_which_solves_soc_chosen_CRF_constrained
        )

    @ts.Cache._property
    def soc_unit_diff_flows_traj(self):
        """ Soil carbon flows per HA of land in the differentiated
        annualization case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = 'none',
        ...     final_landuse   = 'none',
        ...     project_horizon = 3,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> o.soc_unit_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.07902303]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-6.59577175e+00, -2.10605417e-05, -6.72475409e-11]])
        """
        _D_ = self.Delay_so_diff if self.so_emitting else 0
        return ts.redim_row_array(
            np.hstack((
                np.zeros((1, _D_)),
                self.soc_unit_stock_traj[:, 1:]\
                - self.soc_unit_stock_traj[:, :-1]
            )),
            self.T_so_diff,
            self.project_horizon
        )[:, :(-_D_ if _D_ else None)]

    """**[VGC-SPECIFIC]****************************************************************************"""
    @ts.Cache._property
    def vg_emitting(self):
        """ Boolean specifying whether carbon is emitted (True) or sequestered
        (False). Returns `None` if the delta is null."""
        return None if self.delta_vgc == 0 else self.delta_vgc < 0

    @ts.Cache._property
    def vgc_unit_unif_flows_traj(self):
        """ Vegetation carbon flows per HA of land in the uniform annualization
        case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 3,
        ... )

        Note the value set for `delta_soc`. This is set so simply to show
        that it is actually not involved within the present example.
        
        >>> o.vgc_unit_unif_flows_traj
        array([[-28., -28., -28.]])
        """
        _D_ = self.Delay_vg_unif if self.vg_emitting else 0
        return ts.redim_row_array(
            np.hstack((
                np.zeros((1, _D_)),
                self.delta_vgc*np.ones((1, int(self.T_vg_unif)))/self.T_vg_unif
            )),
            self.T_vg_unif,
            self.project_horizon
        )[:, :(-_D_ if _D_ else None)]

    def vgc_POEPLAU_et_al_eq7_p2418(self,_a_):
        """ C.Poeplau et al equation which computes the stock evolution of carbon
        emissions as a function of time t, i.e. as a solution of a differential
        equation.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 6,
        ...     T_vg_diff       = 3,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.
        
        >>> o.vgc_POEPLAU_et_al_eq7_p2418(.5)
        array([[ -0.        , -72.63183621, -82.46148633, -83.79178482]])
        >>> o.vgc_POEPLAU_et_al_eq7_p2418(.25)
        array([[ -0.        , -82.46148633, -83.97182114, -83.99948389]])
        """
        return self.delta_vgc*( 1. - np.exp(-self.T_vg_years_after_LUC/_a_) )
    
    def vgc_DUPOUX(self,_a_):
        """ Dupoux equation which computes the stock evolution of carbon
        sequestrations as a function of time t.
        """
        return self.delta_vgc*( 1. - np.exp(-self.T_vg_years_after_LUC/_a_) )
    
    @property
    def vgc_chosen_CRF(self):
        """ Carbon response function (CRF) which is chosen to describe the
        evolution of the stock.
          `self.soc_POEPLAU_et_al_eq7_p2418` in the emission case
          `self.soc_DUPOUX`                  in the sequestration case."""
        return self.vgc_POEPLAU_et_al_eq7_p2418 if self.vg_emitting else\
               self.vgc_DUPOUX

    @ts.Cache._property
    def vgc_chosen_CRF_constrained(self):
        """ Chosen CRF constrained such that _a_ must equate (i) to (ii)
          (i)  the soil carbon stock variation due the LUC : `self.delta_vgc`
          (ii) the sum of annually emitted flows."""
        return lambda _a_ : -self.delta_vgc + np.sum(
            self.vgc_chosen_CRF(_a_)[:, 1:] - self.vgc_chosen_CRF(_a_)[:, :-1]
        )

    @ts.Cache._property
    def a_parameter_which_solves_vgc_chosen_CRF_constrained(self):
        """ Parameter a which sastifies the chosen vegetation CRF constraint.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 3,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> a = o.a_parameter_which_solves_vgc_chosen_CRF_constrained
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.07953016]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> a
        0.0795301617017074
        >>> o.vgc_POEPLAU_et_al_eq7_p2418(a)
        array([[ -0.        , -83.99970924, -84.        , -84.        ]])
        
        """
        return ts.solver_ND(
            VERBOSE_SOLVER,
            'a_parameter_which_solves_vgc_chosen_CRF_constrained',
            self.vgc_chosen_CRF_constrained,
            [1.],
            bforce=True
        )[0]

    @ts.Cache._property
    def vgc_unit_stock_traj(self):
        """ Evolution trajectory of the vegetation carbon stock.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 3,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> a = 0.0795301617017074
        >>> o.vgc_chosen_CRF(a)
        array([[ -0.        , -83.99970924, -84.        , -84.        ]])
        >>> o.vgc_unit_stock_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.07953016]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[ -0.        , -83.99970924, -84.        , -84.        ]])
        """
        return self.vgc_chosen_CRF(
            self.a_parameter_which_solves_vgc_chosen_CRF_constrained
        )

    @ts.Cache._property
    def vgc_unit_diff_flows_traj(self):
        """ Vegetation carbon flows per HA of land in the differentiated
        annualization case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = 'none',
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 2,
        ... )

        Note the values of parameters set to `'none'`. This is set so simply to
        show that those are actually not involved within the present example.

        >>> o.vgc_unit_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04725381]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-8.39999999e+01, -5.41505898e-08]])
        """
        _D_ = self.Delay_vg_diff if self.vg_emitting else 0
        return ts.redim_row_array(
            np.hstack((
                np.zeros((1, _D_)),
                self.vgc_unit_stock_traj[:, 1:]\
                - self.vgc_unit_stock_traj[:, :-1]
            )),
            self.T_vg_diff,
            self.project_horizon
        )[:, :(-_D_ if _D_ else None)]

    """**[VGC+SOC]*********************************************************************************"""
    @ts.Cache._property
    def unit_unif_carbon_flows_traj(self):
        """ Total (so+vg) carbon flows per HA of land in the uniform
        annualization case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 2,
        ... )

        Note the value set for `final_landuse`. This is set so simply to show
        that the value is actually not involved within the present example.
        
        >>> o.unit_unif_carbon_flows_traj
        array([[-45.29789641, -45.29789641]])
        """
        return 1.*self.soc_unit_unif_flows_traj\
               + 1.*self.vgc_unit_unif_flows_traj

    @ts.Cache._property
    def unit_diff_carbon_flows_traj(self):
        """ Total (so+vg) carbon flows per HA of land in the differentiated
        annualization case.

        Example
        -------
        >>> o = CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'none',
        ...     project_horizon = 2,
        ... )

        Note the value set for `final_landuse`. This is set so simply to show
        that the value is actually not involved within the present example.
        
        >>> o.unit_diff_carbon_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05214615]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04725381]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-9.05957927e+01, -8.51145954e-08]])
        """
        return 1.*self.soc_unit_diff_flows_traj\
               + 1.*self.vgc_unit_diff_flows_traj

    """**[VGC+TO*VGCO2][SOC*TO*VGCO2]***************************************************************"""
    def vg_and_so_co2_unit_x_flows_trajecter(self, key, traj):
        return traj*self.vg_and_so_spec.biomass_share_translating_in_ghg_flow[
            self.final_landuse
        ][key][
            'emi' if getattr(self, '%s_emitting'%key) else 'seq'
        ]*(44./12.)
        
    @ts.Cache._property
    def vgco2_unit_unif_flows_traj(self):
        """ Vegetation CO2 flows per HA of land in the uniform annualization
        case.

        Example
        -------
        >>> base_kwargs = {
        ...     'delta_soc'      : 'none',
        ...     'delta_vgc'      : -84,
        ...     'final_landuse'  : 'miscanthus',
        ...     'project_horizon': 6,
        ... }

        Note the value set for `delta_soc`. This is set so simply to show
        that the value is actually not involved within the present example.

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_vg_unif = 2,
        ...     **base_kwargs
        ... ).vgco2_unit_unif_flows_traj
        array([[-138.6, -138.6,    0. ,    0. ,    0. ,    0. ]])

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_vg_unif = 4,
        ...     **base_kwargs
        ... ).vgco2_unit_unif_flows_traj
        array([[-69.3, -69.3, -69.3, -69.3,   0. ,   0. ]])
        """
        return self.vg_and_so_co2_unit_x_flows_trajecter(
            'vg', self.vgc_unit_unif_flows_traj
        )

    @ts.Cache._property
    def vgco2_unit_diff_flows_traj(self):
        """ Vegetation CO2 flows per HA of land in the differentiated
        annualization case.

        Example
        -------
        >>> base_kwargs = {
        ...     'delta_soc'      : 'none',
        ...     'delta_vgc'      : -84,
        ...     'final_landuse'  : 'miscanthus',
        ...     'project_horizon': 6,
        ... }

        Note the value set for `delta_soc`. This is set so simply to show
        that the value is actually not involved within the present example.

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_vg_diff = 2,
        ...     **base_kwargs
        ... ).vgco2_unit_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04725381]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-2.77200000e+02, -1.78696946e-07,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_vg_diff = 4,
        ...     **base_kwargs
        ... ).vgco2_unit_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.10617162]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-2.77177494e+02, -2.25041722e-02, -1.82712438e-06,
                -1.48378376e-10,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.vg_and_so_co2_unit_x_flows_trajecter(
            'vg', self.vgc_unit_diff_flows_traj
        )
    
    @ts.Cache._property
    def soco2_unit_unif_flows_traj(self):
        """ Soil CO2 flows per HA of land in the uniform annualization
        case.

        Example
        -------
        >>> base_kwargs = {
        ...     'delta_soc'      : -6.595792810000006,
        ...     'delta_vgc'      : 'none',
        ...     'final_landuse'  : 'miscanthus',
        ...     'project_horizon': 6,
        ... }

        Note the value set for `delta_vgc`. This is set so simply to show
        that the value is actually not involved within the present example.

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_so = 2,
        ...     **base_kwargs
        ... ).soco2_unit_unif_flows_traj
        array([[-3.62768605, -3.62768605,  0.        ,  0.        ,  0.        ,
                 0.        ]])

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_so = 4,
        ...     **base_kwargs
        ... ).soco2_unit_unif_flows_traj
        array([[-1.81384302, -1.81384302, -1.81384302, -1.81384302,  0.        ,
                 0.        ]])
        """
        return self.vg_and_so_co2_unit_x_flows_trajecter(
            'so', self.soc_unit_unif_flows_traj
        )

    @ts.Cache._property
    def soco2_unit_diff_flows_traj(self):
        """ Soil CO2 flows per HA of land in the differentiated annualization
        case.

        Example
        -------
        >>> base_kwargs = {
        ...     'delta_soc'      : -6.595792810000006,
        ...     'delta_vgc'      : 'none',
        ...     'final_landuse'  : 'miscanthus',
        ...     'project_horizon': 6,
        ... }

        Note the value set for `delta_vgc`. This is set so simply to show
        that the value is actually not involved within the present example.

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_so = 2,
        ...     **base_kwargs
        ... ).soco2_unit_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05214615]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-7.25537206e+00, -3.40604061e-08,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])

        >>> CarbonAndCo2FlowsAnnualizer(
        ...     T_so = 4,
        ...     **base_kwargs
        ... ).soco2_unit_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.11195753]
        ---- [***]The solution converged.[1.776357e-15][***]
        array([[-7.25441366e+00, -9.58300932e-04, -1.26590613e-07,
                -1.67232450e-11,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.vg_and_so_co2_unit_x_flows_trajecter(
            'so', self.soc_unit_diff_flows_traj
        )

    """**[VGCO2+SOCO2]*****************************************************************************"""
    @ts.Cache._property
    def unit_unif_co2_flows_traj(self):
        """ Total (so+vg) CO2 flows per HA of land in the uniform annualization
        case.

        Example
        -------
        >>> CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'wheat',
        ...     T_vg_unif       = 10,
        ...     project_horizon = 12,
        ... ).unit_unif_co2_flows_traj
        array([[-28.32461434, -28.32461434, -28.32461434, -28.32461434,
                -28.32461434, -28.32461434, -28.32461434, -28.32461434,
                -28.32461434, -28.32461434,  -0.60461434,  -0.60461434]])
        """
        return 1.*self.soco2_unit_unif_flows_traj\
               + 1.*self.vgco2_unit_unif_flows_traj

    @ts.Cache._property
    def unit_diff_co2_flows_traj(self):
        """ Total (so+vg) CO2 flows per HA of land in the differentiated
        annualization case.

        Example
        -------
        >>> CarbonAndCo2FlowsAnnualizer(
        ...     delta_soc       = -6.595792810000006,
        ...     delta_vgc       = -84,
        ...     final_landuse   = 'wheat',
        ...     T_vg_diff       = 3,
        ...     project_horizon = 12,
        ... ).unit_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.31576933]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.07953016]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-2.84148705e+02, -2.93785903e-01, -1.23383411e-02,
                -5.19879939e-04, -2.19053131e-05, -9.22987605e-07,
                -3.88903874e-08, -1.63865916e-09, -6.90453028e-11,
                -2.90949487e-12, -1.22124533e-13, -5.86197757e-15]])
        """
        return 1.*self.soco2_unit_diff_flows_traj\
               + 1.*self.vgco2_unit_diff_flows_traj



##******************************************
##    ╔═╗┬ ┬┌┬┐┌─┐┬ ┬┌┬┐╔═╗┬  ┌─┐┬ ┬┌─┐
##    ║ ║│ │ │ ├─┘│ │ │ ╠╣ │  │ ││││└─┐
##    ╚═╝└─┘ ┴ ┴  └─┘ ┴ ╚  ┴─┘└─┘└┴┘└─┘
class OutputFlows(ts.Cache):

    def __init__(self,
            first_year, project_horizon, output='ETH', 
            scenario='none', repeated_pattern_polation=False, **kwargs
        ):
        super(OutputFlows, self).__init__(**kwargs)
        self.resources = ts.DataReader(**kwargs).resources['yields']['Output']
        self.output = output.upper()
        self.first_year = first_year
        self.project_horizon = project_horizon - 1
        self.last_year = first_year + self.project_horizon
        self.output_flows_scenario = scenario
        self.repeated_pattern_polation = repeated_pattern_polation

    @ts.Cache._property
    def output_flows_traj_and_infos(self):
        r""" All scenarized trajectories of annual tonnes of output flows among
        which the wanted one is chosen. To add an other selectable scenario,
        edit the following files:
          <output>_yields_<country>.csv
          <output>_yields_<country>.txt or Output.txt
        Originally both in ./resources/yields/Output.

        Example
        -------
        >>> o = OutputFlows(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.
        
        >>> os.path.relpath(
        ...     o.output_flows_traj_and_infos.fname
        ... )
        'resources\\yields\\Output\\ETH_yields_FR.csv'
        """
        return ts.InMindWithCorrespondingUnit(
            'year', self.resources['%s_yields'%self.output], pop=False
        )

    @ts.Cache._property
    def eligible_scenarios(self):
        """ Scenario that can be chosen for simulations.

        Example
        -------
        >>> o = OutputFlows(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.
        
        >>> o.eligible_scenarios
        ['DEBUG', 'O']
        """
        return [s for s in sorted(
            self.output_flows_traj_and_infos\
            .keys_and_values[self.first_year].keys()
        )  if s != 'year']

    @ts.Cache._property
    def scenarized_output_flows_traj_sparse_traj(self):
        """ Chosen scenario of annual output flows, whose trajectory is still
        sparse.

        Example
        -------
        >>> o = OutputFlows(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = 20,
        ...     scenario        = 'O',
        ... )        
        >>> o.scenarized_output_flows_traj_sparse_traj[2025]
        1
        """
        return {
            year : dic[self.output_flows_scenario] for year, dic
            in self.output_flows_traj_and_infos.keys_and_values.items()
        }

    @ts.Cache._property
    def scenarized_output_flows_traj_full_traj_as_dict(self):
        """ Chosen scenario of annual output flows, whose trajectory is now
        completed.

        Example
        -------
        >>> o = OutputFlows(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = 20,
        ...     scenario        = 'O',
        ... )
        >>> o.scenarized_output_flows_traj_full_traj_as_dict[2025]
        1.0
        """
        return {
            year : price for year, price
            in ts.poler(
                self.scenarized_output_flows_traj_sparse_traj,
                self.repeated_pattern_polation,
                yT = self.last_year + 10
            ).items() if self.first_year<=year<=self.last_year
        }

    @ts.Cache._property
    def scenarized_output_flows_traj_full_traj(self):
        """ Chosen scenario of annual output flows, whose trajectory is now
        in array format (needed for matrix-like calculations).

        Example
        -------
        >>> o = OutputFlows(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = 20,
        ...     scenario        = 'O',
        ... )
        >>> o.scenarized_output_flows_traj_full_traj
        array([[1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
                1., 1., 1., 1.]])
        """
        return ts.dict_time_serie_as_row_array(
            self.scenarized_output_flows_traj_full_traj_as_dict
        )
    
    @ts.Cache._property
    def scenarized_output_infos(self):
        """ Informations (unit, year, etc...) about output scenarii.

        Example
        -------
        >>> o = OutputFlows(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ...     scenario        = 'O',
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.
        
        >>> sorted(o.scenarized_output_infos.items())
        [('unit', 'tonne[Output]/tonne[Output]'), ('yrb', 2007)]
        """
        return self.output_flows_traj_and_infos\
               .keys_and_infos[self.output_flows_scenario.lower()]



##******************************************
##    ╦┌┐┌┌─┐┬ ┬┌┬┐╔═╗┬  ┌─┐┬ ┬┌─┐
##    ║│││├─┘│ │ │ ╠╣ │  │ ││││└─┐
##    ╩┘└┘┴  └─┘ ┴ ╚  ┴─┘└─┘└┴┘└─┘
class InputFlows(ts.Cache):

    def __init__(self,
            final_landuse, first_year, project_horizon,
            scenario='none', repeated_pattern_polation=False, **kwargs
        ):
        super(InputFlows, self).__init__(**kwargs)
        self.resources = ts.DataReader(**kwargs).resources['yields']['Input']
        self.final_landuse = final_landuse.upper()
        self.input_flows_scenario = scenario.upper()
        self.repeated_pattern_polation = repeated_pattern_polation
        self.first_year = first_year
        self.project_horizon = project_horizon-1
        self.last_year = first_year+self.project_horizon

    @ts.Cache._property
    def eligible_scenarios(self):
        """ Scenario that can be chosen for simulations.

        Example
        -------
        >>> o = InputFlows(
        ...     country         = 'frANcE',
        ...     final_landuse   = 'miscanthus',
        ...     project_horizon = float('nan'),
        ...     first_year      = 2030,
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.

        >>> o.eligible_scenarios
        ['DEBUG', 'DOE']

        Scenarios depend on the value set for `final_landuse`.
        >>> o = InputFlows(
        ...     country         = 'frANcE',
        ...     final_landuse   = 'wheat',
        ...     project_horizon = float('nan'),
        ...     first_year      = 2030,
        ... )
        >>> o.eligible_scenarios
        ['DEBUG', 'IFP']
        """
        return [s for s in sorted(
            self.input_flows_traj_and_infos\
            .keys_and_values[self.first_year].keys()
        )  if s != 'year']

    @ts.Cache._property
    def input_flows_traj_and_infos(self):
        r""" All scenarized trajectories of annual input flows [1/tonne or tonne]
        (times or per tonne of output) among which the wanted one is chosen.
        To add an other selectable scenario, edit the following files:
          <input>_yields_<country>.csv
          <input>_yields_<country>.txt or Input.txt
        Originally both in ./resources/yields/Input.

        Example
        -------
        >>> o = InputFlows(
        ...     country         = 'frANcE',
        ...     final_landuse   = 'miscanthus',
        ...     project_horizon = float('nan'),
        ...     first_year      = float('nan'),
        ... )

        Note the value set for `project_horizon` and `first_year`. This is set
        so simply to show that, if required for instantiation, the value is not
        involved within the present example.
        
        >>> os.path.relpath(
        ...     o.input_flows_traj_and_infos.fname
        ... )
        'resources\\yields\\Input\\MISCANTHUS_yields_FR.csv'
        
        Let's figure out what the possible scenrii are when
        `final_landuse = 'miscanthus'`.
        >> o.eligible_scenarios
        ['DEBUG', 'DOE']

        Note that values associated to each scenario for the year
        2030 are empty strings (i.e. `''`). Those will be automatically
        retro/intra/extra-polated from existing values. Actually, the only
        existing value for the scenario named DOE is that of 2013, which
        implies that the only possible "polation" is about generating a
        time-constant yield.        
        >>> o.input_flows_traj_and_infos.keys_and_values[2012]['DOE']
        0.31847714
        
        >>> o = InputFlows(
        ...     country         = 'frANcE',
        ...     final_landuse   = 'wheat',
        ...     project_horizon = float('nan'),
        ...     first_year      = float('nan'),
        ... )
        >>> os.path.relpath(
        ...     o.input_flows_traj_and_infos.fname
        ... )
        'resources\\yields\\Input\\WHEAT_yields_FR.csv'

        Let's figure out what the possible scenrii are when
        `final_landuse = 'wheat'`.
        >> o.eligible_scenarios
        ['IFP', 'DEBUG']

        Note that the parameter used to set the scenario is named `scenario`.
        However, for testing purpose, we may have reasons for checking which
        one is set. The attribute to call to do so is named
        `input_flows_scenario`.
        >>> InputFlows(
        ...     country         = 'frANcE',
        ...     final_landuse   = 'wheat',
        ...     project_horizon = float('nan'),
        ...     first_year      = float('nan'),
        ...     scenario        = 'IFP'
        ... ).input_flows_scenario
        'IFP'
        """
        return ts.InMindWithCorrespondingUnit(
            'year', self.resources['%s_yields'%self.final_landuse], pop=False
        )

    @ts.Cache._property
    def scenarized_unit_input_flows_traj_sparse_traj(self):
        """ Chosen scenario of annual unitary input flows, whose trajectory
        is still sparse.

        Example
        -------
        >>> o = InputFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     scenario        = 'DOE',
        ...     first_year      = 2030,
        ...     project_horizon = 5,
        ... )

        Note that the set of values from which the "polation" is performed will
        likely not be of the same size as that involved by `project_horizon`.
        >>> len(o.scenarized_unit_input_flows_traj_sparse_traj)
        60
        
        """
        return {
            year : dic[self.input_flows_scenario] for year, dic
            in self.input_flows_traj_and_infos.keys_and_values.items()
        }
    
    @ts.Cache._property
    def scenarized_unit_input_flows_traj_full_traj_as_dict(self):
        """ Chosen scenario of annual unitary input flows, whose trajectory is
         now completed.

        Example
        -------
        >>> o = InputFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     scenario        = 'DOE',
        ...     first_year      = 2020,
        ...     project_horizon = 5,
        ... )

        The "polated" values that are ultimately considered for calculations
        are those involved by `project_horizon`.
        >>> sorted(
        ...     o.scenarized_unit_input_flows_traj_full_traj_as_dict.items()
        ... )
        [(2020, 0.31847714), (2021, 0.31847714), (2022, 0.31847714), (2023, 0.31847714), (2024, 0.31847714)]

        """
        return {
            year : price for year, price in ts.poler(
                self.scenarized_unit_input_flows_traj_sparse_traj,
                self.repeated_pattern_polation,
                yT = self.last_year + 10
            ).items() if self.first_year<=year<=self.last_year
        }
    
    @ts.Cache._property
    def scenarized_unit_input_flows_traj_full_traj(self):
        """ Chosen scenario of annual unitary input flows, whose trajectory is
        now in array format (needed for matrix-like calculations).

        Example
        -------
        >>> o = InputFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     scenario        = 'DOE',
        ...     first_year      = 2020,
        ...     project_horizon = 5,
        ... )
        >>> o.scenarized_unit_input_flows_traj_full_traj
        array([[0.31847714, 0.31847714, 0.31847714, 0.31847714, 0.31847714]])
        """
        return ts.dict_time_serie_as_row_array(
            self.scenarized_unit_input_flows_traj_full_traj_as_dict
        )

    @ts.Cache._property
    def scenarized_unit_input_infos(self):
        """ Informations (unit, year, etc...) about unitary input scenarii.

        Example
        -------
        >>> o = InputFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     scenario        = 'DOE',
        ...     first_year      = float('nan'),
        ...     project_horizon = float('nan'),
        ... )

        Note the value set for `project_horizon` and `first_year`. This is set
        so simply to show that, if required for instantiation, the value is not
        involved within the present example.

        >>> sorted(
        ...     o.scenarized_unit_input_infos.keys()
        ... )
        ['power', 'unit', 'yrb']
        >>> o.scenarized_unit_input_infos['unit']
        'tonne[Output]/tonne[Input]'
        >>> o.scenarized_unit_input_infos['power']
        -1.0

        The value associated with the key `'power'` is not manually filled.
        It is deduced from `'unit'`, depending on whether `'tonne[Output]'`
        is in the numerator or in the denominator.
        
        >>> o.scenarized_unit_input_infos['yrb']
        2012

        The `'yrb'` key (stands for "year-base") shown above could be, say,
        used to scenarize any temporal trajectory of technological progress.
        """
        _info_ = self.input_flows_traj_and_infos\
                 .keys_and_infos[self.input_flows_scenario.lower()]
        _info_['power'] = 1. if 'Output' in _info_['unit'].split('/')[1]\
                          else -1.
        return _info_


##******************************************
##    ╦  ┌─┐┌┐┌┌┬┐╔═╗┬ ┬┬─┐┌─┐┌─┐┌─┐┌─┐╔═╗┬  ┌─┐┬ ┬┌─┐
##    ║  ├─┤│││ ││╚═╗│ │├┬┘├┤ ├─┤│  ├┤ ╠╣ │  │ ││││└─┐
##    ╩═╝┴ ┴┘└┘─┴┘╚═╝└─┘┴└─└  ┴ ┴└─┘└─┘╚  ┴─┘└─┘└┴┘└─┘
class LandSurfaceFlows(ts.Cache):

    def __init__(self,
            final_landuse, first_year, project_horizon,
            output='eth', repeated_pattern_polation=False, **kwargs
        ):
        super(LandSurfaceFlows, self).__init__(**kwargs)
        self.resources = ts.DataReader(**kwargs).resources['yields']['Input']
        self.output = output
        self.land_input = ('ha%s'%output).upper()
        self.final_landuse = final_landuse.upper()
        self.repeated_pattern_polation = repeated_pattern_polation
        self.first_year = first_year
        self.project_horizon = project_horizon-1
        self.last_year = first_year+self.project_horizon

    @ts.Cache._property
    def land_surface_flows_traj_and_infos(self):
        r""" All scenarized trajectories of annual land surfaces [1/HA or HA]
        (times or per tonne of output) among which the wanted one is chosen.
        To add an other selectable scenario, edit the following files:
          HA<output>_yields_<country>.csv
          HA<output>_yields_<country>.txt
        Originally both in ./resources/yields/Input.

        Example
        -------
        >>> o = LandSurfaceFlows(
        ...     country         = 'FRancE',
        ...     final_landuse   = 'miscanthus',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.
        
        >>> os.path.relpath(
        ...     o.land_surface_flows_traj_and_infos.fname
        ... )
        'resources\\yields\\Input\\HAETH_yields_FR.csv'
        """
        return ts.InMindWithCorrespondingUnit(
            'year', self.resources['%s_yields'%self.land_input], pop=False
        )

    @ts.Cache._property
    def eligible_scenarios(self):
        """ Scenario that can be chosen for simulations.

        Example
        -------
        >>> o = LandSurfaceFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'none',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.
        
        >>> o.eligible_scenarios
        ['DEBUG', 'MISCANTHUS', 'SUGARBEET', 'WHEAT', 'WHEATSTRAW', 'WOODRESIDUES']

        As it reads above, names of eligible LandSurface-scenarios consist of
        all possible values that can be set for `final_landuse`. Indeed, the
        "flows" of lands that will be implied in simulations directly depend on
        those that are involved by this parameter.
        """
        return [s for s in sorted(
            self.land_surface_flows_traj_and_infos\
            .keys_and_values[self.first_year].keys()
        )  if s != 'year']

    @ts.Cache._property
    def scenarized_unit_land_surface_flows_traj_sparse_traj(self):
        """ Chosen scenario of annual unitary land surfaces, whose trajectory
        is still sparse.

        Example
        -------
        >>> o = LandSurfaceFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     first_year      = 2020,
        ...     project_horizon = 20,
        ... )

        Actually, the only existing value from which the "polation" will be
        performed in the present case, is that of 2007. The only possible
        "polation" will about generating a time-constant yield.  
        
        >>> o.scenarized_unit_land_surface_flows_traj_sparse_traj[2006]
        ''
        >>> o.scenarized_unit_land_surface_flows_traj_sparse_traj[2007]
        5.254872818

        Note that unitary land surface "flows" depend on the value set for
        `final_landuse`. See
        >>> o = LandSurfaceFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'wheat',
        ...     first_year      = 2020,
        ...     project_horizon = 20,
        ... )
        >>> o.scenarized_unit_land_surface_flows_traj_sparse_traj[2007]
        2.576086957

        Here again, the only existing value from which the "polation" will be
        performed is that of 2007. We know that since we have filled-up the
        files from which those values are red. We can also figure this out by
        calling the entire dictionary, doing
        >> o.scenarized_unit_land_surface_flows_traj_sparse_traj
        ......, 2060: '', 2061: '', ...... , 2006: '', 2007: 2.576086957, 2008: '', ...... , 2047: ''}

        NB: Remember that in python, dictionaries are unordered objects.
        """
        return {
            year : dic[self.final_landuse] for year, dic
            in self.land_surface_flows_traj_and_infos.keys_and_values.items()
        }

    @ts.Cache._property
    def scenarized_unit_land_surface_flows_traj_full_traj_as_dict(self):
        """ Chosen scenario of annual unitary land surfaces, whose trajectory
        is now completed.

        Example
        -------
        >>> o = LandSurfaceFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     scenario        = 'DOE',
        ...     first_year      = 2020,
        ...     project_horizon = 5,
        ... )

        The "polated" values that are ultimately considered for calculations
        are those involved by `project_horizon`.
        >>> sorted(
        ...     o.scenarized_unit_land_surface_flows_traj_full_traj_as_dict.items()
        ... )
        [(2020, 5.254872818), (2021, 5.254872818), (2022, 5.254872818), (2023, 5.254872818), (2024, 5.254872818)]

        """
        return {
            year : price for year, price
            in ts.poler(
                self.scenarized_unit_land_surface_flows_traj_sparse_traj,
                self.repeated_pattern_polation,
                yT = self.last_year + 10
            ).items() if self.first_year<=year<=self.last_year
        }

    @ts.Cache._property
    def scenarized_unit_land_surface_flows_traj_full_traj(self):
        """ Chosen scenario of annual unitary land surfaces, whose trajectory
        is now in array format (needed for matrix-like calculations).

        Example
        -------
        >>> o = LandSurfaceFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     first_year      = 2020,
        ...     project_horizon = 5,
        ... )
        >>> o.scenarized_unit_land_surface_flows_traj_full_traj
        array([[5.25487282, 5.25487282, 5.25487282, 5.25487282, 5.25487282]])
        """
        return ts.dict_time_serie_as_row_array(
            self.scenarized_unit_land_surface_flows_traj_full_traj_as_dict
        )

    @ts.Cache._property
    def scenarized_unit_land_surface_infos(self):
        """ Informations (unit, year, etc...) about unitary land scenarii.

        Example
        -------
        >>> o = LandSurfaceFlows(
        ...     country         = 'FraNCE',
        ...     final_landuse   = 'miscanthus',
        ...     first_year      = float('nan'),
        ...     project_horizon = float('nan'),
        ...     scenario        = 'DOE',
        ... )

        Note the value set for `project_horizon` and `first_year`. This is set
        so simply to show that, if required for instantiation, the value is not
        involved within the present example.
    
        >>> sorted(
        ...     o.scenarized_unit_land_surface_infos.keys()
        ... )
        ['power', 'unit']
        >>> o.scenarized_unit_land_surface_infos['unit']
        'Tonne[Output]/ha'
        
        >>> o.scenarized_unit_land_surface_infos['power']
        -1.0

        The value associated with the key `'power'` is not manually filled.
        It is deduced from `'unit'`, depending on whether `'Tonne[Output]'`
        is in the numerator or in the denominator.
        """
        _infos_ = self.land_surface_flows_traj_and_infos.keys_and_infos
        _info_  = _infos_[self.final_landuse.lower()]\
                  if self.final_landuse.lower() in _infos_ else _infos_['*']
        _info_['power'] = 1. if 'Output' in _info_['unit'].split('/')[1]\
                          else -1.
        return _info_


##******************************************
##    ╔═╗┌─┐┌─┐╔═╗┬─┐┬┌─┐┌─┐┌─┐
##    ║  │ │┌─┘╠═╝├┬┘││  ├┤ └─┐
##    ╚═╝└─┘└─┘╩  ┴└─┴└─┘└─┘└─┘
class Co2Prices(ts.Cache):
    def __init__(self,
            first_year, project_horizon, scenario,
            repeated_pattern_polation=False, final_currency='EUR', **kwargs
        ):
        super(Co2Prices, self).__init__(**kwargs)
        self.repeated_pattern_polation = repeated_pattern_polation
        self.co2_prices_scenario = scenario
        self.project_horizon = project_horizon
        self.final_currency = final_currency.upper()
        self.first_year = first_year
        self.last_year = first_year + project_horizon
        self.resources = ts.DataReader(**kwargs).resources['prices']['Exput']

    @ts.Cache._property
    def co2_prices_and_infos(self):
        r""" All scenarized trajectories of CO2 prices per tonne among which the
        wanted one is chosen. To add an other selectable scenario, edit the
        following files:
          <exput>_prices_<country>.csv
          <exput>_prices_<country>.txt or Exput.txt
        Originally both in ./resources/prices/Exput.

        Example
        -------
        >>> o = Co2Prices(
        ...     country         = 'france',
        ...     first_year      = float('nan'),
        ...     project_horizon = float('nan'),
        ...     scenario        = 'none',
        ... )

        Note the value set for `scenario`, `project_horizon` and `first_year`.
        This is set so simply to show that, if required for instantiation, the
        value is not involved within the present example.
        
        >>> os.path.relpath(
        ...     o.co2_prices_and_infos.fname
        ... )
        'resources\\prices\\Exput\\CO2_prices_FR.csv'
        """
        return ts.InMindWithCorrespondingUnit(
            'year', self.resources['CO2_prices'], pop=False
        )

    @ts.Cache._property
    def eligible_scenarios(self):
        """ Scenario that can be chosen for simulations.

        Example
        -------
        >>> o = Co2Prices(
        ...     country         = 'france',
        ...     scenario        = 'none',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ... )

        Note the value set for `scenario` and `project_horizon`. This is so
        to show that, if required for instantiation, those values are not
        involved within the present example.

        >>> for eligible_scenario in o.eligible_scenarios:
        ...     print(eligible_scenario)
        A
        B
        C
        DEBUG
        O
        OECD2018
        SPC2009
        SPC2019
        WEO2015-450S
        WEO2015-CPS
        WEO2015-NPS
        WEO2018-CPS
        WEO2018-NPS
        WEO2018-SDS
        """
        return [s for s in sorted(
            self.co2_prices_and_infos\
            .keys_and_values[self.first_year].keys()
        )  if s != 'year']

    @ts.Cache._property
    def scenarized_co2_prices_sparse_traj(self):
        """ Chosen scenario of CO2 prices per tonne, whose trajectory is still.
        sparse.

        Example
        -------
        >>> o = Co2Prices(
        ...     country         = 'FraNCE',
        ...     scenario        = 'WEO2015-450S',
        ...     first_year      = 2020,
        ...     project_horizon = 20,
        ... )

        The values from which the "polation" will be performed are that of 2020,
        2030 and 2040.
        
        >>> o.scenarized_co2_prices_sparse_traj[2020]
        22
        >>> o.scenarized_co2_prices_sparse_traj[2030]
        100
        >>> o.scenarized_co2_prices_sparse_traj[2040]
        140

        We figured this out since we have filled-up the file from which those
        values are red. We can also figure this out by calling the entire
        dictionary, doing
        >> o.scenarized_co2_prices_sparse_traj
        ......, 2030: 100, 2061: '', ...... , 2006: '', 2020: 22, 2008: '', ...... , 2040: 140}

        NB: Remember that in python, dictionaries are unordered objects.

        In the present example, note that before 2020, the 2020-to-2030
        annualized rate is used. After 2040, it is that of 2030-to-2040.
        """
        return {
            year : dic[self.co2_prices_scenario] for year, dic
            in self.co2_prices_and_infos.keys_and_values.items()
        }

    @ts.Cache._property
    def scenarized_co2_prices_full_traj_as_dict(self):
        """ Chosen scenario of CO2 prices per tonne, whose trajectory is now
        completed.

        Example
        -------
        >>> o = Co2Prices(
        ...     country         = 'FraNCE',
        ...     scenario        = 'WEO2015-450S',
        ...     first_year      = 2019,
        ...     project_horizon = 21,
        ... )
        >>> pp.pprint(sorted(
        ...     o.scenarized_co2_prices_full_traj_as_dict.items()
        ... ))
        [(2020, 21.99999999999998),
         (2021, 25.59648984414618),
         (2022, 29.78092237915814),
         (2023, 34.64941260124672),
         (2024, 40.31378807970197),
         (2025, 46.90415759823428),
         (2026, 54.57189970961075),
         (2027, 63.4931398496735),
         (2028, 73.8727958788692),
         (2029, 85.94928497600733),
         (2030, 100.0),
         (2031, 103.42196941293808),
         (2032, 106.96103757250695),
         (2033, 110.62121156199927),
         (2034, 114.40663558587235),
         (2035, 118.32159566199236),
         (2036, 122.37052447444594),
         (2037, 126.5580063924133),
         (2038, 130.88878266078584),
         (2039, 135.36775676840486),
         (2040, 140.0)]

        Everything went as expected. Remember that exogenously, we want
        >>> o.scenarized_co2_prices_sparse_traj[2020]
        22
        >>> o.scenarized_co2_prices_sparse_traj[2030]
        100
        >>> o.scenarized_co2_prices_sparse_traj[2040]
        140

        Remember that on open year-intervals, neighbor intrapolated rates
        are reused for retro- and extra-polation.        
        """
        return {
            year : price for year, price
            in ts.poler(
                self.scenarized_co2_prices_sparse_traj,
                self.repeated_pattern_polation,
                yT = self.last_year + 10
            ).items() if self.first_year<year<=self.last_year
        }

    @ts.Cache._property
    def scenarized_co2_prices_full_traj(self):
        """ Chosen scenario of CO2 prices per tonne, whose trajectory is now in
        array format (needed for matrix-like calculations).

        Example
        -------
        >>> o = Co2Prices(
        ...     country         = 'FraNCE',
        ...     scenario        = 'WEO2015-450S',
        ...     first_year      = 2019,
        ...     project_horizon = 21,
        ... )
        >>> o.scenarized_co2_prices_full_traj
        array([[ 22.        ,  25.59648984,  29.78092238,  34.6494126 ,
                 40.31378808,  46.9041576 ,  54.57189971,  63.49313985,
                 73.87279588,  85.94928498, 100.        , 103.42196941,
                106.96103757, 110.62121156, 114.40663559, 118.32159566,
                122.37052447, 126.55800639, 130.88878266, 135.36775677,
                140.        ]])
                
        >>> o = Co2Prices(
        ...     country         = 'FraNCE',
        ...     scenario        = 'WEO2015-CPS',
        ...     first_year      = 2019,
        ...     project_horizon = 21,
        ... )
        >>> o.scenarized_co2_prices_full_traj
        array([[20.        , 20.82759488, 21.68943542, 22.58693871, 23.52158045,
                24.49489743, 25.50849001, 26.5640248 , 27.66323734, 28.80793502,
                30.        , 30.87558027, 31.77671523, 32.70415073, 33.65865436,
                34.64101615, 35.65204916, 36.69259019, 37.76350045, 38.86566631,
                40.        ]])
                
        >>> o = Co2Prices(
        ...     country         = 'FraNCE',
        ...     scenario        = 'WEO2015-NPS',
        ...     first_year      = 2019,
        ...     project_horizon = 21,
        ... )
        >>> o.scenarized_co2_prices_full_traj
        array([[22.        , 23.17397772, 24.41060198, 25.71321575, 27.08534041,
                28.53068524, 30.05315746, 31.65687279, 33.34616659, 35.12560553,
                37.        , 38.13103136, 39.29663655, 40.49787244, 41.73582822,
                43.01162634, 44.32642358, 45.68141209, 47.07782046, 48.51691481,
                50.        ]])
        """
        return ts.dict_time_serie_as_row_array(
            self.scenarized_co2_prices_full_traj_as_dict
        )

    @ts.Cache._property
    def scenarized_co2_infos(self):
        """ Informations (currency, year, etc...) about CO2 prices/tonne scenarii.

        Example
        -------
        >>> o = Co2Prices(
        ...     country         = 'FraNCE',
        ...     first_year      = 2020,
        ...     project_horizon = float('nan'),
        ...     scenario        = 'O',
        ... )

        Note the value set for `project_horizon`. This is set so simply to
        show that, if required for instantiation, the value is actually not
        involved within the present example.
        
        >>> sorted(o.scenarized_co2_infos.items())
        [('toConvert', False), ('unit', 'EUR/tonne'), ('yrb', 'none')]
        
        The value associated with the key `'toConvert'` is not manually filled.
        It is deduced depending on whether the value set for `final_currency`
        is that that is mentioned in `'unit'`.
        """
        _infos_ = self.co2_prices_and_infos.keys_and_infos[
            self.co2_prices_scenario.lower()
        ]
        _currency_ = _infos_['unit'].split('/')[0].upper().strip()
        _infos_['toConvert'] = self.final_currency != _currency_
        if _infos_['toConvert']:
            _infos_['initial_currency'] = _currency_
        return self.co2_prices_and_infos\
               .keys_and_infos[self.co2_prices_scenario.lower()]


##******************************************
##    ╔═╗╔╗ ╔═╗╔═╗┌─┐┬  ┌─┐┬ ┬┬  ┌─┐┌┬┐┌─┐┬─┐
##    ║  ╠╩╗╠═╣║  ├─┤│  │  │ ││  ├─┤ │ │ │├┬┘
##    ╚═╝╚═╝╩ ╩╚═╝┴ ┴┴─┘└─┘└─┘┴─┘┴ ┴ ┴ └─┘┴└─
folder_copier = ts.DataReader()._folder_copier

class CBACalculator(ts.Cache):

    @staticmethod
    def _testing_instancer(**kws):
        return CBACalculator(
            run_name               = kws.pop('rn', ''),
            project_horizon        = kws.pop('ph', 20),
            T_so                   = kws.pop('ts', 20),
            T_vg_diff              = kws.pop('td', 1),
            T_vg_unif              = kws.pop('tu', 20),
            discount_rate          = kws.pop('dr', .03),
            initial_landuse        = kws.pop('il', 'improved grassland'),
            final_landuse          = kws.pop('fl', 'wheat'),
            co2_prices_scenario    = kws.pop('sc', 'O'),
            input_flows_scenario   = kws.pop('si', 'IFP'),
            output_flows_scenario  = kws.pop('so', 'O'),
            country                = kws.pop('co', 'france'),
            project_first_year     = kws.pop('y0', 2020),
            polat_repeated_pattern = kws.pop('pr', True),
            change_rates           = kws.pop('cr', {'EUR':{'USD/EUR':1.14}}),
            from_local_data        = kws.pop('ld', False),
            **kws
        )  

    def _clear_caches(self):
        """
        Testing
        -------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.NPV_total_diff_minus_black_output_co2_flows_trajs
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1518.4971863 , -1600.9335023 , -1584.75831751, -1472.35798716]])
        >>> o._clear_caches()
        GlobalWarmingPotential
        OutputFlows
        CarbonAndCo2FlowsAnnualizer
        LandSurfaceFlows
        Co2Prices
        CBACalculator
        """
        for obj in self.__caobjs + [self]:
            print(type(obj).__name__)
            obj._clear_cache()
        self.__caobjs = []

    def __init__(self,
            run_name               = '',
            discount_rate          = .0,
            output                 = 'eth',
            black_output           = 'oIl',
            final_currency         = 'EUR',
            change_rates           = {'EUR':{'USD/EUR':float('nan')}},

            initial_landuse        = 'none',
            final_landuse          = 'none',
            country                = 'none',
            project_horizon        = float('nan'),
            T_so                   = float('nan'),
            T_vg_diff              = float('nan'),
            T_vg_unif              = float('nan'),
            project_first_year     = float('nan'),
            co2_prices_scenario    = 'none',
            output_flows_scenario  = 'none',
            input_flows_scenario   = 'none',
            polat_repeated_pattern = True,
            save_charts            = True,
            GWP_horizon            = 100, #[!!!] EXOGENOUS DATA IMPLICITLY IMPLY GWP100 [!!!]
            GWP_static             = True,#[!!!] EXOGENOUS DATA IMPLICITLY IMPLY STATIC [!!!]
            from_local_data        = False,
            **kwargs
        ):
        
        self.__caobjs = []
        super(CBACalculator, self).__init__(**kwargs)
        self.delay_between_luc_and_production = VegetationsAndSoilSpecificities(
            verbose=kwargs.get('verbose')
        ).delay_between_luc_and_production

        self.discount_rate    = discount_rate
        self.country          = country.upper()
        self.output           = output.upper()
        self.black_output     = black_output.upper()
        self.initial_landuse  = initial_landuse.upper()
        self.final_landuse    = final_landuse.upper()
        self.project_timing   = self.delay_between_luc_and_production.get(
            self.final_landuse, 0
        )
        self._project_horizon = project_horizon + self.project_timing
        self.T_so             = T_so
        self.T_vg_diff        = T_vg_diff
        self.T_vg_unif        = T_vg_unif
        self._GWP_horizon     = 100
        self._GWP_static      = True
        if GWP_horizon != 100 or GWP_static != True:
            raise type(
                'NoDescripterError',
                (BaseException,), {}
            )(
                '\n'.join([
                    '`GWP_horizon` and `GWP_static` must be set to 100 years',
                    'and `True` respectively. The only reason behind this is',
                    'that these two parameters are implictly assumed to be such',
                    'in data reported in attribute `ghgs_emissions_per_tonne_of_eth`',
                    'of the class named `VegetationsAndSoilSpecificities`.'
                ])
            )
            
        self.project_first_year     = project_first_year
        self.polat_repeated_pattern = polat_repeated_pattern
        self.co2_prices_scenario    = co2_prices_scenario
        self.output_flows_scenario  = output_flows_scenario
        self.input_flows_scenario   = input_flows_scenario.upper()
        self.final_currency         = final_currency.upper()
        self.change_rates           = change_rates[self.final_currency]
        self.dashboard              = ts.Dashboard(**kwargs)
        self.from_local_data        = from_local_data
        self.save_charts            = save_charts
        self.pre_run_name           = run_name.replace(' ', '_')
        self.msg                    = None
        self.stdout_off             = False

    @property
    def project_horizon(self):
        """ Horizon of the project (years).
        NB: is a public property-like wrapper of `_project_horizon`.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.project_timing
        1
        >>> o.project_horizon
        4
        """
        return self._project_horizon

    @project_horizon.setter
    def project_horizon(self, v):
        """ Horizon of the project (years).
        NB: is a public property-like setter of `_project_horizon`.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.project_timing
        1
        >>> o.project_horizon = 9
        10
        """
        self._project_horizon = v + self.project_timing
        return self._project_horizon

    @property
    def GWP_horizon(self):
        return self._GWP_horizon
    @property
    def GWP_static(self):
        return self._GWP_static

    @property
    def summary_args(self):
        """ Attributes which consists of parameters used for simulation
        exercices.

        Example
        -------
        >>> print(CBACalculator(
        ...     project_horizon        = 150,
        ...     T_so                   = 20,
        ...     T_vg_diff              = 1,
        ...     T_vg_unif              = 20,
        ...     discount_rate          = .03,
        ...     co2_prices_scenario    = 'WEO2018-SDS',
        ...     initial_landuse        = 'improved grassland',
        ...     final_landuse          = 'wheat',
        ...     input_flows_scenario   = 'IFP',
        ...     output_flows_scenario  = 'O',
        ...     country                = 'france',
        ...     project_first_year     = 2020,
        ...     polat_repeated_pattern = True,
        ...     change_rates           = {'EUR':{'USD/EUR':1.14}},
        ... ).summary_args)
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        **************************************************************************************
        run_name                : [ETH(O)][IMPROVEDGRASSLAND~WHEAT(IFP)][T151Y2020D1][Tvgd1Tvgu20Tso20][Tgwp100STATIC][CO2p(WEO2018-SDS)DR(0.03)]VS[OIL][EUR]
        output                  : ETH
        black_output            : OIL
        initial_landuse         : IMPROVED GRASSLAND
        final_landuse/input     : WHEAT
        country                 : FRANCE
        project_horizon         : 151
        T_so                    : 20
        T_vg_diff               : 1
        T_vg_unif               : 20
        project_first_year      : 2020
        polat_repeated_pattern  : True
        co2_prices_scenario     : WEO2018-SDS
        discount_rate           : 0.03
        diff_payback_period     : 33
        unif_payback_period     : 41
        final_currency          : EUR
        change_rates            : {'USD/EUR': 1.14}
        output_flows_scenario   : O
        input_flows_scenario    : IFP

        Note the difference between the value originally set for `project_horizon`
        (of 150) and that that is returned above. The difference between the two
        values is that the latter integrates the "ante-project" years needed to
        prepare lands. The number of years that are needed to do so are set within
        the attribute `delay_between_luc_and_production` of the class defined in
        the present script and named `VegetationsAndSoilSpecificities`.
        """
        return '\n'.join([
            86*"*",
            'run_name                : %s'%self.run_name,
            'output                  : %s'%self.output,
            'black_output            : %s'%self.black_output,
            'initial_landuse         : %s'%self.initial_landuse,
            'final_landuse/input     : %s'%self.final_landuse,
            'country                 : %s'%self.country,
            'project_horizon         : %s'%self.project_horizon,
            'T_so                    : %s'%self.T_so,
            'T_vg_diff               : %s'%self.T_vg_diff,
            'T_vg_unif               : %s'%self.T_vg_unif,
            'project_first_year      : %s'%self.project_first_year,
            'polat_repeated_pattern  : %s'%self.polat_repeated_pattern,
            'co2_prices_scenario     : %s'%self.co2_prices_scenario,
            'discount_rate           : %s'%self.discount_rate,
            'diff_payback_period     : %s'%self.diff_payback_period,
            'unif_payback_period     : %s'%self.unif_payback_period,
            'final_currency          : %s'%self.final_currency,
            'change_rates            : %s'%self.change_rates,
            'output_flows_scenario   : %s'%self.output_flows_scenario,
            'input_flows_scenario    : %s'%self.input_flows_scenario,
          ##'GWP_horizon             : %s'%self.GWP_horizon,
          ##'GWP_static              : %s'%self.GWP_static,
          ##'save_charts             : %s'%self.save_charts,
        ]+(['message                 : %s'%self.msg,] if self.msg else []))


    @ts.Cache._property
    def run_name(self):
        """ Name of the computation run. It is defined such that results and
        their associated files will have names being representative of the
        simulation settings. Hence, the only possible filenames collisions
        are actually those that consist of the same results.
        

        Example
        -------
        >>> CBACalculator(
        ...     project_horizon        = 150,
        ...     T_so                   = 20,
        ...     T_vg_diff              = 1,
        ...     T_vg_unif              = 20,
        ...     discount_rate          = .03,
        ...     co2_prices_scenario    = 'O',
        ...     initial_landuse        = 'improved grassland',
        ...     final_landuse          = 'wheat',
        ...     input_flows_scenario   = 'IFP',
        ...     output_flows_scenario  = 'O',
        ...     country                = 'france',
        ...     project_first_year     = 2020,
        ...     polat_repeated_pattern = True,
        ...     change_rates           = {'EUR':{'USD/EUR':1.14}},
        ... ).run_name
        '[ETH(O)][IMPROVEDGRASSLAND~WHEAT(IFP)][T151Y2020D1][Tvgd1Tvgu20Tso20][Tgwp100STATIC][CO2p(O)DR(0.03)]VS[OIL][EUR]'

        Probably better to set your own meaningful name, admittedly.
        >>> CBACalculator(run_name='myIdentifyingRunName').run_name
        'myIdentifyingRunName'
        """
        return self.pre_run_name or ''.join([
            '[%s(%s)]'%(
                self.output,
                self.output_flows_scenario
            ),
            '[%s~%s(%s)]'%(
                self.initial_landuse,
                self.final_landuse,
                self.input_flows_scenario
            ),
            '[T%sY%sD%s]'%(
                self.project_horizon,
                self.project_first_year,
                int(self.project_timing)
            ),
            '[Tvgd%sTvgu%sTso%s]'%(
                self.T_vg_diff,
                self.T_vg_unif,
                self.T_so
            ),
            '[Tgwp%s%s]'%(
                int(self.GWP_horizon) if self.GWP_horizon else self.project_horizon,
                'STATIC'*self.GWP_static + 'DYNAMIC'*(1-self.GWP_static)
            ),
            '[CO2p(%s)DR(%s)]'%(
                self.co2_prices_scenario,
                self.discount_rate
            ),
            'VS[%s]'%self.black_output,
            '[%s]'%self.final_currency,
        ]).replace(' ','')

    @property
    def save_dir(self):
        """ Name of the folder wich will contain the generated results.
        It is actually an alias for `run_name`.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(rn='a run name')
        >>> o.save_dir
        'a_run_name'

        >>> o = CBACalculator._testing_instancer()
        >>> o.save_dir
        '[ETH(O)][IMPROVEDGRASSLAND~WHEAT(IFP)][T21Y2020D1][Tvgd1Tvgu20Tso20][Tgwp100STATIC][CO2p(O)DR(0.03)]VS[OIL][EUR]'
        """
        return self.run_name

    @ts.Cache._property
    def horizon(self):
        """ List of years implied by the NPV horizon.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3, y0=2050)
        >>> o.horizon
        [2050, 2051, 2052, 2053]
        """
        y0 = 1 + self.project_first_year - self.project_timing
        return list(range(y0, y0 + self.project_horizon))

    @ts.Cache._property
    def economic_horizon(self):
        """ Array of indexes used as exponent in the discounting calculations.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3, y0=2050)
        >>> o.economic_horizon
        array([[0, 1, 2, 3]])
        """
        return np.array(self.horizon)[None, :] - self.project_first_year

    @ts.Cache._property
    def discounting_factors(self):
        """ Array of discounting factors.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3, y0=2050)
        >>> o.discounting_factors
        array([[1.        , 0.97087379, 0.94259591, 0.91514166]])
        """
        return pow(
            1. + np.array(self.discount_rate).reshape((1,1)),
            -self.economic_horizon
        )

    """**[VGC&SOC*DELTAS*CALCULATION]**************************************************************"""
    @ts.Cache._property
    def deltas_computer(self):
        """ Instantiated class-like object whose methodes and properties will be
        used for calculations of the variations in soil and vegetation carbon
        stocks due to LUC.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.deltas_computer)
        <class '__main__.VGCAndSOCDeltas'>
        >>> o.deltas_computer.absolute_SOC_differential
        -25.527659479999997
        >>> o.deltas_computer.absolute_VGC_differential
        -5.566666667
        """     
        obj = VGCAndSOCDeltas(
            initial_landuse = self.initial_landuse,
            final_landuse   = self.final_landuse,
            country         = self.country,
            verbose         = self.verbose,
            from_local_data = self.from_local_data
        )
        #self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj

    """**[ANNUALIZED*DELTAS]***********************************************************************"""
    @ts.Cache._property
    def carbon_and_co2_flows_traj_annualizer(self):
        """ Instantiated class-like object whose methodes and properties will be
        used for the uniform and differentiated annualizing calculations.

        Testing/Example (emission)
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.carbon_and_co2_flows_traj_annualizer)
        <class '__main__.CarbonAndCo2FlowsAnnualizer'>

        >>> o.carbon_and_co2_flows_traj_annualizer.delta_soc
        -25.527659479999997
        >>> o.carbon_and_co2_flows_traj_annualizer.so_emitting
        True
        >>> o.carbon_and_co2_flows_traj_annualizer.soc_chosen_CRF.__name__
        'soc_POEPLAU_et_al_eq7_p2418'
        >>> o.carbon_and_co2_flows_traj_annualizer.soc_chosen_CRF_constrained(1)
        5.261642499476693e-08

        >>> o.carbon_and_co2_flows_traj_annualizer.delta_vgc
        -5.566666667
        >>> o.carbon_and_co2_flows_traj_annualizer.vg_emitting
        True
        >>> o.carbon_and_co2_flows_traj_annualizer.vgc_chosen_CRF.__name__
        'vgc_POEPLAU_et_al_eq7_p2418'
        >>> o.carbon_and_co2_flows_traj_annualizer.vgc_chosen_CRF_constrained(1)
        2.0478622226436554

        Testing/Example (sequestration)
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     il='degraded grassland', fl='miscanthus', si='none'
        ... )

        >>> o.carbon_and_co2_flows_traj_annualizer.delta_soc
        30.91111111
        >>> o.carbon_and_co2_flows_traj_annualizer.so_emitting
        False
        >>> o.carbon_and_co2_flows_traj_annualizer.soc_chosen_CRF.__name__
        'soc_DUPOUX'
        >>> o.carbon_and_co2_flows_traj_annualizer.soc_chosen_CRF_constrained(1)
        -6.371254812620464e-08
        
        >>> o = CBACalculator._testing_instancer(
        ...     il='miscanthus', fl='degraded grassland', si='none'
        ... )
        >>> o.carbon_and_co2_flows_traj_annualizer.delta_vgc
        5.566666667
        >>> o.carbon_and_co2_flows_traj_annualizer.vg_emitting
        False
        >>> o.carbon_and_co2_flows_traj_annualizer.vgc_chosen_CRF.__name__
        'vgc_DUPOUX'
        >>> o.carbon_and_co2_flows_traj_annualizer.vgc_chosen_CRF_constrained(1)
        -2.0478622226436554
        """ 
        obj = CarbonAndCo2FlowsAnnualizer(
            delta_soc       = self.deltas_computer.absolute_SOC_differential,
            delta_vgc       = self.deltas_computer.absolute_VGC_differential,
            final_landuse   = self.final_landuse,
            project_horizon = self.project_horizon,
            T_so            = self.T_so,
            T_vg_diff       = self.T_vg_diff,
            T_vg_unif       = self.T_vg_unif,
            verbose         = self.verbose,
            from_local_data = self.from_local_data
        )
        self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj
                
    """**[CARBON]**********************************************************************************"""
    @ts.Cache._property
    def soc_unif_flows_traj(self):
        """
        Resolution order:

        >| final_so_carbon_stock_value
        >| initial_so_carbon_stock_value
        ->\ absolute_SOC_differential
        -->\ so_emitting
        --->| soc_unit_unif_flows_traj
        \------------------------------------------------------------------|NON-ANNUALIZATION-SPECIFIC
        >| scenarized_unit_land_surface_infos                              |
        >| scenarized_unit_land_surface_flows_traj_sparse_traj             |
        ->\ scenarized_unit_land_surface_flows_traj_full_traj_as_dict      |
        -->| scenarized_unit_land_surface_flows_traj_full_traj (as array)  |
        >| scenarized_output_flows_traj_sparse_traj                        |
        ->\ scenarized_output_flows_traj_full_traj_as_dict                 |
        -->| scenarized_output_flows_traj_full_traj (as array)             |
        -->| output_flows_traj                                             |
                                                                           |
        ---->\ land_surface_flows_traj                                     |
              \------------------------------------------------------------|
        =======
        ------>| soc_unif_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=20)
        >>> t = o.soc_unif_flows_traj
        >>> np.sum(t)
        -9.909471188708787
        """
        return self.soc_unit_unif_flows_traj\
        *self.land_surface_flows_traj

    @ts.Cache._property
    def soc_diff_flows_traj(self):
        """
        Resolution order:

        >| final_so_carbon_stock_value
        >| initial_so_carbon_stock_value
        ->\ absolute_SOC_differential
        -->| so_emitting
        >| T_so_years_after_LUC
        ->| a_parameter_which_solves_soc_chosen_CRF_constrained
        -->\ soc_unit_stock_traj
        --->| soc_unit_diff_flows_traj
        \-----------------------------------------------------------------|NON-ANNUALIZATION-SPECIFIC
        >| scenarized_unit_land_surface_infos                             |
        >| scenarized_unit_land_surface_flows_traj_sparse_traj            |
        ->\ scenarized_unit_land_surface_flows_traj_full_traj_as_dict     |
        -->| scenarized_unit_land_surface_flows_traj_full_traj (as array) |
        >| scenarized_output_flows_traj_sparse_traj                       |
        ->\ scenarized_output_flows_traj_full_traj_as_dict                |
        -->| scenarized_output_flows_traj_full_traj (as array)            |
        -->| output_flows_traj                                            |
                                                                          |
        ---->\ land_surface_flows_traj                                    |
              \-----------------------------------------------------------|
        =======
        ------>| soc_diff_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=20)
        >>> t = o.soc_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> np.sum(t)
        -9.909471188708789
        """
        return self.soc_unit_diff_flows_traj\
        *self.land_surface_flows_traj

    @property
    def chart_of_soc_unif_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_soc_unif_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """        
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.soc_unif_flows_traj.T,
            labels=['UNIF SOC-TRAJ [tonnes]'],
            colors=['grey'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon so [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @property
    def soc_unit_unif_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'soc_unit_unif_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .soc_unit_unif_flows_traj

    @property
    def chart_of_soc_unit_unif_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_soc_unit_unif_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """   
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.soc_unit_unif_flows_traj.T,
            labels=['UNIF U-SOC-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon u-so [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @property
    def chart_of_soc_diff_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_soc_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """   
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.soc_diff_flows_traj.T,
            labels=['DIFF SOC-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon so [diff-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @property
    def soc_unit_diff_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'soc_unit_diff_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .soc_unit_diff_flows_traj

    @property
    def chart_of_soc_unit_diff_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_soc_unit_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """  
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.soc_unit_diff_flows_traj.T,
            labels=['DIFF U-SOC-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon u-so [diff-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @ts.Cache._property
    def vgc_unif_flows_traj(self):
        """
        Resolution order:

        >| final_vg_carbon_stock_value
        >| initial_vg_carbon_stock_value
        ->\ absolute_VGC_differential
        -->\ vg_emitting
        --->| vgc_unit_unif_flows_traj
        \------------------------------------------------------------------|NON-ANNUALIZATION-SPECIFIC
        >| scenarized_unit_land_surface_infos                              |
        >| scenarized_unit_land_surface_flows_traj_sparse_traj             |
        ->\ scenarized_unit_land_surface_flows_traj_full_traj_as_dict      |
        -->| scenarized_unit_land_surface_flows_traj_full_traj (as array)  |
        >| scenarized_output_flows_traj_sparse_traj                        |
        ->\ scenarized_output_flows_traj_full_traj_as_dict                 |
        -->| scenarized_output_flows_traj_full_traj (as array)             |
        -->| output_flows_traj                                             |
                                                                           |
        ---->\ land_surface_flows_traj                                     |
              \------------------------------------------------------------|
        =======
        ------>| vgc_unif_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=20)
        >>> t = o.vgc_unif_flows_traj
        >>> np.sum(t)
        -2.1609001403751913
        """
        return self.vgc_unit_unif_flows_traj\
        *self.land_surface_flows_traj
    
    @property
    def vgc_unit_unif_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'vgc_unit_unif_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .vgc_unit_unif_flows_traj

    @ts.Cache._property
    def vgc_diff_flows_traj(self):
        """
        Resolution order:

        >| final_vg_carbon_stock_value
        >| initial_vg_carbon_stock_value
        ->\ absolute_VGC_differential
        -->| vg_emitting
        >| T_vg_years_after_LUC
        ->| a_parameter_which_solves_vgc_chosen_CRF_constrained
        -->\ vgc_unit_stock_traj
        --->| vgc_unit_diff_flows_traj
        \------------------------------------------------------------------|NON-ANNUALIZATION-SPECIFIC
        >| scenarized_unit_land_surface_infos                              |
        >| scenarized_unit_land_surface_flows_traj_sparse_traj             |
        ->\ scenarized_unit_land_surface_flows_traj_full_traj_as_dict      |
        -->| scenarized_unit_land_surface_flows_traj_full_traj (as array)  |
        >| scenarized_output_flows_traj_sparse_traj                        |
        ->\ scenarized_output_flows_traj_full_traj_as_dict                 |
        -->| scenarized_output_flows_traj_full_traj (as array)             |
        -->| output_flows_traj                                             |
                                                                           |
        ---->\ land_surface_flows_traj                                     |
              \------------------------------------------------------------|
        =======
        ------>| vgc_diff_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=20)
        >>> t = o.vgc_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> np.sum(t)
        -2.1609001403751917
        """
        return self.vgc_unit_diff_flows_traj\
        *self.land_surface_flows_traj

    @property
    def vgc_unit_diff_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'vgc_unit_diff_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .vgc_unit_diff_flows_traj

    @property
    def chart_of_vgc_unif_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vgc_unif_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """  
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.vgc_unif_flows_traj.T,
            labels=['UNIF VGC-TRAJ [tonnes]'],
            colors=['grey'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon vg [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )
    @property
    def chart_of_vgc_diff_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vgc_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.vgc_diff_flows_traj.T,
            labels=['DIFF VGC-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon vg [diff-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @ts.Cache._property
    def unif_carbon_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| vgc_unit_unif_flows_traj
        --->| soc_unit_unif_flows_traj
            |
        ---->\ unit_unif_carbon_flows_traj
             |-------------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                                 |
        ----->\ land_surface_flows_traj            |
               \-----------------------------------|
        ========
        ------->\ unif_carbon_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, tu=5, ts=5)
        >>> t = o.unif_carbon_flows_traj
        >>> np.sum(t)
        -12.070371329083983
        """
        return self.unit_unif_carbon_flows_traj\
        *self.land_surface_flows_traj

    @property
    def unit_unif_carbon_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'unit_unif_carbon_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .unit_unif_carbon_flows_traj

    @ts.Cache._property
    def diff_carbon_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| vgc_unit_diff_flows_traj
        --->| soc_unit_diff_flows_traj
            |
        ---->\ unit_diff_carbon_flows_traj
             |---------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                             |
        ----->\ land_surface_flows_traj        |
               \-------------------------------|
        ========
        ------->\ diff_carbon_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, ts=5)
        >>> t = o.diff_carbon_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.09004353]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> np.sum(t)
        -12.07037132908398
        """
        return self.unit_diff_carbon_flows_traj\
        *self.land_surface_flows_traj

    @property
    def unit_diff_carbon_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'unit_diff_carbon_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .unit_diff_carbon_flows_traj

    @property
    def chart_of_unif_carbon_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_unif_carbon_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.unif_carbon_flows_traj.T,
            labels=['UNIF [VG+SO] C-TRAJ [tonnes]'],
            colors=['grey'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon vg+so [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )
    @property
    def chart_of_diff_carbon_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_diff_carbon_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.diff_carbon_flows_traj.T,
            labels=['DIFF [VG+SO] C-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES carbon vg+so [diff-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    """**[CO2]*************************************************************************************"""
    @ts.Cache._property
    def soco2_unif_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->\ soc_unit_unif_flows_traj
        ---->\ soco2_unit_unif_flows_traj
             |----------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                              |
        ----->\ land_surface_flows_traj         |
               \--------------------------------|
        ========
        ------->\ soco2_unif_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, ts=4)
        >>> t = o.soco2_unif_flows_traj
        >>> t
        array([[-2.72510458, -2.72510458, -2.72510458, -2.72510458,  0.        ,
                 0.        ]])
        >>> np.sum(t)
        -10.900418307579667
        """
        return self.soco2_unit_unif_flows_traj\
        *self.land_surface_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @property
    def soco2_unit_unif_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'soco2_unit_unif_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .soco2_unit_unif_flows_traj 

    @ts.Cache._property
    def soco2_diff_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->\ soc_unit_diff_flows_traj
        ---->\ soco2_unit_diff_flows_traj
             |------------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                                |
        ----->\ land_surface_flows_traj           |
               \----------------------------------|
        ========
        ------->\ soco2_diff_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, ts=4)
        >>> t = o.soco2_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.09621511]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> t        
        array([[-1.09000844e+01, -3.33920718e-04, -1.02295580e-08,
                -3.14023912e-13,  0.00000000e+00,  0.00000000e+00]])
        >>> np.sum(t)
        -10.900418307579667
        """
        return self.soco2_unit_diff_flows_traj\
        *self.land_surface_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @property
    def soco2_unit_diff_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'soco2_unit_diff_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .soco2_unit_diff_flows_traj      

    @property
    def chart_of_soco2_unif_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_soco2_unif_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.soco2_unif_flows_traj.T,
            labels=['UNIF SOCO2-TRAJ [tonnes]'],
            colors=['grey'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 so [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )
    @property
    def chart_of_soco2_diff_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_soco2_diff_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.soco2_diff_flows_traj.T,
            labels=['DIFF SOCO2-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 so [diff-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @ts.Cache._property
    def vgco2_unif_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->\ vgc_unit_unif_flows_traj
        ---->\ vgco2_unit_unif_flows_traj
             |-------------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                                 |
        ----->\ land_surface_flows_traj            |
               \-----------------------------------|
        ========
        ------->\ vgco2_unif_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=7, tu=4)
        >>> t = o.vgco2_unif_flows_traj
        >>> t
        array([[-1.78274262, -1.78274262, -1.78274262, -1.78274262,  0.        ,
                 0.        ,  0.        ,  0.        ]])
        >>> np.sum(t)
        -7.130970463238132
        """
        return self.vgco2_unit_unif_flows_traj\
        *self.land_surface_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @property
    def vgco2_unit_unif_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'vgco2_unit_unif_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .vgco2_unit_unif_flows_traj

    @ts.Cache._property
    def vgco2_diff_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->\ vgc_unit_diff_flows_traj
        ---->\ vgco2_unit_diff_flows_traj
             |-------------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                                 |
        ----->\ land_surface_flows_traj            |
               \-----------------------------------|
        ========
        ------->\ vgco2_diff_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=7, td=4)
        >>> t = o.vgco2_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.09430653]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> t
        array([[-7.13079345e+00, -1.77011362e-04, -4.39404445e-09,
                -1.09225709e-13,  0.00000000e+00,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00]])
        >>> np.sum(t)
        -7.130970463238132
        """
        return self.vgco2_unit_diff_flows_traj\
        *self.land_surface_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @property
    def vgco2_unit_diff_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'vgco2_unit_diff_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .vgco2_unit_diff_flows_traj

    @property
    def chart_of_vgco2_unif_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vgco2_unif_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.vgco2_unif_flows_traj.T,
            labels=['UNIF VGCO2-TRAJ [tonnes]'],
            colors=['grey'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 vg [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )
    @property
    def chart_of_vgco2_diff_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vgco2_diff_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.vgco2_diff_flows_traj.T,
            labels=['DIFF VGCO2-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 vg [diff-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )

    @ts.Cache._property
    def unif_co2_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| vgc_unit_unif_flows_traj
        --->| soc_unit_unif_flows_traj
            |
        ---->\ unit_unif_carbon_flows_traj
        ----->\ unit_unif_co2_flows_traj
             |-------------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                                 |
        ----->\ land_surface_flows_traj            |
               \-----------------------------------|
        ========
        ------->\ unif_co2_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=6, ts=2, tu=4)
        >>> t = o.unif_co2_flows_traj
        >>> t
        array([[-7.23295177, -7.23295177, -1.78274262, -1.78274262,  0.        ,
                 0.        ,  0.        ]])
        >>> np.sum(t)
        -18.0313887708178
        """
        return self.unit_unif_co2_flows_traj\
        *self.land_surface_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @property
    def unit_unif_co2_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'unit_unif_co2_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .unit_unif_co2_flows_traj

    @ts.Cache._property
    def diff_co2_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| vgc_unit_diff_flows_traj
        --->| soc_unit_diff_flows_traj
            |
        ---->\ unit_diff_carbon_flows_traj
        ----->\ unit_diff_co2_flows_traj
             |-------------------------------------|NON-ANNUALIZATION-SPECIFIC
             | ...                                 |
        ----->\ land_surface_flows_traj            |
               \-----------------------------------|
        ========
        ------->\ diff_co2_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=6, ts=2, td=4)
        >>> t = o.diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.09430653]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> t
        array([[-1.80312116e+01, -1.77144720e-04, -4.39404445e-09,
                -1.09225709e-13,  0.00000000e+00,  0.00000000e+00,
                 0.00000000e+00]])
        >>> np.sum(t)
        -18.0313887708178
        """
        return self.unit_diff_co2_flows_traj\
        *self.land_surface_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @property
    def unit_diff_co2_flows_traj(self):
        """
        Testing
        -------
        >>> hasattr(CarbonAndCo2FlowsAnnualizer, 'unit_diff_co2_flows_traj')
        True
        """
        return self.carbon_and_co2_flows_traj_annualizer\
        .unit_diff_co2_flows_traj

    @property
    def chart_of_unif_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_unif_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.unif_co2_flows_traj.T,
            labels=['UNIF [VG+SO] CO2-TRAJ [tonnes]'],
            colors=['grey'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 vg+so [unif-%s~%s]'%(
                self.initial_landuse, self.final_landuse
            ),
            bar=True
        )
    
    @property
    def chart_of_diff_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.diff_co2_flows_traj.T,
            labels=['DIFF [VG+SO] CO2-TRAJ [tonnes]'],
            colors=['black'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 vg+so [diff-%s~%s]'%(
                self.initial_landuse,
                self.final_landuse
            ),
            bar=True
        )

    """**[CO2*PRICES]******************************************************************************"""
    @ts.Cache._property
    def co2_prices_computer(self):
        """ Instantiated class-like object whose methodes and properties will be
        used for calculations of the scenarized CO2 prices/tonne trajectory.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.co2_prices_computer)
        <class '__main__.Co2Prices'>
        """
        obj = Co2Prices(
            scenario                  = self.co2_prices_scenario,
            first_year                = self.project_first_year\
                                        - self.project_timing,
            project_horizon           = self.project_horizon,
            repeated_pattern_polation = self.polat_repeated_pattern,
            final_currency            = self.final_currency,
            country                   = self.country,
            verbose                   = self.verbose,
            from_local_data           = self.from_local_data
        )
        self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj                
                
    @ts.Cache._property
    def co2_prices_traj(self):
        """
        Resolution order:

        >| scenarized_co2_infos
        >| scenarized_co2_prices_sparse_traj
        ->\ scenarized_co2_prices_full_traj_as_dict
        -->| scenarized_co2_prices_full_traj (as array)
        ===
        -->| co2_prices_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(y0=2020, ph=20, sc='WEO2015-450S')
        >>> o.co2_prices_traj
        array([[ 19.29824561,  22.45306127,  26.12361612,  30.39422158,
                 35.362972  ,  41.14399789,  47.87008746,  55.69573671,
                 64.80069814,  75.39410963,  87.71929825,  90.7210258 ,
                 93.82547155,  97.03615049, 100.35669788, 103.79087339,
                107.34256533, 111.01579508, 114.81472163, 118.74364629,
                122.80701754]])

        Remember that the above prices has been converted from USD to EUR.
        The USD price of 1EUR that has been used is
        >>> r = o.change_rates['USD/EUR']
        >>> r
        1.14
        >>> r*o.co2_prices_traj
        array([[ 22.        ,  25.59648984,  29.78092238,  34.6494126 ,
                 40.31378808,  46.9041576 ,  54.57189971,  63.49313985,
                 73.87279588,  85.94928498, 100.        , 103.42196941,
                106.96103757, 110.62121156, 114.40663559, 118.32159566,
                122.37052447, 126.55800639, 130.88878266, 135.36775677,
                140.        ]])
        """
        _infos_ = self.co2_prices_computer.scenarized_co2_infos
        return self.co2_prices_computer.scenarized_co2_prices_full_traj*(
            ts.change_rate_extractor(
                self.change_rates,
                _infos_['initial_currency'],
                self.final_currency
            ) if _infos_['toConvert'] else 1.
        )

    @property
    def chart_of_co2_prices_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_co2_prices_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.co2_prices_traj.T,
            labels=['CO2 %s prices [%s/tonne]'%(
                self.co2_prices_scenario, self.final_currency
            )],
            colors=['red'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='PRICES co2 [%s]'%(
                self.co2_prices_scenario
            ),
            bar=False
        )
    @ts.Cache._property
    def co2_disc_prices_traj(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
        >| horizon
        ->\ economic_horizon
        ->| discounting_factors
        ====
        --->\ co2_disc_prices_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     y0=2020, ph=3, dr=.0, sc='WEO2015-450S'
        ... ).co2_disc_prices_traj
        array([[19.29824561, 22.45306127, 26.12361612, 30.39422158]])
        
        >>> CBACalculator._testing_instancer(
        ...     y0=2020, ph=3, dr=.01, sc='WEO2015-450S'
        ... ).co2_disc_prices_traj
        array([[19.29824561, 22.23075373, 25.60887768, 29.50033202]])
        """
        return self.co2_prices_traj*self.discounting_factors

    @property
    def chart_of_co2_disc_prices_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_co2_disc_prices_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """ 
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.co2_disc_prices_traj.T,
            labels=['CO2 %s prices-d [%s/tonne]'%(
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkgreen'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='PRICES-D co2 [%s]'%(
                self.co2_prices_scenario
            ),
            bar=False
        )
    """**[OUTPUT*FLOWS]*****************************************************************************"""
    @ts.Cache._property
    def output_flows_traj_computer(self):
        """ Instantiated class-like object whose methodes and properties will
        be used for calculations of the scenarized trajectory of annual tonnes
        of output flows.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.output_flows_traj_computer)
        <class '__main__.OutputFlows'>
        """
        obj = OutputFlows(
            output                    = self.output,
            scenario                  = self.output_flows_scenario,
            first_year                = self.project_first_year,
            project_horizon           = self.project_horizon,
            repeated_pattern_polation = self.polat_repeated_pattern,
            country                   = self.country,
            verbose                   = self.verbose,
            from_local_data           = self.from_local_data
        )
        self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj

    @ts.Cache._property
    def output_flows_traj(self):
        """
        Resolution order:

        >| scenarized_output_flows_traj_sparse_traj
        ->\ scenarized_output_flows_traj_full_traj_as_dict
        -->| scenarized_output_flows_traj_full_traj (as array)
        ===
        -->| output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, so='O')
        >>> o.output_flows_traj
        array([[1., 1., 1., 1., 1., 1.]])
        
        >>> o = CBACalculator._testing_instancer(ph=5, so='DEBUG')
        >>> o.output_flows_traj
        array([[1., 1., 1., 1., 1., 1.]])
        """
        return self.output_flows_traj_computer\
        .scenarized_output_flows_traj_full_traj

    @ts.Cache._property
    def timed_output_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        -->| output_flows_traj
        ====
        --->\ timed_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, so='O')
        >>> o.timed_output_flows_traj
        array([[0., 1., 1., 1., 1., 1.]])

        The attribute `delay_between_luc_and_production` of the class defined in
        the present script and named `VegetationsAndSoilSpecificities` is the
        reason behind this prepended 0.
        """
        _D_ = self.project_timing
        return np.hstack((
            np.zeros((1, _D_)),
            self.output_flows_traj
        ))[:, :(-_D_ if _D_ else None)]

    @property
    def chart_of_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_output_flows_traj.T,
            labels=['%s %s flows [tonnes]'%(
                self.output, self.output_flows_scenario
            )],
            colors=['blue'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES %s [%s]'%(
                self.output, self.output_flows_scenario
            ),
            bar=True
        )

    """**[CUM-OUTPUT*FLOWS]*************************************************************************"""
    @ts.Cache._property
    def cum_output_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        -->| output_flows_traj
        ====
        --->\ cum_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, so='O')
        >>> o.cum_output_flows_traj
        array([[1., 2., 3., 4., 5., 6.]])
        """
        return np.cumsum(self.output_flows_traj, axis=1)

    @ts.Cache._property
    def timed_P_cum_output_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| cum_output_flows_traj
        =====
        ---->\ timed_P_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, so='O')
        >>> o.timed_P_cum_output_flows_traj
        array([[0., 1., 2., 3., 4., 5.]])
        
        It takes one year to launch production.
        """
        _D_ = self.project_timing
        return np.hstack((
            np.zeros((1, _D_)),
            self.cum_output_flows_traj
        ))[:, :(-_D_ if _D_ else None)]

    @ts.Cache._property
    def timed_C_cum_output_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| cum_output_flows_traj
        =====
        ---->\ timed_C_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=5, so='O')
        >>> o.timed_C_cum_output_flows_traj
        array([[1., 2., 3., 4., 5., 5.]])

        During the last year, in the present case, there is no production.
        """
        _D_ = self.project_timing
        return np.hstack((
            self.cum_output_flows_traj[:, :(-_D_ if _D_ else None)],
            _D_*[self.cum_output_flows_traj[:, -_D_-1]]
        ))


    """**[INPUT*FLOWS]******************************************************************************"""
    @ts.Cache._property
    def input_flows_traj_computer(self):
        """ Instantiated class-like object whose methodes and properties will
        be used for calculations of the scenarized trajectory of annual tonnes
        of input flows.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.input_flows_traj_computer)
        <class '__main__.InputFlows'>
        """       
        obj = InputFlows(
            final_landuse             = self.final_landuse,
            scenario                  = self.input_flows_scenario,
            first_year                = self.project_first_year,
            project_horizon           = self.project_horizon,
            repeated_pattern_polation = self.polat_repeated_pattern,
            country                   = self.country,
            verbose                   = self.verbose,
            from_local_data           = self.from_local_data
        )
        self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj

    @ts.Cache._property
    def input_flows_traj(self):
        """
        Resolution order:
        ..
          \ ...
        -->| output_flows_traj
        >| scenarized_unit_input_infos
        >| scenarized_unit_input_flows_traj_sparse_traj
        ->\ scenarized_unit_input_flows_traj_full_traj_as_dict
        -->| scenarized_unit_input_flows_traj_full_traj (as array)
        ====
        --->\ input_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=3, so='O', fl='wheat', si='IFP'
        ... ).input_flows_traj
        array([[3.5161744, 3.5161744, 3.5161744, 3.5161744]])

        >>> CBACalculator._testing_instancer(
        ...     ph=3, so='O', fl='miscanthus', si='DOE'
        ... ).input_flows_traj
        array([[3.13994279, 3.13994279, 3.13994279, 3.13994279]])
        """
        ifc = self.input_flows_traj_computer
        return pow(
            ifc.scenarized_unit_input_flows_traj_full_traj,
            ifc.scenarized_unit_input_infos['power']
        )*self.output_flows_traj

    @ts.Cache._property
    def timed_input_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        -->| input_flows_traj
        ====
        --->\ timed_input_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=3, so='O', fl='wheat', si='IFP'
        ... ).timed_input_flows_traj
        array([[3.5161744, 3.5161744, 3.5161744, 0.       ]])

        >>> CBACalculator._testing_instancer(
        ...     ph=3, so='O', fl='miscanthus', si='DOE'
        ... ).timed_input_flows_traj
        array([[3.13994279, 3.13994279, 3.13994279, 0.        ]])
        """
        _D_ = self.project_timing
        return np.hstack((
            self.input_flows_traj[:, :(-_D_ if _D_ else None)],
            np.zeros((1, _D_))
        ))

    @property
    def chart_of_input_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_input_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_input_flows_traj.T,
            labels=['%s %s flows [tonnes]'%(
                self.final_landuse, self.input_flows_scenario
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES input [%s][%s]'%(
                self.input_flows_scenario, self.final_landuse
            ),
            bar=True
        )

    """**[INPUT-CO2eq*FLOWS]************************************************************************"""
    @ts.Cache._property
    def co2eq_computer(self):
        """ Instantiated class-like object whose methodes and properties will be
        used for calculations of the scenarized trajectory of annual tonnes of
        co2eq flows. NB : `co2eq` calculations follow Levasseur (2010).

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.co2eq_computer)
        <class '__main__.GlobalWarmingPotential'>
        """
        obj = GlobalWarmingPotential(
            first_year      = self.project_first_year,
            project_horizon = self.project_horizon,
            GWP_horizon     = self.GWP_horizon,
            static          = self.GWP_static,
            verbose         = self.verbose,
            from_local_data = self.from_local_data
        )
        self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj

    @ts.Cache._property
    def cultivated_unit_input_co2eq_flows_traj_as_dict(self):
        """
        Resolution order:

        >| AGWP<project_horizon+1>_CO2_traj
        ->\ GWP<project_horizon+1>_CO2_traj ( = 1.)
        >| AGWP<project_horizon+1>_CH4_traj
        ->\ GWP<project_horizon+1>_CH4_traj
        >| AGWP<project_horizon+1>_N2O_traj
        ->\ GWP<project_horizon+1>_N2O_traj
        ===
        -->| cultivated_unit_input_co2eq_flows_traj_as_dict

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> sorted(
        ...     o.cultivated_unit_input_co2eq_flows_traj_as_dict.items()
        ... )
        [(2020, -1.04039), (2021, -1.04039), (2022, -1.04039), (2023, -1.04039)]
        """
        return self.co2eq_computer.co2eq_yields_GWP_traj_computer(
            self.co2eq_computer\
            .biomass_ghgs_specificities['culture'][self.final_landuse]
        )
            
    @property
    def chart_of_cult_unit_input_co2eq_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_cult_unit_input_co2eq_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=ts.dict_time_serie_as_row_array(
                self.cultivated_unit_input_co2eq_flows_traj_as_dict
            ).T,
            labels=['%s-CO2eq unitary cult-flows [tonnes]'%(self.final_landuse)],
            colors=['mediumpurple'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='GWP FLOWS TONNES co2eq [cult-%s]'%(
                self.final_landuse
            ),
            bar=True
        )

    @ts.Cache._property
    def cultivated_input_co2eq_flows_traj(self):
        """
        Resolution order:
        ..
          \ ...
        -->| as_row_array( cultivated_unit_input_co2eq_flows_traj_as_dict )
        ..
          \ ...
        -->| output_flows_traj
        ====
        --->\ cultivated_input_co2eq_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.cultivated_input_co2eq_flows_traj
        array([[-1.04039, -1.04039, -1.04039, -1.04039]])
        """
        return ts.dict_time_serie_as_row_array(
            self.cultivated_unit_input_co2eq_flows_traj_as_dict
        )*self.output_flows_traj

    @ts.Cache._property
    def timed_cult_input_co2eq_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| cultivated_input_co2eq_flows_traj
        =====
        ---->\ timed_cult_input_co2eq_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.timed_cult_input_co2eq_flows_traj
        array([[-1.04039, -1.04039, -1.04039,  0.     ]])
        """
        _D_ = self.project_timing
        return np.hstack((
            self.cultivated_input_co2eq_flows_traj[
                :, :(-_D_ if _D_ else None)
            ],
            np.zeros((1, _D_))
        ))

    @property
    def chart_of_cult_input_co2eq_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_cult_input_co2eq_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_cult_input_co2eq_flows_traj.T,
            labels=['%s-CO2eq cult-flows [tonnes]'%(self.final_landuse)],
            colors=['mediumpurple'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2eq [cult-%s]'%(self.final_landuse),
            bar=True
        )

    @ts.Cache._property
    def processed_unit_input_co2eq_flows_traj_as_dict(self):
        """
        Resolution order:

        >| AGWP<project_horizon+1>_CO2_traj
        ->\ GWP<project_horizon+1>_CO2_traj ( = 1.)
        >| AGWP<project_horizon+1>_CH4_traj
        ->\ GWP<project_horizon+1>_CH4_traj
        >| AGWP<project_horizon+1>_N2O_traj
        ->\ GWP<project_horizon+1>_N2O_traj
        ===
        -->| processed_unit_input_co2eq_flows_traj_as_dict

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> sorted(
        ...     o.processed_unit_input_co2eq_flows_traj_as_dict.items()
        ... )
        [(2020, -0.8895799999999999), (2021, -0.8895799999999999), (2022, -0.8895799999999999), (2023, -0.8895799999999999)]
        """
        ghgs_yield = self.co2eq_computer\
                     .biomass_ghgs_specificities['process'][self.final_landuse]
        return self.co2eq_computer.co2eq_yields_GWP_traj_computer(
            ghgs_yield
        )
        
    @property
    def chart_of_proc_unit_input_co2eq_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_proc_unit_input_co2eq_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=ts.dict_time_serie_as_row_array(
                self.processed_unit_input_co2eq_flows_traj_as_dict
            ).T,
            labels=[
                '%s-CO2eq unitary proc-flows [tonnes]'%(self.final_landuse)
            ],
            colors=['darkslateblue'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='GWP FLOWS TONNES co2eq [proc-%s]'%(self.final_landuse),
            bar=True
        )

    @ts.Cache._property
    def processed_input_co2eq_flows_traj(self):
        """
        Resolution order:
        ..
          \ ...
        -->| as_row_array( processed_unit_input_co2eq_flows_traj_as_dict )
        ..
          \ ...
        -->| output_flows_traj
        ====
        --->\ processed_input_co2eq_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.processed_input_co2eq_flows_traj
        array([[-0.88958, -0.88958, -0.88958, -0.88958]])
        """
        return ts.dict_time_serie_as_row_array(
            self.processed_unit_input_co2eq_flows_traj_as_dict
        )*self.output_flows_traj

    @ts.Cache._property
    def timed_proc_input_co2eq_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| processed_input_co2eq_flows_traj
        =====
        ---->\ timed_proc_input_co2eq_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=3)
        >>> o.timed_proc_input_co2eq_flows_traj
        array([[ 0.     , -0.88958, -0.88958, -0.88958]])
        """
        _D_ = self.project_timing
        return np.hstack((
            np.zeros((1, _D_)),
            self.processed_input_co2eq_flows_traj
        ))[:, :(-_D_ if _D_ else None)]
        
    @property
    def chart_of_proc_input_co2eq_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_proc_input_co2eq_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_proc_input_co2eq_flows_traj.T,
            labels=['%s-CO2eq proc-flows [tonnes]'%(self.final_landuse)],
            colors=['darkslateblue'],save=self.save_charts,save_dir=self.save_dir,
            file_name='FLOWS TONNES co2eq [proc-%s]'%(self.final_landuse),
            bar=True
        )

    """**[LAND*FLOWS]*******************************************************************************"""
    @ts.Cache._property
    def land_surface_flows_traj_computer(self):
        """ Instantiated class-like object whose methodes and properties will
        be used for calculations of the scenarized trajectory of annual HA of
        lands.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer()
        >>> type(o.land_surface_flows_traj_computer)
        <class '__main__.LandSurfaceFlows'>
        """
        obj = LandSurfaceFlows(
            output                    = self.output,
            final_landuse             = self.final_landuse,
            first_year                = self.project_first_year,
            project_horizon           = self.project_horizon,
            repeated_pattern_polation = self.polat_repeated_pattern,
            country                   = self.country,
            verbose                   = self.verbose,
            from_local_data           = self.from_local_data
        )
        self.__caobjs.append(obj)
        if self._cache.get('endogenizing', False):
            obj._cache['endogenizing'] = True
        return obj

    @ts.Cache._property
    def land_surface_flows_traj(self):
        """
        Resolution order:

        >| scenarized_unit_land_surface_infos
        >| scenarized_unit_land_surface_flows_traj_sparse_traj
        ->\ scenarized_unit_land_surface_flows_traj_full_traj_as_dict
        -->| scenarized_unit_land_surface_flows_traj_full_traj (as array)
        ..
          \ ...
        -->| output_flows_traj
        ====
        --->\ land_surface_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.land_surface_flows_traj
        array([[0.38818565, 0.38818565, 0.38818565]])
        """
        lfc = self.land_surface_flows_traj_computer
        return pow(
            lfc.scenarized_unit_land_surface_flows_traj_full_traj,
            lfc.scenarized_unit_land_surface_infos['power']
        )*self.output_flows_traj

    @ts.Cache._property
    def timed_land_surface_flows_traj(self):
        """
        Resolution order:
        ...
           \ ...
        --->| land_surface_flows_traj
        =====
        ---->\ timed_land_surface_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.timed_land_surface_flows_traj
        array([[0.38818565, 0.38818565, 0.        ]])
        """            
        _D_ = self.project_timing
        return np.hstack((
            self.land_surface_flows_traj[:, :(-_D_ if _D_ else None)],
            np.zeros((1, _D_))
        ))

    @property
    def chart_of_land_surface_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_land_surface_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_land_surface_flows_traj.T,
            labels=['%s-%s flows [ha]'%(
                self.land_surface_flows_traj_computer.land_input, self.final_landuse
            )],
            colors=['yellow'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS HA land [%s]'%(self.final_landuse),
            bar=True
        )

    """**[PROC&CULT*CO2*VALUE]**********************************************************************"""
    #----------------------------------< NON ANNUALIZATION SPECIFIC >----------------------------------

    @ts.Cache._property
    def timed_proc_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
         ...
            \ ...
        ---->| timed_proc_input_co2eq_flows_traj
        ======
        ----->\ timed_proc_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=1)
        >>> o.timed_proc_co2_flows_traj_values
        array([[  0.     , -77.39346]])
        """
        return self.timed_proc_input_co2eq_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_proc_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_proc_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_proc_co2_flows_traj_values.T,
            labels=['%s process co2 value [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 process [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_proc_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
          ...
             \ ...
        ----->\ timed_proc_co2_flows_traj_values
        =======
        ------>\ timed_proc_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=1)
        >>> o.timed_proc_co2_flows_traj_disc_values
        array([[  0.        , -75.13928155]])
        """
        return self.timed_proc_co2_flows_traj_values*self.discounting_factors

    @property
    def chart_of_proc_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_proc_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_proc_co2_flows_traj_disc_values.T,
            labels=['%s process co2 value-d [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 process [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )


    @ts.Cache._property
    def timed_cult_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
         ...
            \ ...
        ---->| timed_cult_input_co2eq_flows_traj
        ======
        ----->\ timed_cult_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.timed_cult_co2_flows_traj_values
        array([[-90.51393, -90.51393,   0.     ]])
        """
        return self.timed_cult_input_co2eq_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_cult_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_cult_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_cult_co2_flows_traj_values.T,
            labels=['%s culture co2 value [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_cult_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
          ...
             \ ...
        ----->\ timed_cult_co2_flows_traj_values
        =======
        ------>\ timed_cult_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.timed_cult_co2_flows_traj_disc_values
        array([[-90.51393   , -87.87760194,   0.        ]])
        """
        return self.timed_cult_co2_flows_traj_values*self.discounting_factors

    @property
    def chart_of_cult_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_cult_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_cult_co2_flows_traj_disc_values.T,
            labels=['%s culture co2 value-d [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_cult_co2_flows_traj(self):
        """
        Resolution order:
           ...
              \ ...
        ------>\ timed_cult_co2_flows_traj_disc_values
        ========
        ------->\ NPV_cult_co2_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_cult_co2_flows_traj
        array([[ -90.51393   , -178.39153194, -178.39153194]])
        """
        return np.cumsum(
            self.timed_cult_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_cult_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_cult_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_cult_co2_flows_traj.T,
            labels=['%s culture co2 NPV [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_cult_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_C_cum_output_flows_traj
           ...
              \ ...
        ------>\ NPV_cult_co2_flows_traj
        ========
        ------->\ NPV_cult_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_cult_co2_flows_traj_per_cum_output_flows_traj
        array([[-90.51393   , -89.19576597, -89.19576597]])
        """
        return np.nan_to_num(
            self.NPV_cult_co2_flows_traj/self.timed_C_cum_output_flows_traj
        )

    @property
    def chart_of_NPV_cult_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_cult_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_cult_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['%s culture co2 NPV [%s][%s/TONNE]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkblue'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )
    @ts.Cache._property
    def NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
            ...
               \ ...
        ------->\ NPV_cult_co2_flows_traj_per_cum_output_flows_traj
        =========
        -------->\ NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[-0.00338891, -0.00333956, -0.00333956]])
        """
        return self.NPV_cult_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['%s culture co2 NPV [%s][%s/MJ]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkblue'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_proc_plus_cult_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
         ...
            \ ...
        ---->| timed_cult_input_co2eq_flows_traj
         ...
            \ ...
        ---->| timed_proc_input_co2eq_flows_traj
        ======
        ----->\ timed_proc_plus_cult_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.timed_proc_plus_cult_co2_flows_traj_values
        array([[ -90.51393, -167.90739,  -77.39346]])
        """
        return (
            self.timed_proc_input_co2eq_flows_traj\
            + self.timed_cult_input_co2eq_flows_traj
        )*self.co2_prices_traj

    @property
    def chart_of_proc_plus_cult_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_proc_plus_cult_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_proc_plus_cult_co2_flows_traj_values.T,
            labels=['%s process+culture co2 value [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 process+culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_proc_co2_flows_traj(self):
        """
        Resolution order:
           ...
              \ ...
        ------>\ timed_proc_co2_flows_traj_disc_values
        ========
        ------->\ NPV_proc_co2_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_proc_co2_flows_traj
        array([[   0.        ,  -75.13928155, -148.09004034]])
        """
        return np.cumsum(
            self.timed_proc_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_proc_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_proc_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_proc_co2_flows_traj.T,
            labels=['%s process co2 NPV [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 process [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_proc_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_P_cum_output_flows_traj
           ...
              \ ...
        ------>\ NPV_proc_co2_flows_traj
        ========
        ------->\ NPV_proc_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_proc_co2_flows_traj_per_cum_output_flows_traj
        array([[  0.        , -75.13928155, -74.04502017]])
        """
        return np.nan_to_num(
            self.NPV_proc_co2_flows_traj/self.timed_P_cum_output_flows_traj
        )

    @property
    def chart_of_NPV_proc_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_proc_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_proc_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['%s process co2 NPV [%s][%s/TONNE]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 process [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )
    @ts.Cache._property
    def NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
            ...
               \ ...
        ------->\ NPV_proc_co2_flows_traj_per_cum_output_flows_traj
        =========
        -------->\ NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[ 0.        , -0.00281327, -0.0027723 ]])
        """
        return self.NPV_proc_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['%s process co2 NPV [%s][%s/MJ]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 process [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_proc_plus_cult_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
          ...
             \ ...
        ----->\ timed_proc_plus_cult_co2_flows_traj_values
        =======
        ------>\ timed_proc_plus_cult_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.timed_proc_plus_cult_co2_flows_traj_disc_values
        array([[ -90.51393   , -163.0168835 ,  -72.95075879]])
        """
        return self.timed_proc_plus_cult_co2_flows_traj_values\
        *self.discounting_factors

    @property
    def chart_of_proc_plus_cult_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_proc_plus_cult_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_proc_plus_cult_co2_flows_traj_disc_values.T,
            labels=['%s process+culture co2 value-d [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 process+culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_proc_plus_cult_co2_flows_traj(self):
        """
        Resolution order:
           ...
              \ ...
        ------>\ timed_proc_plus_cult_co2_flows_traj_disc_values
        ========
        ------->\ NPV_proc_plus_cult_co2_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_proc_plus_cult_co2_flows_traj
        array([[ -90.51393   , -253.5308135 , -326.48157228]])
        """
        return np.cumsum(
            self.timed_proc_plus_cult_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_proc_plus_cult_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_proc_plus_cult_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_proc_plus_cult_co2_flows_traj.T,
            labels=['%s process+culture co2 NPV [%s][%s]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 process+culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
            ...
               \ ...
        ------->\ NPV_cult_co2_flows_traj_per_cum_output_flows_traj
            ...
               \ ...
        ------->\ NPV_proc_co2_flows_traj_per_cum_output_flows_traj
        =========
        -------->\ NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj
        array([[ -90.51393   , -164.33504752, -163.24078614]])
        """
        return self.NPV_proc_co2_flows_traj_per_cum_output_flows_traj\
        + self.NPV_cult_co2_flows_traj_per_cum_output_flows_traj

    @property
    def chart_of_NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['%s process+culture co2 NPV [%s][%s/TONNE]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 process+culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
             ...
                \ ...
        -------->\ NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj
        ==========
        --------->\ NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=2)
        >>> o.NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[-0.00338891, -0.00615283, -0.00611186]])
        """
        return self.NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['%s process+culture co2 NPV [%s][%s/MJ]'%(
                self.final_landuse,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 process+culture [%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )


    #---------------------------------------------< DIFF >---------------------------------------------
    @ts.Cache._property
    def timed_vg_diff_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
            ...
               \ ...
        ------->\ vgco2_diff_flows_traj
        =========
        -------->\ timed_vg_diff_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, td=1
        ... ).timed_vg_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-620.3944303,    0.       ,    0.       ,    0.       ,
                   0.       ,    0.       ]])

        >>> CBACalculator._testing_instancer(
        ...     ph=5, td=2
        ... ).timed_vg_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-6.20394430e+02, -4.47322267e-07,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.vgco2_diff_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_vg_diff_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vg_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_vg_diff_co2_flows_traj_values.T,
            labels=['diff-%s co2 vg value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_vg_diff_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
             ...
                \ ...
        -------->\ timed_vg_diff_co2_flows_traj_values
        ==========
        --------->\ timed_vg_diff_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, td=2
        ... ).timed_vg_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-6.20394430e+02, -4.34293463e-07,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.timed_vg_diff_co2_flows_traj_values\
        *self.discounting_factors

    @property
    def chart_of_vg_diff_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vg_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_vg_diff_co2_flows_traj_disc_values.T,
            labels=['diff-%s co2 vg value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_vg_diff_co2_flows_traj(self):
        """
        Resolution order:
              ...
                 \ ...
        --------->\ timed_vg_diff_co2_flows_traj_disc_values
        ===========
        ---------->\ NPV_vg_diff_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, td=2
        ... ).NPV_vg_diff_co2_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-620.39442985, -620.39443029, -620.39443029, -620.39443029,
                -620.39443029, -620.39443029]])
        """
        return np.cumsum(
            self.timed_vg_diff_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_vg_diff_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_vg_diff_co2_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_vg_diff_co2_flows_traj.T,
            labels=['diff-%s co2 vg NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_C_cum_output_flows_traj
               ...
                  \ ...
        ---------->\ NPV_vg_diff_co2_flows_traj
        ============
        ----------->\ NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, td=2
        ... ).NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-620.39442985, -310.19721514, -206.79814343, -155.09860757,
                -124.07888606, -124.07888606]])
        """
        return np.nan_to_num(
            self.NPV_vg_diff_co2_flows_traj
            /self.timed_C_cum_output_flows_traj
        )

    @property
    def chart_of_NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['diff-%s co2 vg NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
                ...
                   \ ...
        ----------->\ NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------>\ NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, td=2
        ... ).NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-0.02322804, -0.01161402, -0.00774268, -0.00580701, -0.00464561,
                -0.00464561]])
        """
        return self.NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['diff-%s co2 vg NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],save=self.save_charts,save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )


    @ts.Cache._property
    def timed_so_diff_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
            ...
               \ ...
        ------->\ soco2_diff_flows_traj
        =========
        -------->\ timed_so_diff_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2
        ... ).timed_so_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        array([[-9.48336381e+02, -1.16020926e-05,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.soco2_diff_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_so_diff_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_diff_co2_flows_traj_values.T,
            labels=['diff-%s co2 so value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 so [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_so_diff_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
             ...
                \ ...
        -------->\ timed_so_diff_co2_flows_traj_values
        ==========
        --------->\ timed_so_diff_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2
        ... ).timed_so_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        array([[-9.48336381e+02, -1.12641675e-05,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.timed_so_diff_co2_flows_traj_values\
        *self.discounting_factors

    @property
    def chart_of_so_diff_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_diff_co2_flows_traj_disc_values.T,
            labels=['diff-%s co2 so value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 so [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_diff_co2_flows_traj(self):
        """
        Resolution order:
              ...
                 \ ...
        --------->\ timed_so_diff_co2_flows_traj_disc_values
        ===========
        ---------->\ NPV_so_diff_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2
        ... ).NPV_so_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        array([[-948.33638116, -948.33639242, -948.33639242, -948.33639242,
                -948.33639242, -948.33639242]])
        """
        return np.cumsum(
            self.timed_so_diff_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_so_diff_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_diff_co2_flows_traj.T,
            labels=['diff-%s co2 so NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 so [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_C_cum_output_flows_traj
               ...
                  \ ...
        ---------->\ NPV_so_diff_co2_flows_traj
        ============
        ----------->\ NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2
        ... ).NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        array([[-948.33638116, -474.16819621, -316.11213081, -237.08409811,
                -189.66727848, -189.66727848]])
        """
        return np.nan_to_num(
            self.NPV_so_diff_co2_flows_traj
            /self.timed_C_cum_output_flows_traj
        )

    @property
    def chart_of_NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['diff-%s co2 so NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 so [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
                ...
                   \ ...
        ----------->\ NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------>\ NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2
        ... ).NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        array([[-0.03550643, -0.01775322, -0.01183548, -0.00887661, -0.00710129,
                -0.00710129]])
        """
        return self.NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['diff-%s co2 so NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 so [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_so_plus_vg_diff_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
            ...
               \ ...
        ------->\ diff_co2_flows_traj
        =========
        -------->\ timed_so_plus_vg_diff_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).timed_so_plus_vg_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1.56873081e+03, -1.20494148e-05,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.diff_co2_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_so_plus_vg_diff_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_plus_vg_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_plus_vg_diff_co2_flows_traj_values.T,
            labels=['diff-%s co2 so+vg value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 so+vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_so_plus_vg_diff_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
             ...
                \ ...
        -------->\ timed_so_plus_vg_diff_co2_flows_traj_values
        ==========
        --------->\ timed_so_plus_vg_diff_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).timed_so_plus_vg_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1.56873081e+03, -1.16984610e-05,  0.00000000e+00,
                 0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])
        """
        return self.timed_so_plus_vg_diff_co2_flows_traj_values\
        *self.discounting_factors

    @property
    def chart_of_so_plus_vg_diff_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_plus_vg_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_plus_vg_diff_co2_flows_traj_disc_values.T,
            labels=['diff-%s co2 so+vg value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 so+vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_plus_vg_diff_co2_flows_traj(self):
        """
        Resolution order:
              ...
                 \ ...
        --------->\ timed_so_plus_vg_diff_co2_flows_traj_disc_values
        ===========
        ---------->\ NPV_so_plus_vg_diff_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).NPV_so_plus_vg_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1568.73081101, -1568.73082271, -1568.73082271, -1568.73082271,
                -1568.73082271, -1568.73082271]])
        """
        return np.cumsum(
            self.timed_so_plus_vg_diff_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_so_plus_vg_diff_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_plus_vg_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_plus_vg_diff_co2_flows_traj.T,
            labels=['diff-%s co2 so+vg NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 so+vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
                ...
                   \ ...
        ----------->\ NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj
                ...
                   \ ...
        ----------->\ NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------>\ NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1568.73081101,  -784.36541136,  -522.91027424,  -392.18270568,
                 -313.74616454,  -313.74616454]])
        """
        return self.NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj\
        + self.NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj

    @property
    def chart_of_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['diff-%s co2 so+vg NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 so+vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
                 ...
                    \ ...
        ------------>\ NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        ==============
        ------------->\ NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-0.05873447, -0.02936724, -0.01957816, -0.01468362, -0.01174689,
                -0.01174689]])
        """
        return self.NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['diff-%s co2 so+vg NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 so+vg [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )


    """**[DIFF*ALL*TIMED*CO2*FLOWS*&*VALUE]*********************************************************"""
    @ts.Cache._property
    def timed_total_diff_co2_flows_traj(self):
        """
        Resolution order:
        |-----------------------------------------|NON-ANNUALIZATION-SPECIFIC
         ...                                      |
            \ ...                                 |
        ---->\ timed_proc_input_co2eq_flows_traj  |
         ...                                      |
            \ ...                                 |
        ---->\ timed_cult_input_co2eq_flows_traj  |
              \-----------------------------------|
            ...
               \ ...
        ------->\ diff_co2_flows_traj (implicitly timed)
        =========
        -------->\ timed_total_diff_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).timed_total_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-19.07177863,  -1.92997014,  -1.92997   ,  -1.92997   ,
                 -1.92997   ,  -0.88958   ]])
        """
        return self.timed_proc_input_co2eq_flows_traj\
        + self.timed_cult_input_co2eq_flows_traj\
        + self.diff_co2_flows_traj

    @property
    def chart_of_total_diff_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_total_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_total_diff_co2_flows_traj.T,
            labels=['diff-%s total co2 flows [tonnes]'%(self.output)],
            colors=['red'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 total [diff-%s]'%(self.output),
            bar=True
        )

    @ts.Cache._property
    def timed_total_diff_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
             ...
                \ ...
        -------->\ timed_total_diff_co2_flows_traj
        ==========
        --------->\ timed_total_diff_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).timed_total_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1659.24474101,  -167.90740205,  -167.90739   ,  -167.90739   ,
                 -167.90739   ,   -77.39346   ]])
        """
        return self.timed_total_diff_co2_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_total_diff_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_total_diff_co2_flows_traj_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_total_diff_co2_flows_traj_values.T,
            labels=['diff-%s co2 total value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 total [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_total_diff_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        .
         \ ...
        ->| discounting_factors
              ...
                 \ ...
        --------->\ timed_total_diff_co2_flows_traj_values
        ===========
        ---------->\ timed_total_diff_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).timed_total_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1659.24474101,  -163.01689519,  -158.26881893,  -153.6590475 ,
                 -149.18354126,   -66.76027845]])
        """
        return self.timed_total_diff_co2_flows_traj_values\
        *self.discounting_factors

    @property
    def chart_of_total_diff_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_total_diff_co2_flows_traj_disc_values
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_total_diff_co2_flows_traj_disc_values.T,
            labels=['diff-%s co2 total value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 total [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_total_diff_co2_flows_traj(self):
        """
        Resolution order:
               ...
                  \ ...
        ---------->\ timed_total_diff_co2_flows_traj_disc_values
        ===========
        ---------->| NPV_total_diff_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).NPV_total_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1659.24474101, -1822.26163621, -1980.53045513, -2134.18950263,
                -2283.3730439 , -2350.13332235]])
        """
        return np.cumsum(
            self.timed_total_diff_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_total_diff_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_diff_co2_flows_traj.T,
            labels=['diff-%s co2 total NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 total [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
             ...
                \ ...
        -------->\ NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj
                 ...
                    \ ...
        ------------>\ NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------->\ NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1659.24474101,  -948.70045888,  -684.85849177,  -551.7903773 ,
                 -471.05856411,  -470.02666447]])
        """
        return self.NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj\
        + self.NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj

    @property
    def chart_of_NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['diff-%s co2 total NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 total [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonnes_to_MJs_computer
                  ...
                     \ ...
        ------------->\ NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj
        ==============
        -------------->\ NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=2, td=2
        ... ).NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.05488765]
        ---- [***]The solution converged.[3.552714e-15][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-0.06212338, -0.03552006, -0.02564162, -0.02065945, -0.01763679,
                -0.01759815]])
        """
        return self.NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output, 1.
        )

    @property
    def chart_of_NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['diff-%s co2 total NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 total [diff-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )


    #---------------------------------------------< UNIF >---------------------------------------------

    @ts.Cache._property
    def timed_vg_unif_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
            ...
               \ ...
        ------->\ vgco2_unif_flows_traj
        =========
        -------->\ timed_vg_unif_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, tu=2
        ... ).timed_vg_unif_co2_flows_traj_values
        array([[-310.19721515, -310.19721515,    0.        ,    0.        ,
                   0.        ,    0.        ]])
        """
        return self.vgco2_unif_flows_traj*self.co2_prices_traj

    @property
    def chart_of_vg_unif_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vg_unif_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_vg_unif_co2_flows_traj_values.T,
            labels=['unif-%s co2 vg value [%s][%s]'%(
                self.output,self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_vg_unif_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
             ...
                \ ...
        -------->\ timed_vg_unif_co2_flows_traj_values
        ==========
        --------->\ timed_vg_unif_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, tu=2
        ... ).timed_vg_unif_co2_flows_traj_disc_values
        array([[-310.19721515, -301.16234481,    0.        ,    0.        ,
                   0.        ,    0.        ]])
        """
        return self.timed_vg_unif_co2_flows_traj_values*self.discounting_factors

    @property
    def chart_of_vg_unif_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_vg_unif_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_vg_unif_co2_flows_traj_disc_values.T,
            labels=['unif-%s co2 vg value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_vg_unif_co2_flows_traj(self):
        """
        Resolution order:
              ...
                 \ ...
        --------->\ timed_vg_unif_co2_flows_traj_disc_values
        ===========
        ---------->\ NPV_vg_unif_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, tu=2
        ... ).NPV_vg_unif_co2_flows_traj
        array([[-310.19721515, -611.35955996, -611.35955996, -611.35955996,
                -611.35955996, -611.35955996]])
        """
        return np.cumsum(
            self.timed_vg_unif_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_vg_unif_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_vg_unif_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_vg_unif_co2_flows_traj.T,
            labels=['unif-%s co2 vg NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_C_cum_output_flows_traj
               ...
                  \ ...
        ---------->\ NPV_vg_unif_co2_flows_traj
        ============
        ----------->\ NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, tu=2
        ... ).NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        array([[-310.19721515, -305.67977998, -203.78651999, -152.83988999,
                -122.27191199, -122.27191199]])
        """
        return np.nan_to_num(
            self.NPV_vg_unif_co2_flows_traj\
            /self.timed_C_cum_output_flows_traj
        )

    @property
    def chart_of_NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['unif-%s co2 vg NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
                ),
            bar=False
        )

    @ts.Cache._property
    def NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
                ...
                   \ ...
        ----------->\ NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------>\ NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, tu=2
        ... ).NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[-0.01161402, -0.01144488, -0.00762992, -0.00572244, -0.00457795,
                -0.00457795]])
        """
        return self.NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(self.output, 1. )

    @property
    def chart_of_NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['unif-%s co2 vg NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_so_unif_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
            ...
               \ ...
        ------->\ soco2_unif_flows_traj
        =========
        -------->\ timed_so_unif_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3
        ... ).timed_so_unif_co2_flows_traj_values
        array([[-316.11213092, -316.11213092, -316.11213092,    0.        ,
                   0.        ,    0.        ]])
        """
        return self.soco2_unif_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_so_unif_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_unif_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_unif_co2_flows_traj_values.T,
            labels=['unif-%s co2 so value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 so [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_so_unif_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
             ...
                \ ...
        -------->\ timed_so_unif_co2_flows_traj_values
        ==========
        --------->\ timed_so_unif_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3
        ... ).timed_so_unif_co2_flows_traj_disc_values
        array([[-316.11213092, -306.90498148, -297.96600143,    0.        ,
                   0.        ,    0.        ]])
        """
        return self.timed_so_unif_co2_flows_traj_values*self.discounting_factors

    @property
    def chart_of_so_unif_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_unif_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_unif_co2_flows_traj_disc_values.T,
            labels=['unif-%s co2 so value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 so [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_unif_co2_flows_traj(self):
        """
        Resolution order:
              ...
                 \ ...
        --------->\ timed_so_unif_co2_flows_traj_disc_values
        ===========
        ---------->\ NPV_so_unif_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3
        ... ).NPV_so_unif_co2_flows_traj
        array([[-316.11213092, -623.0171124 , -920.98311383, -920.98311383,
                -920.98311383, -920.98311383]])
        """
        return np.cumsum(
            self.timed_so_unif_co2_flows_traj_disc_values, axis=1
        )

    @property
    def chart_of_NPV_so_unif_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_unif_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_unif_co2_flows_traj.T,
            labels=['unif-%s co2 so NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 so [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_C_cum_output_flows_traj
               ...
                  \ ...
        ---------->\ NPV_so_unif_co2_flows_traj
        ============
        ----------->\ NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3
        ... ).NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj
        array([[-316.11213092, -311.5085562 , -306.99437128, -230.24577846,
                -184.19662277, -184.19662277]])
        """
        return np.nan_to_num(
            self.NPV_so_unif_co2_flows_traj\
            /self.timed_C_cum_output_flows_traj
        )

    @property
    def chart_of_NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['unif-%s co2 so NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 so [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
                ...
                   \ ...
        ----------->\ NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------>\ NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3
        ... ).NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[-0.01183548, -0.01166312, -0.0114941 , -0.00862058, -0.00689646,
                -0.00689646]])
        """
        return self.NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(self.output, 1.)

    @property
    def chart_of_NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['unif-%s co2 so NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 so [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )



    @ts.Cache._property
    def timed_so_plus_vg_unif_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
            ...
               \ ...
        ------->\ unif_co2_flows_traj
        =========
        -------->\ timed_so_plus_vg_unif_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).timed_so_plus_vg_unif_co2_flows_traj_values
        array([[-626.30934607, -626.30934607, -316.11213092,    0.        ,
                   0.        ,    0.        ]])
        """
        return self.unif_co2_flows_traj*self.co2_prices_traj

    @property
    def chart_of_so_plus_vg_unif_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_plus_vg_unif_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_plus_vg_unif_co2_flows_traj_values.T,
            labels=['unif-%s co2 so+vg value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 so+vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_so_plus_vg_unif_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        ..
          \ ...
        ->| discounting_factors
             ...
                \ ...
        -------->\ timed_so_plus_vg_unif_co2_flows_traj_values
        ==========
        --------->\ timed_so_plus_vg_unif_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).timed_so_plus_vg_unif_co2_flows_traj_disc_values
        array([[-626.30934607, -608.06732628, -297.96600143,    0.        ,
                   0.        ,    0.        ]])
        """
        return self.timed_so_plus_vg_unif_co2_flows_traj_values\
        *self.discounting_factors

    @property
    def chart_of_so_plus_vg_unif_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_so_plus_vg_unif_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_so_plus_vg_unif_co2_flows_traj_disc_values.T,
            labels=['unif-%s co2 so+vg value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 so+vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_plus_vg_unif_co2_flows_traj(self):
        """
        Resolution order:
              ...
                 \ ...
        --------->\ timed_so_plus_vg_unif_co2_flows_traj_disc_values
        ===========
        ---------->\ NPV_so_plus_vg_unif_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).NPV_so_plus_vg_unif_co2_flows_traj
        array([[ -626.30934607, -1234.37667235, -1532.34267379, -1532.34267379,
                -1532.34267379, -1532.34267379]])
        """
        return np.cumsum(
            self.timed_so_plus_vg_unif_co2_flows_traj_disc_values,
            axis=1
        )

    @property
    def chart_of_NPV_so_plus_vg_unif_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_plus_vg_unif_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_plus_vg_unif_co2_flows_traj.T,
            labels=['unif-%s co2 so+vg NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 so+vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
                ...
                   \ ...
        ----------->\ NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj
                ...
                   \ ...
        ----------->\ NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------>\ NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        array([[-626.30934607, -617.18833618, -510.78089126, -383.08566845,
                -306.46853476, -306.46853476]])
        """
        return self.NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj\
        + self.NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj

    @property
    def chart_of_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['unif-%s co2 so+vg NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 so+vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonne_to_MJs
                 ...
                    \ ...
        ------------>\ NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        ==============
        ------------->\ NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[-0.0234495 , -0.023108  , -0.01912402, -0.01434302, -0.01147441,
                -0.01147441]])
        """
        return self.NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(self.output, 1. )

    @property
    def chart_of_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['unif-%s co2 so+vg NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 so+vg [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.final_landuse
            ),
            bar=False
        )


    """**[UNIF*ALL*TIMED*CO2*FLOWS*&*VALUE]*********************************************************"""
    @ts.Cache._property
    def timed_total_unif_co2_flows_traj(self):
        """
        Resolution order:
        |-----------------------------------------|NON-ANNUALIZATION-SPECIFIC
         ...                                      |
            \ ...                                 |
        ---->\ timed_proc_input_co2eq_flows_traj  |
         ...                                      |
            \ ...                                 |
        ---->\ timed_cult_input_co2eq_flows_traj  |
              \-----------------------------------|
            ...
               \ ...
        ------->\ unif_co2_flows_traj (implicitly timed)
        =========
        -------->\ timed_total_unif_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).timed_total_unif_co2_flows_traj
        array([[-8.239348  , -9.128928  , -5.56344277, -1.92997   , -1.92997   ,
                -0.88958   ]])
        """
        return self.timed_proc_input_co2eq_flows_traj\
        + self.timed_cult_input_co2eq_flows_traj\
        + self.unif_co2_flows_traj

    @property
    def chart_of_total_unif_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_total_unif_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_total_unif_co2_flows_traj.T,
            labels=['unif-%s total co2 flows [tonnes]'%(self.output)],
            colors=['red'],save=self.save_charts,save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 total [unif-%s]'%(self.output),
            bar=True
        )

    @ts.Cache._property
    def timed_total_unif_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
             ...
                \ ...
        -------->\ timed_total_unif_co2_flows_traj
        ==========
        --------->\ timed_total_unif_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).timed_total_unif_co2_flows_traj_values
        array([[-716.82327607, -794.21673607, -484.01952092, -167.90739   ,
                -167.90739   ,  -77.39346   ]])
        """
        return self.timed_total_unif_co2_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_total_unif_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_total_unif_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_total_unif_co2_flows_traj_values.T,
            labels=['unif-%s co2 total value [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 total [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_total_unif_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        .
         \ ...
        ->| discounting_factors
              ...
                 \ ...
        --------->\ timed_total_unif_co2_flows_traj_values
        ===========
        ---------->\ timed_total_unif_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).timed_total_unif_co2_flows_traj_disc_values
        array([[-716.82327607, -771.08420978, -456.23482036, -153.6590475 ,
                -149.18354126,  -66.76027845]])
        """
        return self.timed_total_unif_co2_flows_traj_values*self.discounting_factors

    @property
    def chart_of_total_unif_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_total_unif_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_total_unif_co2_flows_traj_disc_values.T,
            labels=['unif-%s co2 total value-d [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 total [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_total_unif_co2_flows_traj(self):
        """
        Resolution order:
               ...
                  \ ...
        ---------->\ timed_total_unif_co2_flows_traj_disc_values
        ===========
        ---------->| NPV_total_unif_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).NPV_total_unif_co2_flows_traj
        array([[ -716.82327607, -1487.90748585, -1944.14230621, -2097.80135371,
                -2246.98489497, -2313.74517342]])
        """
        return np.cumsum(
            self.timed_total_unif_co2_flows_traj_disc_values, axis=1
        )

    @property
    def chart_of_NPV_total_unif_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_unif_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_unif_co2_flows_traj.T,
            labels=['unif-%s co2 total NPV [%s][%s]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 total [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Resolution order:
             ...
                \ ...
        -------->\ NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj
                 ...
                    \ ...
        ------------>\ NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj
        =============
        ------------->\ NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj
        array([[-716.82327607, -781.5233837 , -672.72910879, -542.69334007,
                -463.78093432, -462.74903468]])
        """
        return self.NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj\
        + self.NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj

    @property
    def chart_of_NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj.T,
            labels=['unif-%s co2 total NPV [%s][%s/TONNE]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 total [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Resolution order:

        >| tonnes_to_MJs_computer
                  ...
                     \ ...
        ------------->\ NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj
        ==============
        -------------->\ NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=5, ts=3, tu=2
        ... ).NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        array([[-0.02683841, -0.02926083, -0.02518749, -0.02031885, -0.01736431,
                -0.01732567]])
        """
        return self.NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj\
        /self.output_flows_traj_converter.tonnes_to_MJs_computer(self.output, 1.)

    @property
    def chart_of_NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj.T,
            labels=['unif-%s co2 total NPV [%s][%s/MJ]'%(
                self.output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 total [unif-%s-%s]'%(
                self.co2_prices_scenario,
                self.output
            ),
            bar=False
        )


    """**[BLACK*OUTPUT*CO2*FLOWS*&*VALUE]***********************************************************"""
    @ts.Cache._property
    def output_flows_traj_converter(self):
        """ Instantiated class-like object whose methodes and properties will
        be used for conversions to equivalent "black output" flows of the
        scenarized trajectory of "green output" flows.

        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(ph=0)
        >>> type(o.output_flows_traj_converter)
        <class '__main__.BlackOutputAndSubstitutesSpecificities'>
        """
        return BlackOutputAndSubstitutesSpecificities()

    @ts.Cache._property
    def output_MJs_flows_traj(self):
        """
        Resolution order:
        ..
          \ ...
        -->| output_flows_traj
        ===
        --->\ output_MJs_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).output_MJs_flows_traj
        array([[26708.86076, 26708.86076, 26708.86076, 26708.86076, 26708.86076]])
        """
        return self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output,self.output_flows_traj
        )

    @ts.Cache._property
    def timed_output_MJs_flows_traj(self):
        """
        Resolution order:
        ..
          \ ...
        -->| timed_output_flows_traj
        ===
        --->\ timed_output_MJs_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).timed_output_MJs_flows_traj
        array([[    0.     , 26708.86076, 26708.86076, 26708.86076, 26708.86076]])
        """
        return self.output_flows_traj_converter.tonnes_to_MJs_computer(
            self.output,self.timed_output_flows_traj
        )

    @ts.Cache._property
    def timed_black_output_flows_traj(self):
        """
        Tonnes of "black output" implicitly involved to produce such a quantity of MJs
        Resolution order:
        ...
           \ ...
        --->| timed_output_MJs_flows_traj
        ====
        ---->\ timed_black_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).timed_black_output_flows_traj
        array([[0.        , 0.58683364, 0.58683364, 0.58683364, 0.58683364]])
        """
        return self.output_flows_traj_converter.MJs_to_tonnes_computer(
            self.black_output,
            self.timed_output_MJs_flows_traj
        )

    @ts.Cache._property
    def cum_black_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_black_output_flows_traj
        =====
        ---->| cum_black_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).cum_black_output_flows_traj
        array([[0.        , 0.58683364, 1.17366728, 1.76050092, 2.34733456]])
        """
        return np.cumsum(self.timed_black_output_flows_traj, axis=1)

    @ts.Cache._property
    def cum_MJs_black_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ timed_output_MJs_flows_traj
        =====
        ---->| cum_MJs_black_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).cum_MJs_black_output_flows_traj
        array([[     0.     ,  26708.86076,  53417.72152,  80126.58228,
                106835.44304]])
        """
        return np.cumsum(self.timed_output_MJs_flows_traj, axis=1)

    @property
    def chart_of_black_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_black_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_black_output_flows_traj.T,
            labels=['%s %s flows [tonnes]'%(
                self.black_output,
                self.output_flows_scenario
            )],
            colors=['blue'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES %s [%s]'%(
                self.black_output,
                self.output_flows_scenario
            ),
            bar=True
        )

    @ts.Cache._property
    def black_output_co2eq_flows_traj(self):
        """
        Resolution order:

        >| co2eq_yields_GWP_traj_computer({'CO2':1., 'N2O':.0, 'CH4':.0})
        ...
           \ ...
        --->\ output_MJs_flows_traj
        ====
        ---->\ black_output_co2eq_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).black_output_co2eq_flows_traj
        array([[-2.33168354, -2.33168354, -2.33168354, -2.33168354, -2.33168354]])
        """
        return self.output_flows_traj_converter.co2eq_emissions_per_MJ[self.black_output]\
        *self.output_MJs_flows_traj\
        *ts.dict_time_serie_as_row_array(
            self.co2eq_computer.co2eq_yields_GWP_traj_computer(
                {'CO2':1., 'N2O':.0, 'CH4':.0}
            )
        )

    @ts.Cache._property
    def timed_black_output_co2eq_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->\ black_output_co2eq_flows_traj
        =====
        ----->\ timed_black_output_co2eq_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).timed_black_output_co2eq_flows_traj
        array([[ 0.        , -2.33168354, -2.33168354, -2.33168354, -2.33168354]])
        """
        _D_ = self.project_timing
        return np.hstack((
            np.zeros((1, _D_)),
            self.black_output_co2eq_flows_traj
        ))[:, :(-_D_ if _D_ else None)]

    @property
    def chart_of_black_output_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_black_output_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_black_output_co2eq_flows_traj.T,
            labels=['%s co2 total flows [tonnes]'%self.black_output],
            colors=['red'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='FLOWS TONNES co2 total [%s]'%(self.black_output),
            bar=True
        )

    @ts.Cache._property
    def timed_black_output_co2_flows_traj_values(self):
        """
        Resolution order:
        ..
          \ ...
        -->| co2_prices_traj
          ...
             \ ...
        ----->\ timed_black_output_co2eq_flows_traj
        ======
        ------>\ timed_black_output_co2_flows_traj_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).timed_black_output_co2_flows_traj_values
        array([[   0.        , -202.85646836, -202.85646836, -202.85646836,
                -202.85646836]])
        """
        return self.timed_black_output_co2eq_flows_traj\
        *self.co2_prices_traj

    @property
    def chart_of_black_output_co2_flows_traj_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_black_output_co2_flows_traj_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_black_output_co2_flows_traj_values.T,
            labels=['%s co2 total value [%s][%s]'%(
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['darkred'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE co2 total [%s-%s]'%(
                self.co2_prices_scenario,
                self.black_output
            ),
            bar=False
        )

    @ts.Cache._property
    def timed_black_output_co2_flows_traj_disc_values(self):
        """
        Resolution order:
        .
         \ ...
        ->| discounting_factors
           ...
              \ ...
        ------>\ timed_black_output_co2_flows_traj_values
        =======
        ------->\ timed_black_output_co2_flows_traj_disc_values

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).timed_black_output_co2_flows_traj_disc_values
        array([[   0.        , -196.94802753, -191.21167722, -185.64240506,
                -180.23534472]])
        """
        return self.timed_black_output_co2_flows_traj_values*self.discounting_factors

    @property
    def chart_of_black_output_co2_flows_traj_disc_values(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_black_output_co2_flows_traj_disc_values
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.timed_black_output_co2_flows_traj_disc_values.T,
            labels=['%s co2 total value-d [%s][%s]'%(
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='VALUE-D co2 total [%s-%s]'%(
                self.co2_prices_scenario,
                self.black_output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_black_output_co2_flows_traj(self):
        """
        Resolution order:
            ...
               \ ...
        ------->\ timed_black_output_co2_flows_traj_disc_values
        ========
        ------->| NPV_black_output_co2_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).NPV_black_output_co2_flows_traj
        array([[   0.        , -196.94802753, -388.15970475, -573.80210981,
                -754.03745453]])
        """
        return np.cumsum(
            self.timed_black_output_co2_flows_traj_disc_values, axis=1
        )

    @property
    def chart_of_NPV_black_output_co2_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_black_output_co2_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_black_output_co2_flows_traj.T,
            labels=['%s co2 total NPV [%s][%s]'%(
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV co2 total [%s-%s]'%(
                self.co2_prices_scenario,
                self.black_output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->| cum_black_output_flows_traj
            ...
               \ ...
        ------->| NPV_black_output_co2_flows_traj
        ========
        -------->\ NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj
        array([[   0.        , -335.61134608, -330.7238022 , -325.93116209,
                -321.23135261]])
        """
        return np.nan_to_num(
            self.NPV_black_output_co2_flows_traj\
            /self.cum_black_output_flows_traj
        )
    
    @property
    def chart_of_NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj.T,
            labels=['%s co2 total NPV [%s][%s/TONNE]'%(
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary co2 total [%s-%s]'%(
                self.co2_prices_scenario,
                self.black_output
            ),
            bar=False
        )

    @ts.Cache._property
    def NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj(self):
        """
        Resolution order:
         ...
            \ ...
        ---->| cum_MJs_black_output_flows_traj
            ...
               \ ...
        ------->| NPV_black_output_co2_flows_traj
        ========
        -------->\ NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4
        ... ).NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj
        array([[ 0.        , -0.00737388, -0.0072665 , -0.0071612 , -0.00705793]])
        """
        return np.nan_to_num(
            self.NPV_black_output_co2_flows_traj\
            /self.cum_MJs_black_output_flows_traj
        )

    @property
    def chart_of_NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj.T,
            labels=['%s co2 total NPV [%s][%s/MJ]'%(
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['green'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='NPV-unitary-MJ co2 total [%s-%s]'%(
                self.co2_prices_scenario,
                self.black_output
            ),
            bar=False
        )



    """**[PAYBACK*RELATED-OBJECTS]******************************************************************"""
    @ts.Cache._property
    def NPV_total_diff_minus_black_output_co2_flows_trajs(self):
        """
        Resolution order:
               ...
                  \ ...
        ---------->\ NPV_total_diff_co2_flows_traj
               ...
                  \ ...
        ---------->\ NPV_black_output_co2_flows_traj
        ===========
        ---------->| NPV_total_diff_minus_black_output_co2_flows_trajs

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4, ts=3, td=2
        ... ).NPV_total_diff_minus_black_output_co2_flows_trajs
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.0613595]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.04750517]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([[-1659.24467335, -1625.3136067 , -1592.37074841, -1560.38739085,
                -1448.91513293]])
        """
        return self.NPV_total_diff_co2_flows_traj\
        - self.NPV_black_output_co2_flows_traj
    
    @property
    def chart_of_NPV_total_diff_minus_black_output_co2_flows_trajs(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_diff_minus_black_output_co2_flows_trajs
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_diff_minus_black_output_co2_flows_trajs.T,
            labels=['DIFF %s minus %s NPVs [%s][%s]'%(
                self.output,
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['orange'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='dNPV co2 total [diff-%s-%svs%s]'%(
                self.co2_prices_scenario,
                self.output,
                self.black_output
            ),
            bar=False
        )

    @ts.Cache._property
    def diff_payback_period(self):
        """ Time required for the "green" project to become more profitable
        than its black counterpart when co2 flows are differentiated.

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=60, sc='WEO2015-CPS'
        ... ).diff_payback_period
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        45
        """
        s_ = np.sign(self.NPV_total_diff_minus_black_output_co2_flows_trajs)
        s  = ((np.roll(s_, 1) - s_) != 0).astype(int) 
        z  = np.where(s.flatten()==1)[0]
        return z[1] if len(z) else []

    @ts.Cache._property
    def NPV_total_unif_minus_black_output_co2_flows_trajs(self):
        """
        Resolution order:
               ...
                  \ ...
        ---------->\ NPV_total_unif_co2_flows_traj
               ...
                  \ ...
        ---------->\ NPV_black_output_co2_flows_traj
        ===========
        ---------->| NPV_total_unif_minus_black_output_co2_flows_trajs

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=4, ts=3, tu=2
        ... ).NPV_total_unif_minus_black_output_co2_flows_trajs
        array([[ -716.82327607, -1290.95945832, -1555.98260146, -1523.9992439 ,
                -1412.52698598]])
        """
        return self.NPV_total_unif_co2_flows_traj\
        - self.NPV_black_output_co2_flows_traj
    
    @property
    def chart_of_NPV_total_unif_minus_black_output_co2_flows_trajs(self):
        """
        Testing/Example
        ---------------
        >>> o = CBACalculator._testing_instancer(
        ...     rn='.doctests', return_charts=True
        ... )
        >>> c = o.chart_of_NPV_total_unif_minus_black_output_co2_flows_trajs
        >>> c.show()  # doctest: +SKIP
        >>> c.close()
        """
        return self.dashboard.plot(
            abs_=self.horizon,
            imas=self.NPV_total_unif_minus_black_output_co2_flows_trajs.T,
            labels=['UNIF %s minus %s NPVs [%s][%s]'%(
                self.output,
                self.black_output,
                self.co2_prices_scenario,
                self.final_currency
            )],
            colors=['orange'],
            save=self.save_charts,
            save_dir=self.save_dir,
            file_name='dNPV co2 total [unif-%s-%svs%s]'%(
                self.co2_prices_scenario,
                self.output,
                self.black_output
            ),
            bar=False
        )

    @ts.Cache._property
    def unif_payback_period(self):
        """ Time required for the "green" project to become more profitable
        than its black counterpart when co2 flows are uniforme.

        Testing/Example
        ---------------
        >>> CBACalculator._testing_instancer(
        ...     ph=60, sc='WEO2015-CPS'
        ... ).unif_payback_period
        49
        """
        s_ = np.sign(self.NPV_total_unif_minus_black_output_co2_flows_trajs)
        s  = ((np.roll(s_, 1) - s_) != 0).astype(int) 
        z  = np.where(s.flatten()==1)[0]
        return z[1] if len(z) else []


    """**[FINALIZE]*********************************************************************************"""
    @ts.Cache._property
    def all_XLSXed(self):
        """ XLSX file of all computed data, stored in `self.save_dir`."""
        q_listed_content = [
            self.horizon,
            self.economic_horizon,

            self.soc_unif_flows_traj,
            self.soc_diff_flows_traj,
            self.vgc_unif_flows_traj,
            self.vgc_diff_flows_traj,
            self.unif_carbon_flows_traj,
            self.diff_carbon_flows_traj,

            self.soco2_unif_flows_traj,
            self.soco2_diff_flows_traj,
            self.vgco2_unif_flows_traj,
            self.vgco2_diff_flows_traj,#@@Q#
            self.unif_co2_flows_traj,
            self.diff_co2_flows_traj,

            self.timed_cult_input_co2eq_flows_traj,
            self.timed_proc_input_co2eq_flows_traj,
            self.timed_output_flows_traj,
            self.timed_output_MJs_flows_traj,
            self.timed_black_output_flows_traj,
            self.timed_input_flows_traj,
            self.timed_land_surface_flows_traj,

            self.timed_total_diff_co2_flows_traj,
            self.timed_total_unif_co2_flows_traj,
            self.timed_black_output_co2eq_flows_traj,
        ]
        v_listed_content = [
            self.horizon,
            self.economic_horizon,

            self.co2_prices_traj,
            self.timed_cult_co2_flows_traj_values,
            self.timed_proc_co2_flows_traj_values,
            self.timed_proc_plus_cult_co2_flows_traj_values,

            self.timed_so_diff_co2_flows_traj_values,
            self.timed_vg_diff_co2_flows_traj_values,
            self.timed_so_plus_vg_diff_co2_flows_traj_values,

            self.timed_so_unif_co2_flows_traj_values,
            self.timed_vg_unif_co2_flows_traj_values,
            self.timed_so_plus_vg_unif_co2_flows_traj_values,

            self.timed_total_diff_co2_flows_traj_values,
            self.timed_total_unif_co2_flows_traj_values,
            self.timed_black_output_co2_flows_traj_values,

            self.discounting_factors,#@@V#

            self.co2_disc_prices_traj,
            self.timed_cult_co2_flows_traj_disc_values,
            self.timed_proc_co2_flows_traj_disc_values,
            self.timed_proc_plus_cult_co2_flows_traj_disc_values,

            self.timed_so_diff_co2_flows_traj_disc_values,
            self.timed_vg_diff_co2_flows_traj_disc_values,
            self.timed_so_plus_vg_diff_co2_flows_traj_disc_values,

            self.timed_so_unif_co2_flows_traj_disc_values,
            self.timed_vg_unif_co2_flows_traj_disc_values,
            self.timed_so_plus_vg_unif_co2_flows_traj_disc_values,

            self.timed_total_diff_co2_flows_traj_disc_values,
            self.timed_total_unif_co2_flows_traj_disc_values,
            self.timed_black_output_co2_flows_traj_disc_values,
        ]
        n_listed_content = [
            self.horizon,
            self.economic_horizon,

            self.NPV_cult_co2_flows_traj,
            self.NPV_proc_co2_flows_traj,
            self.NPV_proc_plus_cult_co2_flows_traj,

            self.NPV_so_diff_co2_flows_traj,
            self.NPV_vg_diff_co2_flows_traj,
            self.NPV_so_plus_vg_diff_co2_flows_traj,

            self.NPV_so_unif_co2_flows_traj,
            self.NPV_vg_unif_co2_flows_traj,
            self.NPV_so_plus_vg_unif_co2_flows_traj,

            self.NPV_total_diff_co2_flows_traj,
            self.NPV_total_unif_co2_flows_traj,
            self.NPV_black_output_co2_flows_traj,
            self.NPV_total_diff_minus_black_output_co2_flows_trajs,
            self.NPV_total_unif_minus_black_output_co2_flows_trajs,

            self.NPV_cult_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_proc_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj,

            self.NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj,    #@@N#

            self.NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj,

            self.NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj,
            self.NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj,

            self.NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj,

            self.NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj,

            self.NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj,

            self.NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj,
            self.NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj,
        ]
        q_content_heads   = [
            'horizon',
            'economic_horizon',

            'soc_unif_flows_traj',
            'soc_diff_flows_traj',
            'vgc_unif_flows_traj',
            'vgc_diff_flows_traj',
            'unif_carbon_flows_traj',
            'diff_carbon_flows_traj',

            'soco2_unif_flows_traj',
            'soco2_diff_flows_traj',
            'vgco2_unif_flows_traj',
            'vgco2_diff_flows_traj',#@@Q#
            'unif_co2_flows_traj',
            'diff_co2_flows_traj',

            'timed_cult_input_co2eq_flows_traj',
            'timed_proc_input_co2eq_flows_traj',
            'timed_output_flows_traj',
            'timed_output_MJs_flows_traj',
            'timed_black_output_flows_traj',
            'timed_input_flows_traj',
            'timed_land_surface_flows_traj',

            'timed_total_diff_co2_flows_traj',
            'timed_total_unif_co2_flows_traj',
            'timed_black_output_co2eq_flows_traj',
        ]
        v_content_heads = [
            'horizon',
            'economic_horizon',

            'co2_prices_traj',
            'timed_cult_co2_flows_traj_values',
            'timed_proc_co2_flows_traj_values',
            'timed_proc_plus_cult_co2_flows_traj_values',

            'timed_so_diff_co2_flows_traj_values',
            'timed_vg_diff_co2_flows_traj_values',
            'timed_so_plus_vg_diff_co2_flows_traj_values',

            'timed_so_unif_co2_flows_traj_values',
            'timed_vg_unif_co2_flows_traj_values',
            'timed_so_plus_vg_unif_co2_flows_traj_values',

            'timed_total_diff_co2_flows_traj_values',
            'timed_total_unif_co2_flows_traj_values',
            'timed_black_output_co2_flows_traj_values',

            'discounting_factors',  #@@V#

            'co2_disc_prices_traj',
            'timed_cult_co2_flows_traj_disc_values',
            'timed_proc_co2_flows_traj_disc_values',
            'timed_proc_plus_cult_co2_flows_traj_disc_values',

            'timed_so_diff_co2_flows_traj_disc_values',
            'timed_vg_diff_co2_flows_traj_disc_values',
            'timed_so_plus_vg_diff_co2_flows_traj_disc_values',

            'timed_so_unif_co2_flows_traj_disc_values',
            'timed_vg_unif_co2_flows_traj_disc_values',
            'timed_so_plus_vg_unif_co2_flows_traj_disc_values',

            'timed_total_diff_co2_flows_traj_disc_values',
            'timed_total_unif_co2_flows_traj_disc_values',
            'timed_black_output_co2_flows_traj_disc_values',
        ]
        n_content_heads = [
            'horizon',
            'economic_horizon',

            'NPV_cult_co2_flows_traj',
            'NPV_proc_co2_flows_traj',
            'NPV_proc_plus_cult_co2_flows_traj',

            'NPV_so_diff_co2_flows_traj',
            'NPV_vg_diff_co2_flows_traj',
            'NPV_so_plus_vg_diff_co2_flows_traj',

            'NPV_so_unif_co2_flows_traj',
            'NPV_vg_unif_co2_flows_traj',
            'NPV_so_plus_vg_unif_co2_flows_traj',

            'NPV_total_diff_co2_flows_traj',
            'NPV_total_unif_co2_flows_traj',
            'NPV_black_output_co2_flows_traj',
            'NPV_total_diff_minus_black_output_co2_flows_trajs',
            'NPV_total_unif_minus_black_output_co2_flows_trajs',

            'ut_NPV_cult_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_proc_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj',

            'ut_NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj',#@@N#

            'ut_NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj',

            'ut_NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj',
            'ut_NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj',

            'um_NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj',

            'um_NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',

            'um_NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',

            'um_NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
            'um_NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj',
        ]

        ts.xlsx_file_writer(
            [q_content_heads] + np.vstack(q_listed_content).T.tolist(),
            save_dir=self.save_dir,
            file_name='_quantities'
        )
        ts.xlsx_file_writer(
            [v_content_heads] + np.vstack(v_listed_content).T.tolist(),
            save_dir=self.save_dir,
            file_name='_values'
        )
        ts.xlsx_file_writer(
            [n_content_heads] + np.vstack(n_listed_content).T.tolist(),
            save_dir=self.save_dir,
            file_name='_NPVs'
        )

        print('xlsx files saved in {}'.format(
            os.path.abspath(self.save_dir)
        ))
        return True

    @ts.Cache._property
    def all_charts(self):
        """ Charts of computed data, stored in `self.save_dir`."""
        nb_keys = len(self._charts_keys)
        for i, ckey in enumerate(self._charts_keys):
            getattr(self, ckey)
            if i%2 == 0:
                print("Rendering all charts: {0:.2f}%".format(
                    100.*(i + 1)/nb_keys)
                )
        return True
    
    _charts_keys = [
        'chart_of_NPV_black_output_co2_flows_traj',
        'chart_of_NPV_black_output_co2_flows_traj_per_cum_MJs_black_output_flows_traj',
        'chart_of_NPV_black_output_co2_flows_traj_per_cum_black_output_flows_traj',
        'chart_of_NPV_cult_co2_flows_traj',
        'chart_of_NPV_cult_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_cult_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_proc_co2_flows_traj',
        'chart_of_NPV_proc_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_proc_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_proc_plus_cult_co2_flows_traj',
        'chart_of_NPV_proc_plus_cult_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_proc_plus_cult_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_so_diff_co2_flows_traj',
        'chart_of_NPV_so_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_so_diff_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_so_plus_vg_diff_co2_flows_traj',
        'chart_of_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_so_plus_vg_diff_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_so_plus_vg_unif_co2_flows_traj',
        'chart_of_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_so_plus_vg_unif_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_so_unif_co2_flows_traj',
        'chart_of_NPV_so_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_so_unif_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_total_diff_co2_flows_traj',
        'chart_of_NPV_total_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_total_diff_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_total_diff_minus_black_output_co2_flows_trajs',
        'chart_of_NPV_total_unif_co2_flows_traj',
        'chart_of_NPV_total_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_total_unif_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_total_unif_minus_black_output_co2_flows_trajs',
        'chart_of_NPV_vg_diff_co2_flows_traj',
        'chart_of_NPV_vg_diff_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_vg_diff_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_NPV_vg_unif_co2_flows_traj',
        'chart_of_NPV_vg_unif_co2_flows_traj_per_cum_MJs_output_flows_traj',
        'chart_of_NPV_vg_unif_co2_flows_traj_per_cum_output_flows_traj',
        'chart_of_black_output_co2_flows_traj',
        'chart_of_black_output_co2_flows_traj_disc_values',
        'chart_of_black_output_co2_flows_traj_values',
        'chart_of_black_output_flows_traj',
        'chart_of_co2_disc_prices_traj',
        'chart_of_co2_prices_traj',
        'chart_of_cult_co2_flows_traj_disc_values',
        'chart_of_cult_co2_flows_traj_values',
        'chart_of_cult_input_co2eq_flows_traj',
        'chart_of_cult_unit_input_co2eq_flows_traj',
        'chart_of_diff_carbon_flows_traj',
        'chart_of_diff_co2_flows_traj',
        'chart_of_input_flows_traj',
        'chart_of_land_surface_flows_traj',
        'chart_of_output_flows_traj',
        'chart_of_proc_co2_flows_traj_disc_values',
        'chart_of_proc_co2_flows_traj_values',
        'chart_of_proc_plus_cult_co2_flows_traj_disc_values',
        'chart_of_proc_plus_cult_co2_flows_traj_values',
        'chart_of_proc_input_co2eq_flows_traj',
        'chart_of_proc_unit_input_co2eq_flows_traj',
        'chart_of_so_diff_co2_flows_traj_disc_values',
        'chart_of_so_diff_co2_flows_traj_values',
        'chart_of_so_plus_vg_diff_co2_flows_traj_disc_values',
        'chart_of_so_plus_vg_diff_co2_flows_traj_values',
        'chart_of_so_plus_vg_unif_co2_flows_traj_disc_values',
        'chart_of_so_plus_vg_unif_co2_flows_traj_values',
        'chart_of_so_unif_co2_flows_traj_disc_values',
        'chart_of_so_unif_co2_flows_traj_values',
        'chart_of_soc_diff_flows_traj',
        'chart_of_soc_unif_flows_traj',
        'chart_of_soc_unit_diff_flows_traj',
        'chart_of_soc_unit_unif_flows_traj',
        'chart_of_soco2_diff_flows_traj',
        'chart_of_soco2_unif_flows_traj',
        'chart_of_total_diff_co2_flows_traj',
        'chart_of_total_diff_co2_flows_traj_disc_values',
        'chart_of_total_diff_co2_flows_traj_values',
        'chart_of_total_unif_co2_flows_traj',
        'chart_of_total_unif_co2_flows_traj_disc_values',
        'chart_of_total_unif_co2_flows_traj_values',
        'chart_of_unif_carbon_flows_traj',
        'chart_of_unif_co2_flows_traj',
        'chart_of_vg_diff_co2_flows_traj_disc_values',
        'chart_of_vg_diff_co2_flows_traj_values',
        'chart_of_vg_unif_co2_flows_traj_disc_values',
        'chart_of_vg_unif_co2_flows_traj_values',
        'chart_of_vgc_diff_flows_traj',
        'chart_of_vgc_unif_flows_traj',
        'chart_of_vgco2_diff_flows_traj',
        'chart_of_vgco2_unif_flows_traj',
    ]


##******************************************
##    ╔═╗╔╗ ╔═╗╔═╗┌─┐┬─┐┌─┐┌┬┐┌─┐┌┬┐┌─┐┬─┐┌─┐╔═╗┌┐┌┌┬┐┌─┐┌─┐┌─┐┌┐┌┬┌─┐┌─┐┬─┐
##    ║  ╠╩╗╠═╣╠═╝├─┤├┬┘├─┤│││├┤  │ ├┤ ├┬┘└─┐║╣ │││ │││ ││ ┬├┤ ││││┌─┘├┤ ├┬┘
##    ╚═╝╚═╝╩ ╩╩  ┴ ┴┴└─┴ ┴┴ ┴└─┘ ┴ └─┘┴└─└─┘╚═╝┘└┘─┴┘└─┘└─┘└─┘┘└┘┴└─┘└─┘┴└─
class CBAParametersEndogenizer(object):
    """ Class object designed to handle a CBACalculator instances and to
    endogenize some of its parameters."""

    def __init__(self, CBACalculator_instance):
        self._CBAcI          = copy.copy(CBACalculator_instance)
        self._CBAcI._cache   = CBACalculator_instance._cache.copy()
        self._caches_cleaner = lambda k:(
            self._CBAcI._cache.pop(k, None)
            if k.split('_')[-1] not in [
                'annualizer', 'computer'
            ] else None
        )

    def _ENDOGENIZER(self, _key_, _method_, _ci_):
        """ Generic method used to wrapp the solving phase."""
        return ts.solver_ND(
            VERBOSE_SOLVER, _key_, _method_, _ci_, bforce=False, msg=True
        )

    """**[OBJECTIVES]******************************************************************************"""
    @property
    def OBJECTIVE_NPV_total_unif_co2_flows_traj_VS_NPV_total_diff_co2_flows_traj(self):
        """ Method which computes the objective of the discount rate
        endogenizing process.

        Testing/Example
        ---------------
        >>> _dr_ = 0.03847487575799428 ## the solution
        >>> cba = CBACalculator._testing_instancer(
        ...     dr = _dr_, 
        ...     sc = 'WEO2015-CPS',
        ... )
        >>> CBAParametersEndogenizer(
        ...     CBACalculator_instance = cba
        ... ).OBJECTIVE_NPV_total_unif_co2_flows_traj_VS_NPV_total_diff_co2_flows_traj
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        array([2.22044605e-16])
        """
        return -1. + self._CBAcI.NPV_total_unif_co2_flows_traj[:,-1]\
        /self._CBAcI.NPV_total_diff_co2_flows_traj[:,-1]

    """**[DISCOUNT*RATE]***************************************************************************"""
    def _ENDOGENIZER_of_the_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj(self, _disc_rate_):
        """ Semi-private method used by the solver when endogenizing the discount rate."""
        self._CBAcI.discount_rate = _disc_rate_

        for key in list(self._CBAcI._cache):
            self._caches_cleaner(key)

        self._CBAcI._cache['endogenizing'] = True

        _obj_ = self.OBJECTIVE_NPV_total_unif_co2_flows_traj_VS_NPV_total_diff_co2_flows_traj

        return _obj_ + pow(_obj_, 3.) - pow(_obj_, 3.)

    @property
    def endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj(self):
        """
        Returns a CBACalculator instance configured with the discount rate
        which equates NPV_total_unif_co2_flows_traj TO NPV_total_diff_co2_flows_traj.

        Testing/Example
        ---------------
        >>> cba = CBACalculator._testing_instancer(
        ...     sc = 'WEO2015-CPS',
        ... )
        >>> o = CBAParametersEndogenizer(
        ...     CBACalculator_instance = cba
        ... )
        >>> o.endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj.discount_rate[0]
        ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
        ---- [***]The solution converged.[0.000000e+00][***]
        ---- disc rate equating unif- and diff-based NPVs sol=[0.03847488]
        ---- [***]The solution converged.[2.220446e-16][***]
        0.038474875757994256
        """
        _S_ = self._ENDOGENIZER(
            _key_   = 'disc rate equating unif- and diff-based NPVs',
            _method_= self._ENDOGENIZER_of_the_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj,
            _ci_    = [.0]
        )
        self._CBAcI.discount_rate = _S_
        self._CBAcI.msg = '_ENDOGENIZER finally says sol=%s \n\t\t\t  obj(sol)=%s'%(
            self._CBAcI.discount_rate[0],
            self.OBJECTIVE_NPV_total_unif_co2_flows_traj_VS_NPV_total_diff_co2_flows_traj
        )
        return self._CBAcI


if __name__ == '__main__':
    import doctest
    np.set_printoptions(
        precision = 8,
        suppress  = False,
        linewidth = 75,
    )
    doctest.testmod(verbose=VERBOSE_DTESTS)
