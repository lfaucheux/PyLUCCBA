# PyLUCCBA
A Land-Use-Change Cost-Benefit-Analysis calculator coded in python.

## Code coverage

|  Module  | statements | missing | excluded | coverage |
| -------- | ---------- | ------- | -------- | -------- |
| core.py  | 893        | 103     | 0        | 88%      |
| tools.py | 290        | 58      | 0        | 80%      |
| Total    | 1183       | 161     | 0        | 86%      |


## Value of the data

•	The calculator offers a compilation of environmental and economic data to generate environment-related net present values of any project with impacts to the environment (GHG emissions or sequestrations).

•	The calculator is coded in Python (2 and 3). Python is a cross platform and a comprehensive extensible and editable language with a large community of users.

•	The structure of the code is simple with accessible input data to which it is possible to add or suppress one’s own trajectories (of prices, carbon stocks, etc).

•	The compensatory rate (see the paper for more information) can be calculated easily with the tool.

•	Note that constant returns to scale (biofuel production) are assumed in the tool.

## Data
  Raw data from the public repository as listed above are first used in the “Data_CarbonStocks_Emissions” Excel file to generate (i) land use change carbon stock changes for the scenarios studied in the paper, and (ii) emissions from the process and cultivation of bioethanol. This data is then directly used in the tool (either in the “resources” folder or the code) which is described below. The output data is not directly provided but as explained below, it can be generated easily with the “ready-to-use” study cases provided.

