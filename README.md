# PyLUCCBA

<details>
    <summary>A Land-Use-Change Cost-Benefit-Analysis calculator coded in Python.</summary>
</details>
    
*This package offers a compilation of environmental and economic data to generate environment-related net present values of any project with impacts to the environment (GHG emissions or sequestrations). It is coded in Python (compatible with both versions: 2 and 3). Python is a cross platform and a comprehensive extensible and editable language with a large community of users. The structure of the package is simple with accessible input data to which it is possible to add or suppress one’s own trajectories (of prices, carbon stocks, etc).*

<hr>

- [Installation](#installation)
- [Example usage](#example-usage)
    - [A note on the carbon profitability payback period](#a-note-on-the-carbon-profitability-payback-period)
    - [A note on the compensatory rate](#a-note-on-the-compensatory-rate)
- [Invoking documentation](#invoking-documentation)
- [Data](#data)
- [Data customization/addition](#data-customizationaddition)
- [Format of results](#format-of-results)
- [Paper's results replication](#papers-results-replication)
- [References](#references)
- [Code coverage](#code-coverage)

<hr>

## Installation

First, you need Python installed, either [Python2.7.+](https://www.python.org/downloads/) or [Python3.+](https://www.python.org/downloads/). Either versions are good for our purpose. Then, we are going to use a package management system to install [PyLUCCBA](https://github.com/lfaucheux/PyLUCCBA), namely [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)), _already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4_. Open a session in your OS [shell](https://en.wikipedia.org/wiki/Shell_(computing)) prompt and type

    pip install pyluccba

Or using a non-python-builtin approach, namely [git](https://git-scm.com/downloads),

    git clone git://github.com/lfaucheux/PyLUCCBA.git
    cd PyLUCCBA
    python setup.py install 


<hr>

## Example usage
    
*The example that follows is done with the idea of showing how to go beyond the replication of the results presented in [Dupoux (2018)](https://github.com/lfaucheux/PyLUCCBA/raw/master/Dupoux_Sept2018.pdf) via the Python Shell*.

Let's first import the module `PyLUCCBA`

    >>> import PyLUCCBA as cc

The alias of `PyLUCCBA`, namely `cc`, actually contains many objects definitions, such as that of the calculator that we are going to use in examples. The name of the calculator is `CBACalculator`.

But before using the calculator as such, let's define (and introduce) the set of parameters that we are going to use to configure `CBACalculator`. As can be expected when performing a cost benefit analysis, these parameters are related to: *(i)* the horizon of the project, *(ii)* the discount rate that we want to use in our calculations, *(iii)* the scenarized price trajectory of carbon dioxide (CO2), *(iv)* the scenarized trajectory of quantities of bio-ethanol to produce annually and *(...)* so on. Let's introduce them all in practice:

    >>> cba = cc.CBACalculator(
            run_name               = 'Example-1',
            country                = 'france',
            project_first_year     = 2020,
            project_horizon        = 20,
            discount_rate          = .03,
            co2_prices_scenario    = 'SPC',
            output_flows_scenario  = 'O',
            initial_landuse        = 'improved grassland',
            final_landuse          = 'wheat',
            input_flows_scenario   = 'IFP',
            T_so                   = 20,
            T_vg_diff              = 1,
            T_vg_unif              = 20,
            polat_repeated_pattern = True,
            final_currency         = 'EUR',
            change_rates           = {'EUR':{'USD/EUR':1.14}}, # https://www.google.fr/#q=EUR+USD
            return_plts            = True,
            from_local_data        = False,
        )

The following table enumerates all parameters that can be used to create an instance of `CBACalculator`.

 Parameter's name         | Description
 ------------------------ | -------
 `run_name`               | name of the folder that will contain the generated results and charts, *e.g.* `'Example-1'`.
 `country`                | name of the country under study. Only *one* possible choice currently: `France`.
 `project_first_year`     | first year of the project.
 `project_horizon`        | duration of the biofuel production project (years).
 `discount_rate`          | rate involved in the calculations of net present values. Set to `0.` by default.
 `co2_prices_scenario`    | name of the trajectory of CO2 prices. The current choices are `'A'`, `'B'`, `'C'`, `'DEBUG'`, `'O'`, `'SPC'`, `'WEO2015-450S'`, `'WEO2015-CPS'` or `'WEO2015-NPS'`.
 `output`                 | name of the produced biofuel. Set to `'eth'` by default. Only *one* possible choice currently: `'eth'`. ***NB***: `'eth'` actually stands for **bio**ethanol.
 `black_output`           | name of the counterfactual produced output. Serves as the reference according to which the production of bioethanol (`'eth'`) is considered (or not) as pro-environmental. Set to `'oil'` by default. Only *one* possible choice currently: `'oil'`. ***NB***: `'oil'` actually stands for gasoline.
 `output_flows_scenario`  | name of the trajectory of annually produced quantities of biofuel. The current choices are `'DEBUG'` or `'O'`.
 `initial_landuse`        | use of the land *before* land conversion. The current choices are `'forestland30'`, `'improved grassland'`, `'annual cropland'` or `'degraded grassland'`.
 `final_landuse`          | use of the land *after* land conversion. The current choices are `'miscanthus'`, `'sugarbeet'` or `'wheat'`.
 `input_flows_scenario`   | name of the trajectory of input-to-ouput yields. The current choices depend on the value set for `final_landuse`. If `final_landuse` is set to `'miscanthus'`, the possibilities are `'DEBUG'` and `'DOE'`. If `final_landuse` is set to `'wheat'` or `'sugarbeet'`, the possibilities are `'IFP'` and `'DEBUG'`.
 `T_so`                   | period over which soil carbon emissions due to LUC are considered.
 `T_vg_diff`              | period over which vegetation carbon emissions due to LUC are considered in the differentiated annualization approach.
 `T_vg_unif`              | period over which vegetation carbon emissions due to LUC are considered in the uniform annualization approach.
 `polat_repeated_pattern` | if `True`, retro/extra-polation pattern is repeated before/after the first/last mentioned value. Otherwise, it is maintained constant.
 `final_currency`         | currency used to conduct the study and express the results. The current choices are `'EUR'` or `'USD'`. Set to `'EUR'` by default.
 `change_rates`           | `final_currency`-dependent exchange rate to consider in calculations, *e.g.* `{'EUR':{'USD/EUR':1.14,}}` *(or `{'EUR':{'EUR/USD':0.8772,}}` since the tool ensures dimensional homogeneity)*.
 `return_plts`            | if `True`, charts are returned (for interactive use). Otherwise, they are saved or shown to users depending on the value set for `save_charts`. Set to `False` by default.
 `save_charts`            | if `True`, charts are saved on the disk. Otherwise, they are shown to users. Set to `True` by default. **NB**: `return_plts=True` has priority over `save_charts`.
 `from_local_data`        | if `True`, scenarized trajectories (*e.g.* of CO2 prices, of output flows quantities, of yields) are read from the 'resources' folder that is located next to the working script. If `False`, those are read from the 'resources' folder natively contained in the package directory. Set to `False` by default.

Once we have our instance of `CBACalculator` in hand, *i.e.* `cba`, we may wonder what are the scenarized trajectories over which we are about to conduct our study, *e.g.* of CO2 prices, produced quantities of biofuel, etc. In this case, we can simply type:

    >>> cba.chart_of_output_flows_traj.show()

<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20ETH%20%5BO%5D.png?raw=true" width="60%"/><img></p>

As it reads in the above chart, we are about to work with a constant level of production over the project horizon. Note the abscence of flow in 2020: this illustrates the need for waiting one year before having enough wheat to produce biofuel.

We may then wonder what is the counterfactual trajectory in terms of gasoline – targeting the same [energy efficiency](https://en.wikipedia.org/wiki/Energy_conversion_efficiency) (in joule) as conversion basis: 

    >>> cba.chart_of_black_output_flows_traj.show()

<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20OIL%20%5BO%5D.png?raw=true" width="60%"/><img></p>

Now, let's see which trajectory of CO2 prices is behind the name `'SPC'` – which stands for [Quinet (2009)](http://www.ladocumentationfrancaise.fr/var/storage/rapports-publics/094000195.pdf)'s shadow price of carbon:

    >>> cba.chart_of_co2_prices_traj.show()

<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/PRICES%20co2%20%5BSPC%5D.png?raw=true" width="60%"/><img></p>

We may also wonder which quantities trajectory of wheat is implied by that of biofuel on the one hand, and by the value we set for the parameter `input_flows_scenario`, that is `'IFP'` , on the other hand – where *I.F.P* stands for *Institut Français du Pétrole énergies nouvelles* – which made a report in [2013](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/resources/yields/Input/Input.txt) in which it reads that, with 1 tonne of wheat, one can produce [0.2844](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/resources/yields/Input/WHEAT_yields_FR.csv) tonnes of bioethanol. Let's vizualize that:

    >>> cba.chart_of_input_flows_traj.show()

<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20input%20%5BIFP%5D%5BWHEAT%5D.png?raw=true" width="60%"/><img></p>

Note the abscence of input flow in 2040: as explained previously, this illustrates the time delay that exists between the cultivation of wheat and its proccesing into bioethanol, *e.g.* wheat cultivated in 2039 is used for the production of bioethanol planned in 2040.

The land use change from `initial_landuse='improved grassland'` to `final_landuse='wheat'` has effects in terms of CO2 emissions. These emissions clearly don't exhibit the same profile depending on how we choose to consider them over the project horizon. First, regarding soil CO2 emissions:

    >>> cba.carbon_and_co2_flows_traj_annualizer.so_emitting
    True
    >>> cba.chart_of_soco2_unif_flows_traj.show()
    >>> cba.chart_of_soco2_diff_flows_traj.show()
    ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
    ---- [***]The solution converged.[0.000000e+00][***]
    
<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2%20so%20%5Bunif-IMPROVED%20GRASSLAND~WHEAT%5D.png?raw=true" width="50%"/><img><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2%20so%20%5Bdiff-IMPROVED%20GRASSLAND~WHEAT%5D.png?raw=true" width="50%"/><img></p>

Of course, the comparison makes sense since the total emitted stocks are identical:

    >>> import numpy as np
    >>> np.sum(cba.soco2_unif_flows_traj)
    -10.90041830757967 # tonnes
    >>> np.sum(cba.soco2_diff_flows_traj)
    -10.90041830757967 # tonnes
    
On the side of vegetation-related emissions, converting grassland into wheat field generates a loss of carbon since the latter is harvested annually while the former sequestrates carbon on a pertpetual basis. Here again, emissions' profiles are clearly different under differentiated or uniform anualization approach, see 

    >>> cba.carbon_and_co2_flows_traj_annualizer.vg_emitting
    True
    >>> cba.chart_of_vgco2_unif_flows_traj.show()
    >>> np.sum(cba.vgco2_unif_flows_traj)
    -7.130970463238133 # tonnes
    >>> cba.chart_of_vgco2_diff_flows_traj.show()
    ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
    ---- [***]The solution converged.[0.000000e+00][***]
    >>> np.sum(cba.vgco2_diff_flows_traj)
    -7.130970463238132 # tonnes
    
<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2%20vg%20%5Bunif-IMPROVED%20GRASSLAND~WHEAT%5D.png?raw=true" width="50%"/><img><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2%20vg%20%5Bdiff-IMPROVED%20GRASSLAND~WHEAT%5D.png?raw=true" width="50%"/><img></p>

Independently of how we annualize the LUC-related CO2 emissions, the cultivation and the processing of wheat generate emissions annually as well. See

    >>> cba.chart_of_cult_input_co2eq_flows_traj.show()
    >>> cba.chart_of_proc_input_co2eq_flows_traj.show()
    
<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2eq%20%5Bcult-WHEAT%5D.png?raw=true" width="50%"/><img><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2eq%20%5Bproc-WHEAT%5D.png?raw=true" width="50%"/><img></p>

Once again, the two above charts unambiguously illustrate the time delay that exists between the cultivation of wheat and its proccesing into bioethanol, *i.e.* wheat cultivated in year *t-1* is used for the production of bioethanol planned in year *t*. Also, note that these cultivation- and processing-related emissions are in *CO2eq* since *CH4* and *N2O* flows are considered as well, using their relative global warming potentials – relatively to that of CO2 – as a basis of conversion. See calculation details at [PyGWP](https://github.com/lfaucheux/PyGWP). 

Finally, under the two types of annualization approach, the total emissions following a change in land use from improved grassland into wheat field are:

    >>> cba.chart_of_total_unif_co2_flows_traj.show()
    >>> cba.chart_of_total_diff_co2_flows_traj.show()

<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2%20total%20%5Bunif-ETH%5D.png?raw=true" width="50%"/><img><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/FLOWS%20TONNES%20co2%20total%20%5Bdiff-ETH%5D.png?raw=true" width="50%"/><img></p>

which, when monetized with a non-zero discount rate and compared in terms of absolute deviations from gasoline's valorized CO2 flows, lead to sensitivly different profiles for the values of the environmental component of the project, see rather

    >>> cba.chart_of_NPV_total_unif_minus_black_output_co2_flows_trajs.show()
    >>> cba.chart_of_NPV_total_diff_minus_black_output_co2_flows_trajs.show()
    
<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/dNPV%20co2%20total%20%5Bunif-SPC-ETHvsOIL%5D.png?raw=true" width="50%"/><img><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/dNPV%20co2%20total%20%5Bdiff-SPC-ETHvsOIL%5D.png?raw=true" width="50%"/><img></p>

Note the slop-breaks that occur during the last year. This is due to the fact that cultivation and its associated emission flows generally – depending on the type of final land use – finish one year before the end of the project, which structurally increases projects' carbon profitabilities.

### A note on the carbon profitability payback period

Actually, it looks like extending the horizon of the project may be a good idea to see whether one of the two temporal profiles – shown above – exhibit positive values over the long run. Put differently, let's vizualize *when* the project exhibits positive carbon profitabilities (CP) for each annualization approach.
    
•	*NB1: the project horizon must be long enough for such a payback period to exist. Hence the extension from 20 to 50 years configured below.*

•	*NB2: given that cultivation and its associated flows of emission generally – depending on the type of final land use – finish before the end of the project, projects' last years are structurally more environment-friendly, which increases projects' carbon profitabilities, in some cases to such an extent that these last years actually become the payback period, hence the NB1*.

    >>> cba._clear_caches()    # we clear the cache of our instance since we are going to change a calculation parameter.
    GlobalWarmingPotential     # the tool enumerates objects whose cache have been cleaned.
    OutputFlows
    CarbonAndCo2FlowsAnnualizer
    LandSurfaceFlows
    Co2Prices
    CBACalculator
    >>> cba.project_horizon = 50    # we set a long project horizon
    >>> cba.chart_of_NPV_total_unif_minus_black_output_co2_flows_trajs.show()
    >>> cba.chart_of_NPV_total_diff_minus_black_output_co2_flows_trajs.show()
    ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
    ---- [***]The solution converged.[0.000000e+00][***]
    ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
    ---- [***]The solution converged.[0.000000e+00][***]
    
<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/dNPV%20co2%20total%20%5Bunif-SPC-ETHvsOIL%5D-extended.png?raw=true" width="50%"/><img><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Example-1/dNPV%20co2%20total%20%5Bdiff-SPC-ETHvsOIL%5D-extended.png?raw=true" width="50%"/><img></p>

Rather than vizualizing the NPVs' profiles we may use a precise way to know *when* a project will become *environmentally* profitable – referred to as *Carbon Profitability Payback Period* in [Dupoux (2018)](https://github.com/lfaucheux/PyLUCCBA/raw/master/Dupoux_Sept2018.pdf) – for each type of annualization approach.

    >>> cba.unif_payback_period
    41 # years
    >>> cba.diff_payback_period
    35 # years
    
Let's be precautious and go back to the project's settings of interest.

    >>> cba._clear_caches()
    GlobalWarmingPotential
    OutputFlows
    CarbonAndCo2FlowsAnnualizer
    LandSurfaceFlows
    Co2Prices
    CBACalculator
    >>> cba.project_horizon = 20    # let's go back to our initial settings !

### A note on the compensatory rate

We may wonder under which discount rate the two approaches of annualization – uniform *versus* differentiated – would lead to the same carbon profitability (CP) over the project horizon. To do so, we have to use another object that is defined in `PyLUCCBA`, namely `CBAParametersEndogenizer`. Let's continue our example and instantiate it:

    >>> gen = cc.CBAParametersEndogenizer(CBACalculator_instance = cba)

With `gen` in hand, we can now determine which discount rate equalizes our two CPs, as follows:

    >>> cba_eq = gen.endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj
    ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
    ---- [***]The solution converged.[0.000000e+00][***]
    ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
    ---- [***]The solution converged.[0.000000e+00][***]
    ---- disc rate equating unif- and diff-based NPVs sol=[0.05420086]
    ---- [***]The solution converged.[4.440892e-16][***]
    
Note that `cba_eq` is the `disc_rate`-balanced counterpart of `cba`. It reads above that, "so configured", our project would have identical CPs under the uniform and differentiated annualization approaches for a discount rate of 5.42%.

At anytime, we can have a quick look at what is meant exactly by "so configured", typing

    >>> print(cba_eq.summary_args)
    **************************************************************************************
    run_name                : Example-1
    output                  : ETH
    black_output            : OIL
    initial_landuse         : IMPROVED GRASSLAND
    final_landuse/input     : WHEAT
    country                 : FRANCE
    project_horizon         : 21 # because of the time delay between cultivation and processing, taken at t0 - 1.
    T_so                    : 20
    T_vg_diff               : 1
    T_vg_unif               : 20
    project_first_year      : 2020
    polat_repeated_pattern  : True
    co2_prices_scenario     : SPC
    discount_rate           : [0.05420086] # our endogenized compensatory rate
    diff_payback_period     : []
    unif_payback_period     : []
    final_currency          : EUR
    change_rates            : {'USD/EUR': 1.14}
    output_flows_scenario   : O
    input_flows_scenario    : IFP
    message                 : _ENDOGENIZER finally says sol=0.0542008612895724 
                              obj(sol)=[4.4408921e-16]
                              
<hr>

## Invoking documentation

You should abuse of the python-bultin [`help`](https://www.programiz.com/python-programming/methods/built-in/help) on any object defined in PyLUCCBA, as well as on any instantiated object, *e.g.*
    
    >>> import PyLUCCBA as cc
    >>> help(cc.CBAParametersEndogenizer)
    Help on CBAParametersEndogenizer in module PyLUCCBA.core object:

    class CBAParametersEndogenizer(builtins.object)
     |  Class object designed to handle a CBACalculator instances and to
     |  endogenize some of its parameter.
     |  
     |  Methods defined here:
     |  
     |  __init__(self, CBACalculator_instance)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  OBJECTIVE_NPV_total_unif_co2_flows_traj_VS_NPV_total_diff_co2_flows_traj
     |      Method which computes the objective of the discount rate
     |      endogenizing process.
     |      
     |      Testing/Example
     |      ---------------
     |      >>> _dr_ = 0.03847487575799428 ## the solution
     |      >>> cba = CBACalculator._testing_instancer(
     |      ...     dr = _dr_, 
     |      ...     sc = 'WEO2015-CPS',
     |      ... )
     |      >>> CBAParametersEndogenizer(
     |      ...     CBACalculator_instance = cba
     |      ... ).OBJECTIVE_NPV_total_unif_co2_flows_traj_VS_NPV_total_diff_co2_flows_traj
     |      ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
     |      ---- [***]The solution converged.[0.000000e+00][***]
     |      ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
     |      ---- [***]The solution converged.[0.000000e+00][***]
     |      array([2.22044605e-16])
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj
     |      Returns a CBACalculator instance configured with the discount rate
     |      which equates NPV_total_unif_co2_flows_traj TO NPV_total_diff_co2_flows_traj.
     |      
     |      Testing/Example
     |      ---------------
     |      >>> cba = CBACalculator._testing_instancer(
     |      ...     sc = 'WEO2015-CPS',
     |      ... )
     |      >>> o = CBAParametersEndogenizer(
     |      ...     CBACalculator_instance = cba
     |      ... )
     |      >>> o.endo_disc_rate_which_eqs_NPV_total_unif_co2_flows_traj_to_NPV_total_diff_co2_flows_traj.discount_rate[0]
     |      ---- a_parameter_which_solves_soc_chosen_CRF_constrained sol=[0.52418009]
     |      ---- [***]The solution converged.[0.000000e+00][***]
     |      ---- a_parameter_which_solves_vgc_chosen_CRF_constrained sol=[0.02458071]
     |      ---- [***]The solution converged.[0.000000e+00][***]
     |      ---- disc rate equating unif- and diff-based NPVs sol=[0.03847488]
     |      ---- [***]The solution converged.[2.220446e-16][***]
     |      0.038474875757994256
     

I invite you to test the function `help` on any of the following objects: `cc.BlackOutputAndSubstitutesSpecificities`, `cc.CBACalculator`, `cc.CBAParametersEndogenizer`, `cc.CarbonAndCo2FlowsAnnualizer`, `cc.Co2Prices`, `cc.GlobalWarmingPotential`, `cc.InputFlows`, `cc.LandSurfaceFlows`, `cc.OutputFlows`, `cc.VGCAndSOCDeltas`, `cc.VegetationsAndSoilSpecificities`.


<hr>

## Data

Data are stored in the [resources](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources) folder, composed of the following subfolders:
  
•	The [dluc](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/dluc) folder that includes *(i)* [BioGrace Excel tool - version 4c.xls](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/resources/dluc/BioGrace%20Excel%20tool%20-%20version%204c.xls) cited in *(ii)* [Data_CarbonStocks_Emissions.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/resources/dluc/Data_CarbonStocks_Emissions.xlsx), in which you can see how the sequestrated carbon stock per type of land use are calculated and *(iii)* csv and txt files in which the results of these calculations are reported. *NB:* some data that have been calculated with [Data_CarbonStocks_Emissions.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/resources/dluc/Data_CarbonStocks_Emissions.xlsx) are stored in the body of core.py itself under the form of [python dictionary](https://www.w3schools.com/python/python_dictionaries.asp), see [process](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py#L151) and [cultivation](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py#L172).  

•	The [prices/Exput](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/prices/Exput) folder that includes the carbon price scenarios.

•	The [yields](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields) folder which has two folders. The first, named [Input](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields/Input), contains the yields necessary to the calculations: how much biofuel is produced from one tonne of feedstock (miscanthus or wheat) and how much biofuel can be produced per hectare. The second folder, named [Output](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields/Output), tautologically states than one tonne of biofuel is produced per tonne of output.

*NB: in the folders [prices/Exput](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/prices/Exput) and [yields](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields), note that:*

•	The csv files contain temporal trajectories (of prices, of quantities, of yields, ...). These trajectories can be sparse. Indeed, when sparse trajectories with more than one point are provided, say, CO2 prices such as in the scenario *WEO2015-CPS* – see [CO2_prices_FR.csv](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/resources/prices/Exput/CO2_prices_FR.csv) –, the tool automatically retro/intra/extrapolates the values for each year in an exponential way. When both retro- and extrapolation are possible, retropolation is favoured and implied using the next period's rate of growth. Then, if the parameter `polat_repeated_pattern` is set to `True`, extrapolation is performed repeating the pattern of growth rates. If the parameter is set to `False`, the last known value in maintained constant. In the case of sparse trajectories that contain only one value – see *e.g.* [WHEAT_yields_FR.csv](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/resources/yields/Input/WHEAT_yields_FR.csv) –, it is assumed to be constant over the project horizon.

•	The txt files contain informations related to the trajectories that are stored in csv files.


<hr>

## Data customization/addition

You may want to add your own scenarii regarding, say, how the price CO2 evolves, the trajectory of output flows to produce annually, the necessary quantity of input that is required to produce 1 tonne of output, etc...
Given that data are stored (in txt and csv formats) according to a hard-to-guess directory tree, the easiest way to work with custom data is to imitate the package-native data that are contained in the [*resources*](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources) folder. Let's thus start with a local copy of this folder:

    >>> import PyLUCCBA as cc
    >>> cc.folder_copier(name='resources')
    'resources' folder copied to C:\path\to\folder
    
Now, to explore the data, go to `C:\path\to\folder`, where you wil see a folder named `resources` that is the exact copy of the data used in [Dupoux (2018)](https://github.com/lfaucheux/PyLUCCBA/raw/master/Dupoux_Sept2018.pdf).

#### Adding new CO2 prices (or output flows) trajectory

To add a scenario of CO2 prices, go to the folder `resources\prices\Exput` of your local copy. There, you will find two files, namely `CO2_prices_FR.csv` and `Exput.txt`. First, open the csv file, add a scenario's name in the first line, *e.g.* `customPricesScenario`, and prices in the just-named column. Remember that your newly-added trajectory can be sparse and that the tool will retro/intra/extrapolate missing prices. Second, open the txt file and add two lines related to `customPricesScenario`, as shown below:

    customPricesScenario:unit:EUR/tonne
    customPricesScenario:yrb:none
    
The first line tells the tool in which currency the prices are expressed. Note that the tool is actually not capable of dealing with other mass-units than `tonne`, so stick to it. The second line is not mandatory, and is simply here to simplify the potential future improvements of the tool. Finally, to imply this trajectory of prices in your calculations, simply instantiate `CBACalculator` with `'customPricesScenario'`, *i.e.*

    >>> cba = cc.CBACalculator(
            # ...
            co2_prices_scenario = 'customPricesScenario', # not case sensitive
            # ...
        )
        
Note that to add a new trajectory of annual output flows, the approach is exactly the same as that described for CO2 prices. This time, the files are stored in the folder `resources\yields\Output` of your local copy.

#### Adding new dluc or input yields related data

Please, contact me if you are interested in doing so.

<hr>

## Format of results

 *The scripts that must be used to obtain the *results* presented in [Dupoux (2018)](https://www.researchgate.net/publication/304170193_The_land_use_change_time-accounting_failure) are contained in the [example](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/examples) folder.*

  The generated results consists of three .xlsx files, namely [\_quantities.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/examples/Example-1/_quantities.xlsx), [\_values.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/examples/Example-1/_values.xlsx)  and [\_NPVs.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/examples/Example-1/_NPVs.xlsx) all three located in a folder that is named (by default) according to the arguments involved in the computation:
  
•	[\_quantities.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/examples/Example-1/_quantities.xlsx), which only displays the quantities associated to each flow, among which, emissions from the process of production, emissions from the cultivation of the feedstock, land use change impact from soil, land use change impact from biomass, etc.

•	[\_values.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/examples/Example-1/_values.xlsx) which displays the monetary value of the different types of flows from both bioethanol and gasoline (“black”) depending of the carbon price scenario chosen in “study_case.py”.

•	[\_NPVs.xlsx](https://github.com/lfaucheux/PyLUCCBA/raw/master/PyLUCCBA/examples/Example-1/_NPVs.xlsx) which displays the net present values for both the uniform and the differentiated annualizations for the different types of flow again. All titles specify what is calculated. Note that “ut” refers to bioethanol quantities in tonne and “um” refers to bioethanol quantities in megajoules (MJ).

Note that each column has a title that is very verbose – so as to make things as explicit as possible – regarding what is calculated. When the prefix **ut_** appears in the title it means that it is calculated for one unit tonne of biofuel. When the prefix **um_** appears in the title, it means that it is calculated for one unit megajoule of biofuel. When nothing is specified, it takes into account the total quantity of biofuel produced.

<hr>

## Paper's results replication

All the results presented in [Dupoux (2018)](https://github.com/lfaucheux/PyLUCCBA/raw/master/Dupoux_Sept2018.pdf) can easily be reproduced. To replicate a specific result, one has to `import` the associated script. Its importation will run the code that is required to generate the results. The table that follows makes the association between the python `import`-commands and the cases presented in the paper.

 Paper's section and page | Python command                                                     | Invoked script
 ------------------------ | ------------------------------------------------------------------ | -------------------
 Subsection 3.2 page 11   | `from PyLUCCBA.examples import study_Forest_DiscountingEffect`     | [*study_Forest_DiscountingEffect.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Forest_DiscountingEffect.py)
 Subsection 3.2 page 12   | `from PyLUCCBA.examples import study_Grassland_DiscountingEffect`  | [*study_Grassland_DiscountingEffect.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Grassland_DiscountingEffect.py)
 Subsection 3.2 page 12   | `from PyLUCCBA.examples import study_Forest_CarbonPriceEffect`     | [*study_Forest_CarbonPriceEffect.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Forest_CarbonPriceEffect.py)
 Subsection 3.2 page 13   | `from PyLUCCBA.examples import study_Grassland_CarbonPriceEffect`  | [*study_Grassland_CarbonPriceEffect.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Grassland_CarbonPriceEffect.py)
 Subsection 3.2 page 13   | `from PyLUCCBA.examples import study_Forest_CombinedEffect`        | [*study_Forest_CombinedEffect.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Forest_CombinedEffect.py)
 Subsection 3.2 page 14   | `from PyLUCCBA.examples import study_Grassland_CombinedEffect`     | [*study_Grassland_CombinedEffect.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Grassland_CombinedEffect.py)
 Subsection 4.1 page 14   | `from PyLUCCBA.examples import study_Forest_CompensatoryRate`      | [*study_Forest_CompensatoryRate.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Forest_CompensatoryRate.py)
 Subsection 4.1 page 14   | `from PyLUCCBA.examples import study_Grassland_CompensatoryRate`   | [*study_Grassland_CompensatoryRate.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Grassland_CompensatoryRate.py)
 Subsection 4.2 page 15   | `from PyLUCCBA.examples import study_Grassland_PaybackPeriod`      | [*study_Grassland_PaybackPeriod.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Grassland_PaybackPeriod.py)


In case you want to modify those scripts instead of simply invoking them, you can first copy them to your working directory, typing

    >>> import PyLUCCBA as cc
    >>> cc.folder_copier(name='examples')
    'examples' folder copied to C:\path\to\folder

Second, go to `C:\path\to\folder`, where you wil see a folder named `examples` that contains the exact copies of the scripts enumerated in the above table. To edit one of those scripts, say, [*study_Grassland_CompensatoryRate.py*](https://raw.githubusercontent.com/lfaucheux/PyLUCCBA/master/PyLUCCBA/examples/study_Grassland_CompensatoryRate.py), right-click it and and select option *Edit with [IDLE](http://anh.cs.luc.edu/python/hands-on/3.1/handsonHtml/idle.html#windows-in-idle)*. Modify anything you want. To execute the script, type **F5**.

<hr>

## References

Hoefnagels, R., E. Smeets, and A. Faaij (2010). “[Greenhouse gas footprints of different biofuel production systems](https://www.sciencedirect.com/science/article/pii/S1364032110000535)”. _Renewable and Sustainable Energy Reviews_ 14.7, pp. 1661–1694.

IEA (2015). _World Energy Outlook 2015_. Tech. rep. International Energy Agency.

IPCC (2006). “Volume 4: Agriculture, Forestry and Other Land Use”. _IPCC guidelines for national greenhouse gas inventories 4_.

Poeplau, C., A. Don, L. Vesterdal, J. Leifeld, B. VanWesemael, J. Schumacher, and A. Gensior (2011). “[Temporal dynamics of soil organic carbon after land-use change in the temperate zone - carbon response functions as a model approach](https://www.researchgate.net/publication/242081920_Temporal_dynamics_of_soil_organic_carbon_after_land-use_change_in_the_temperate_zone-Carbon_response_functions_as_a_model_approach)”. _Global Change Biology_ 17.7, pp. 2415–2427.

The European Commission (2010). “[Commission decision of 10 June 2010 on guidelines for the calculation of land carbon stocks for the purpose of Annex V to Directive 2009/28/EC](https://www.emissions-euets.com/component/content/article/261-commission-decision-of-10-june-2010-on-guidelines-for-the-calculation-of-land-carbon-stocks-for-the-purpose-of-annex-v-to-directive-200928ec)”. _Official Journal of The European Union_ 2010/335/E.

Dupoux, M. “[The land use change time-accounting failure](https://github.com/lfaucheux/PyLUCCBA/raw/master/Dupoux_Sept2018.pdf)” (in press).


<hr>

## Code coverage

|  Module  | statements | missing | excluded | coverage |
| -------- | ---------- | ------- | -------- | -------- |
| core.py  | 860        | 27      | 0        | 97%      |
| tools.py | 306        | 62      | 0        | 80%      |
| Total    | 1166       | 89      | 0        | 92%      |
