# PyLUCCBA
A Land-Use-Change Cost-Benefit-Analysis calculator coded in [Python](https://www.python.org/downloads/).

#### Code coverage

|  Module  | statements | missing | excluded | coverage |
| -------- | ---------- | ------- | -------- | -------- |
| core.py  | 893        | 103     | 0        | 88%      |
| tools.py | 290        | 58      | 0        | 80%      |
| Total    | 1183       | 161     | 0        | 86%      |

## Installation

First, you need Python installed, either [Python2.7.+](https://www.python.org/downloads/) or [Python3.+](https://www.python.org/downloads/). Either versions are good for our purpose. Then, we are going to use a package management system to install [PyLUCCBA](https://github.com/lfaucheux/PyLUCCBA), namely [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)), _already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4_. Open a session in your OS shell prompt and type

    pip install pyluccba

Or using a non-python-builtin approach, namely [git](https://git-scm.com/downloads),

    git clone git://github.com/lfaucheux/PyLUCCBA.git
    cd PyLUCCBA
    python setup.py install 


## Example usage
    
*The example that follows is done with the idea of reproducing the results presented in Dupoux 2018. via the Python Shell*.

Let's first import the module `PyLUCCBA`

    >>> import PyLUCCBA as cc

The alias of `PyLUCCBA`, namely `cc`, actually contains many objects definitions, such as that of the calculator that we are going to use in examples. The name of the calculator is `CBACalculator`.

But before using the calculator as such, let's define (and introduce) the set of parameters that we are going to use to configure `CBACalculator`. As can be expected when performing a cost-benefit-analysis, these parameters are related to: *(i)* the horizon of the project, *(ii)* the discount rate that we want to use in our calculations, *(iii)* the scenarized price trajectory of carbon dioxide, *(iv)* the scenarized trajectory of quantities of bio-ethanol to produce annualy and *(...)* so on. Let's introduce them all in practice:.

    >>> cba = cc.CBACalculator(
            run_name               = 'introduction example 1',
            country                = 'france',
            project_first_year     = 2020,
            project_horizon        = 20,
            discount_rate          = .03,
            co2_prices_scenario    = 'SPC',
            output_flows_scenario  = 'O',
            initial_landuse        = 'annual cropland',
            final_landuse          = 'miscanthus',
            input_flows_scenario   = 'DOE',
            T_so                   = 20,
            T_vg_diff              = 1,
            T_vg_unif              = 20,
            polat_repeated_pattern = True,
            final_currency         = 'EUR',
            change_rates           = {'EUR':{'USD/EUR':1.14}}, # https://www.google.fr/#q=EUR+USD
            return_plts            = True,
        )

The following table enumerates tall parameters that can be used to create an intance of `CBACalculator`.

 Parameter's name         | and signification
 ------------------------ | -------
 `run_name`               | name of the folder that will contain the generated results and charts, *e.g.* `'introduction example 1'`.
 `country`                | name the country under study. Only *one* possible choice currently: `France`.
 `project_first_year`     | first year of the project (for the sake legibility).
 `project_horizon`        | duration of the biofuel production project (years).
 `discount_rate`          | rate involved in the calculations of net present values. Set to `0.` by default.
 `co2_prices_scenario`    | name of the trajectory of carbon (dioxide) prices. The current choices are `'A'`, `'B'`, `'C'`, `'DEBUG'`, `'O'`, `'SPC'`, `'WEO2015-450S'`, `'WEO2015-CPS'` or `'WEO2015-NPS'`.
 `output`                 | name of the produced output. Set to `'eth'` by default. Only *one* possible choice currently: `'eth'`.
 `black_output`           | name of the counterfactual produced output. Serves as the reference according to which the production of bioethanol (`'eth'`) is considered (or not) as pro-environmental. Set to `'oil'` by default. Only *one* possible choice currently: `'oil'`. 
 `output_flows_scenario`  | name of the trajectory of annually produced quantities of biofuel. The current choices are `'DEBUG'` or `'O'`.
 `initial_landuse`        | use of the land *before* land conversion. The current choices are `'forestland30'`, `'improved grassland'`, `'annual cropland'` or `'degraded grassland'`.
 `final_landuse`          | use of the land *after* land conversion. The current choices are `'miscanthus'`, `'sugarbeet'` or `'wheat'`.
 `input_flows_scenario`   | name of the trajectory of input-to-ouput yields. The current choices depend on the value set for `final_landuse`. If `final_landuse` is set to `'miscanthus'`, the possibilities are `'DEBUG'` and `'DOE'`. If `final_landuse` is set to `'wheat'` or `'sugarbeet'`, the possibilities are `'CRISTANOL'` and `'DEBUG'`.
 `T_so`                   | period over which soil carbon emissions due to LUC are considered.
 `T_vg_diff`              | period over which vegetation carbon emissions due to LUC are considered in the differentiated annualization approach.
 `T_vg_unif`              | period over which vegetation carbon emissions due to LUC are considered in the uniform annualization approach.
 `polat_repeated_pattern` | if `True`, retro/extra-polation pattern is repeated before/after the first/last mentioned value. Otherwise, it is maintained constant.
 `final_currency`         | currency used to express the results. The current choices are `'EUR'` or `'USD'`. Set to `'EUR'` by default.
 `change_rates`           | `final_currency`-dependent exchange rate value to consider in calculations, *e.g.* `{'EUR':{'USD/EUR':1.14,}}` *(or `{'EUR':{'EUR/USD':0.8772,}}` since the tool ensures dimensional homogeneity)*.
 `return_plts`            | if `True`, charts are returned (for interactive use). Otherwise, they are saved on the disk. Set to `False` by default.
 `save_charts`            | if `True` charts are on the disk. Otherwise, they are shown to users. Set to `True` by default. **NB** `return_plts=True` has priority over `save_charts`.

We may wonder what the scenarized trajectories of carbon dioxid prices and produced quantities of biofuel are. In this case, we can simply type:

    >>> cba.chart_of_scenarized_output_flows.show()

<p align="center"><img src="https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/examples/Grassland-Cropland_DR%3D0.03_CP%3DC_TH%3DXX/FLOWS%20TONNES%20ETH%20%5BO%5D.png?raw=true" width="60%"/><img></p>






## Value of the data
<details><summary><i>(click to expand)</i></summary>
<p>

•	The calculator offers a compilation of environmental and economic data to generate environment-related net present values of any project with impacts to the environment (GHG emissions or sequestrations).

•	The calculator is coded in [Python](https://www.python.org/downloads/) (compatible with both versions: 2 and 3). [Python](https://www.python.org/downloads/) is a cross platform and a comprehensive extensible and editable language with a large community of users.

•	The structure of the code is simple with accessible input data to which it is possible to add or suppress one’s own trajectories (of prices, carbon stocks, etc).

•	The compensatory rate (see the paper for more information) can be calculated easily with the tool.

•	Note that constant returns to scale (biofuel production) are assumed in the tool.

</p>
</details>  

## Data
<details><summary><i>(click to expand)</i></summary>
<p>

  Raw data from the public repository as listed above are first used in the “Data_CarbonStocks_Emissions” Excel file to generate (i) land use change carbon stock changes for the scenarios studied in the paper, and (ii) emissions from the process and cultivation of bioethanol. This data is then directly used in the tool (either in the “resources” folder or the code) which is described below. The output data is not directly provided but as explained below, it can be generated easily with the “ready-to-use” study cases provided.

## Materials and Methods

  The calculator, as such, is divided into two (tested and documented) python scripts, namely [core.py](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py) and another that contains non-thematic-specific functions and classes, [tools.py](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py). The scripts that must be used to obtain the *results* presented in [Dupoux (2016)](https://www.researchgate.net/publication/304170193_The_land_use_change_time-accounting_failure) are contained in the [example](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/examples) folder.

#### Used data

  The results are based on data located in the body of [core.py](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py) itself (under the form of python-native dictionary) and in the [resources](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources) folder. The latter folder is composed of:
  
•	The [dluc](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/dluc) folder in which the dluc calculations are reported (see calculations in the provided “Data” Excel file). The .txt file indicates the units of data.

•	The [prices](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/prices) folder which includes the carbon price trajectories scenarios. When only one-time prices are provided, such as in the World Energy Outlook, there is an automatic process which extrapolates the values for each year in an exponential way. For example, if prices are provided at year 2020 and 2025, then the prices at 2021, 2022, 2023 and 2024 are generated in an exponential way. The .txt file provides the unit and year base for the monetary used in scenarios (e.g. EUR 2012).

•	The [yields](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields) folder which has two folders. The first, named [Input](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields/Input), contains the yields necessary to the calculations: how much biofuel is produced from one tonne of feedstock (miscanthus or wheat) and how much biofuel can be produced per hectare. The second folder, named [Output](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields/Output), is only instrumental and tautologically states than one tonne of biofuel is produced per tonne of output.

#### Generated results

  The generated results consists of three .xlsx files, namely [\_quantities.xlsx], [\_values.xlsx]  and [\_NPVs.xlsx] all three located in a folder that is named (by default) according to the arguments involved in the computation:
  
•	[\_quantities.xlsx], which only displays the quantities associated to each flow, among which, emissions from the process of production, emissions from the cultivation of the feedstock, land use change impact from soil, land use change impact from biomass, etc.

•	[\_values.xlsx] which displays the monetary value of the different types of flows from both bioethanol and gasoline (“black”) depending of the carbon price scenario chosen in “study_case.py”.

•	[\_NPVs.xlsx] which displays the net present values for both the uniform and the differentiated annualizations for the different types of flow again. All titles specify what is calculated. Note that “ut” refers to bioethanol quantities in tonne and “um” refers to bioethanol quantities in megajoules (MJ).

Note that each column has a title that is very verbose -- so as to make things as explicit as possible -- regarding what is calculated. When the prefix **ut_** appears in the title it means that it is calculated for one unit tonne of biofuel. When the prefix **um_** appears in the title, it means that it is calculated for one unit megajoule of biofuel. When nothing is specified, it takes into account the total quantity of biofuel produced.

</p>
</details>  

## Acknowledgements
<details><summary><i>(click to expand)</i></summary>
<p>

  I am particularly grateful to Laurent Faucheux from [CIRED](http://www.centre-cired.fr/index.php/fr/) for the coding of the tool I conceived. Researchers from l’[Institut Français du Pétrole et des énergies nouvelles](http://www.ifpenergiesnouvelles.fr/), Frédérique Bouvart, Cécile Querleu, Daphné Lorne, Pierre Collet, and from l’[Institut National de la Recherche Agronomique](http://www.inra.fr/), Serge Garcia, Stéphane de Cara Alexandra Niedwiedth, Raja Chakir are also acknowledged for their valuable advice in the search for input data.

</p>
</details>  

## References
<details><summary><i>(click to expand)</i></summary>
<p>

Hoefnagels, R., E. Smeets, and A. Faaij (2010). “[Greenhouse gas footprints of different biofuel production systems](https://www.sciencedirect.com/science/article/pii/S1364032110000535)”. _Renewable and Sustainable Energy Reviews_ 14.7, pp. 1661–1694.

IEA (2015). _World Energy Outlook 2015_. Tech. rep. International Energy Agency.

IPCC (2006). “Volume 4: Agriculture, Forestry and Other Land Use”. _IPCC guidelines for national greenhouse gas inventories 4_.

Levasseur, A., Lesage, P., Margni, M., Deschênes, L., and Samson, R (2010). “[Considering Time in LCA: Dynamic LCA and Its Application to Global Warming Impact Assessments](https://pubs.acs.org/doi/abs/10.1021/es9030003)”. _Environmental Science & Technology_ 44.8, pp. 3169-3174 

Poeplau, C., A. Don, L. Vesterdal, J. Leifeld, B. VanWesemael, J. Schumacher, and A. Gensior (2011). “[Temporal dynamics of soil organic carbon after land-use change in the temperate zone - carbon response functions as a model approach](https://www.researchgate.net/publication/242081920_Temporal_dynamics_of_soil_organic_carbon_after_land-use_change_in_the_temperate_zone-Carbon_response_functions_as_a_model_approach)”. _Global Change Biology_ 17.7, pp. 2415–2427.

The European Commission (2010). “[Commission decision of 10 June 2010 on guidelines for the calculation of land carbon stocks for the purpose of Annex V to Directive 2009/28/EC](https://www.emissions-euets.com/component/content/article/261-commission-decision-of-10-june-2010-on-guidelines-for-the-calculation-of-land-carbon-stocks-for-the-purpose-of-annex-v-to-directive-200928ec)”. _Official Journal of The European Union_ 2010/335/E.

Dupoux, M. “[The land use change time-accounting failure](https://www.researchgate.net/publication/304170193_The_land_use_change_time-accounting_failure)” (in press).

</p>
</details>