## Materials and Methods

  The calculator, as such, is divided into two (tested and documented) python scripts, namely [core.py](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py) and another that contains non-thematic-specific functions and classes, [tools.py](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py). The scripts that must be used to obtain the *results* presented in [Dupoux (2016)](https://www.researchgate.net/publication/304170193_The_land_use_change_time-accounting_failure) are contained in the [example](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/examples) folder.

#### Used data

  The results are based on data located in the body of [core.py](https://github.com/lfaucheux/PyLUCCBA/blob/master/PyLUCCBA/core.py) itself (under the form of python-native dictionary) and in the [resources](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources) folder. The latter folder is composed of:
  
•	The [dluc](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/dluc) folder in which the dluc calculations are reported (see calculations in the provided “Data” Excel file). The .txt file indicates the units of data.

•	The [prices](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/prices) folder which includes the carbon price trajectories scenarios. When only one-time prices are provided such as in the World Energy Outlook, there is an automatic process which extrapolates the values for each year in an exponential way. For example, if prices are provided at year 2020 and 2025, then the prices at 2021, 2022, 2023 and 2024 are generated in an exponential way. The .txt file provides the unit and year base for the monetary used in scenarios (e.g. EUR 2012).

•	The [yields](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields) folder which has two folders:
  o	The first, named [Input](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields/Input), contains the yields necessary to the calculations: how much biofuel is produced from one tonne of feedstock (miscanthus or wheat) and how much biofuel can be produced per hectare.
  o	The second one, named [Output](https://github.com/lfaucheux/PyLUCCBA/tree/master/PyLUCCBA/resources/yields/Output), is only instrumental and tautologically states than one tonne of biofuel is produced per tonne of output.

#### Generated results

  The generated results consists of three .xlsx files, namely [\_quantities.xlsx], [\_values.xlsx]  and [\_NPVs.xlsx] all three located in a folder that is named (by default) according to the arguments involved in the computation:
  
•	[\_quantities.xlsx], which only displays the quantities associated to each flow, among which, emissions from the process of production, emissions from the cultivation of the feedstock, land use change impact from soil, land use change impact from biomass, etc.

•	[\_values.xlsx] which displays the monetary value of the different types of flows from both bioethanol and gasoline (“black”) depending of the carbon price scenario chosen in “study_case.py”.

•	[\_NPVs.xlsx] which displays the net present values for both the uniform and the differentiated annualizations for the different types of flow again. All titles specify what is calculated. Note that “ut” refers to bioethanol quantities in tonne and “um” refers to bioethanol quantities in megajoules (MJ).

Note that each column has a title that is very verbose -- so as to make things as explicit as possible -- regarding what is calculated. When the prefix **ut_** appears in the title it means that it is calculated for one unit tonne of biofuel. When the prefix **um_** appears in the title, it means that it is calculated for one unit megajoule of biofuel. When nothing is specified, it takes into account the total quantity of biofuel produced.

## Acknowledgements 
  I am particularly grateful to Laurent Faucheux from [CIRED](http://www.centre-cired.fr/index.php/fr/) for the coding of the tool I conceived. Researchers from l’[Institut Français du Pétrole et des énergies nouvelles](http://www.ifpenergiesnouvelles.fr/), Frédérique Bouvart, Cécile Querleu, Daphné Lorne, Pierre Collet, and from l’[Institut National de la Recherche Agronomique](http://www.inra.fr/), Serge Garcia, Stéphane de Cara Alexandra Niedwiedth, Raja Chakir are also acknowledged for their valuable advice in the search for input data.

## References 
Hoefnagels, R., E. Smeets, and A. Faaij (2010). “[Greenhouse gas footprints of different biofuel production systems](https://www.sciencedirect.com/science/article/pii/S1364032110000535)”. _Renewable and Sustainable Energy Reviews_ 14.7, pp. 1661–1694.

IEA (2015). _World Energy Outlook 2015_. Tech. rep. International Energy Agency.

IPCC (2006). “Volume 4: Agriculture, Forestry and Other Land Use”. _IPCC guidelines for national greenhouse gas inventories 4_.

Levasseur, A., Lesage, P., Margni, M., Deschênes, L., and Samson, R (2010). “[Considering Time in LCA: Dynamic LCA and Its Application to Global Warming Impact Assessments](https://pubs.acs.org/doi/abs/10.1021/es9030003)”. _Environmental Science & Technology_ 44.8, pp. 3169-3174 

Poeplau, C., A. Don, L. Vesterdal, J. Leifeld, B. VanWesemael, J. Schumacher, and A. Gensior (2011). “[Temporal dynamics of soil organic carbon after land-use change in the temperate zone - carbon response functions as a model approach](https://www.researchgate.net/publication/242081920_Temporal_dynamics_of_soil_organic_carbon_after_land-use_change_in_the_temperate_zone-Carbon_response_functions_as_a_model_approach)”. _Global Change Biology_ 17.7, pp. 2415–2427.

The European Commission (2010). “[Commission decision of 10 June 2010 on guidelines for the calculation of land carbon stocks for the purpose of Annex V to Directive 2009/28/EC](https://www.emissions-euets.com/component/content/article/261-commission-decision-of-10-june-2010-on-guidelines-for-the-calculation-of-land-carbon-stocks-for-the-purpose-of-annex-v-to-directive-200928ec)”. _Official Journal of The European Union_ 2010/335/E.

Dupoux, M. “[The land use change time-accounting failure](https://www.researchgate.net/publication/304170193_The_land_use_change_time-accounting_failure)” (in press).

## ...

study_case.py is the script where scenarios arguments are formalized and where core.py is imported as a package and then used to execute calculations (e.g. a project evaluated over 20 years with time span of 20 years for both the soil and the vegetation, a classical GWP horizon of 100 years, a discount rate of 3% and scenario “A” for the price of carbon, grassland converted into an annual cropland). To run the tool, just press F5 from  a “study_cases” file. Among the files provided, there are several “study_cases” files: “study_cases_BASE” is the basic file with no specific scenario referring to the paper. For the sake of reproducibility, all the other study cases refer to scenarios used to generate each result of the paper.
Within each study case, you need to specify the scenario you are interested in. Below, I provide a description of all the categories that specify one scenario. Please refer to the file “study_cases_BASE.
-	run_name: here you can specify a title for the files that will be generated by the tool;
-	project_horizon: this is the time horizon of the project. It is set to 20 years in general since in the article I am interested in land use change impacts that are considered over 20 years by the European Commission;
-	T_so: this is the time horizon specific to land use change impacts related to the soil. It is here 20 years as assumed by the European Commission;
-	T_vg_diff: this is the time horizon specific to land use change impacts related to biomass assumed under the differentiated approach. According to the literature, it is assumed to be 1 year i.e. instantaneous impact;
-	T_vg_unif:. this is the time horizon specific to land use change impacts related to biomass assumed under the uniform approach. It is 20 years as assumed by the European Commission. 
-	discount_rate: this is the value of the discount rate chosen for your analysis.;
-	co2_prices_scenario: this is the carbon price scenario you need for your analysis. There are some well-known carbon price scenarios provided in the “resources” folder but you may want to add your own scenarios. In this case, please add a column to the .csv file “CO2_prices_FR” in the folder PyLUCCBA -> resources -> prices -> Exput. In this case, add the currency as well as the year base of the currency in the Exput.txt file in the same folder as for the other scenarios, as follows.
o	“name of the scenario”:unit: “currency”/ “quantity unit”
o	“name of the scenario”:yrb: “year”
-	initial_landuse: this is the initial land use before conversion into energy cropland. All the scenarios provided refer to specific carbon stocks for both soil and biomass. This data is gathered in the “CS_yields_FR” .csv file in the “dluc” folder in the “resources” folder. To change the scenario in the study case, enter the corresponding number which is in the square brackets. More accurately, [0] refers to the first land in brackets i.e. “FORESTLAND30”, [1] refers to “improved grassland”, [2] refers to “annual cropland”, [3] refers to “degraded grassland”. Note that you can add scenarios in the “CS_yields_FR” .csv file and add their name in the Python file inside the square brackets which contains the list of possible lands;	
-	final_landuse: this is the type of energy crop. There are only two options here ([0] for “miscanthus” and [1] for “wheat”), but, again, it can be extended to other types of lands via the “CS_yields_FR” .csv file;
-	input_flows_scenario: this is referring to the biofuel yield (see folder “Input” in folder “yields” itself in folder “resources”). Here, “CRISTANOL” is option [0] and refers to wheat-based bioethanol and “DOE” is option [1] and refers to miscanthus-based bioethanol. Other scenarios can be added to the .csv files again.

## How to use the two tools provided in the paper to support policy-making
-	To obtain the compensatory rate described in the article, please use the study case named “study_cases_Compensatory-Rate”. It will calculate the endogenous discount rate needed to cancel the difference between the uniform and the differentiated approach. The only difference of these study cases (there is one for Grassland and one for Forestland here) compared to the others is that the line “#cba = CBA_parameters_endogenizer(cba).ENDOGENOUS_discount_rate_which_equates_NPV_TOTAL_uniform_co2_flows_TO_NPV_TOTAL_differentiated_co2_flows” is not commented anymore in the code, which allows for the calculation of the compensatory rate. Once you click F5, the tool will display the compensatory rate corresponding to the scenario you chose in a new window. It will appear under the name “discount_rate” in the results window. Note that if you decide to calculate the compensatory rate, there is no need to specify an exogenous discount rate for your analysis since it will be automatically calculated to reach an equality between the net present value under the uniform approach and the net present value under the differentiated approach.
-	The carbon profitability payback period is also directly given in the results window once you press F5 (after specifying the scenario you are interested in). The carbon profitability payback period is the time from which the difference of NPVs between bioethanol and fossil fuel (black output) switches from a negative value to a positive value (involving greenhouse gas savings). The CBA calculator displays it directly. First, enter a “project_horizon” which is long enough to get a switch from a negative to a positive NPV (e.g. 150 years). Once you generate the results of a scenario (by pressing F5), the results window will display the payback periods related to both the uniform and the differentiated approaches. If it does not display any number, it means that the project horizon you entered is not long enough to get a switch form positive to negative values. Then, enter a longer project horizon and start again.


