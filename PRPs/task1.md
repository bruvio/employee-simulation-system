imagine running the code using 
```python employee_simulation_orchestrator.py --scenario GEL```

it creates a million of json xlxs files it creates empty subfolders, there is no way to understand the analysis that has been run, the statistics on the population, on how the population is stratified, files are hiddenm, subfolders are generated using a timestamp as suffix which will be confusing when trying to locate the data if running multiple simulations.

there should be one html file containing all information, all graphs and a single MD file with a story to be used as report. this md file should also contain mermaid graphs to explain the data.

the objective is to understand which the current config what are the consequences on salary inequality, how to reward high performers. generally a manager manages up to 6 engineers and can allocate 0.5% to address inequality.

create a new branch to address this


another task is to use the following list of job titles and associated minimum salary 
Airlock Coordinator
£37,000

Data Engineer x4
£73,000

Director of Equity Assurance (18 month fixed term contract)
£101,500


Genome Analyst x 2 roles
£47,500

£60,000

Platform Engineer
£71,500

Platform Engineer - EDS
£71,500

QA Engineer - Python
£53,500

R&D laboratory Scientist (12 month fixed term contract)
£33,500

Senior Product Designer
£63,300

£71,300

Solutions Architect
£93,500


Role
Salary from
Talent Acquisition Partner
Hiring Manager
Person who can tell you more
Brief Blurb
Applied Machine Learning Researcher
£70,500

Audience Engagement Lead x 2 roles
£65,500

Bioinformatics Engineer
£56,000

Chief Information Security Officer
£127,000

Committee Manager - Participant Panel
£44,500

Cyber Security Engineer
£71,500

Director of Portfolio Management
£92,000

£59,000

Genomic Data Scientist  x2
£55,000

Infrastructure Architect
£86,000

Platform Engineer (12 Month Fixed Term Contract)
£71,500

Platform Engineer (CCoE / Cloud Centre of Excellence)
£71,500

Platform Engineer (HPC / High Performance Compute Team)
£71,500

Principal Engineer (Site Reliability / SRE)
£103,500

QA Engineer (Genie)
£53,500

QA Engineer (KDMS)
£53,000

Scientific Curator
£47,500

Senior Platform Engineer (Developer Platform)  x2
£76,500

Senior QA Engineer
£55,500

Service Owner DDSR (12 month fixed term contract)
£113,500

Software Engineer
£71,500

Strategic Communications Lead (18 month fixed term contract)
£64,000

£65,500

 
to the population of engineer.
the aim is to have a config file where i store for GEL the job title, minimum salary so that can be edited or multiple config can be used.

