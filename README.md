# Project Charter

## Business background

* Who is the client, what business domain the client is in.<br>
Gydy TM is a strong player in the datascience-consult arena, providing end-to-end mlops pipelines customized for the customer.<br>
With variety of service from creating your simple machine-learning research to deployment at scale.<br>
We exemined our different customers and concluded that genereic pipelines will shorten their research time by up to 40%.<br>
# TO-DO add here some information

## Scope # TO-DO
* What data science solutions are we trying to build?
* What will we do?
* How is it going to be consumed by the customer?

## Personnel
* Our team:
	* Gydi:
		* Project lead
		* Data Engineer
		* Data scientist(s)
		* Customer support
	* Client:
		* Data administrator
		* Head of science
	
## Metrics
* What are the qualitative objectives? (e.g. reduce user churn)
* Gydy will reduce machine learning research time and will improve your baselines scores by providing generic pipelines.
* What is a quantifiable metric  (e.g. reduce the fraction of users with 4-week inactivity)
* Increase baseline models MAE, RMSE and more, reduce research & implementation time.
* Quantify what improvement in the values of the metrics are useful for the customer scenario (e.g. reduce the  fraction of users with 4-week inactivity by 20%) 
* Performing generic feature-selection, data reweighting and cleaning will ensure reduced deployment time and increase model scores.
* What is the baseline (current) value of the metric? (e.g. current fraction of users with 4-week inactivity = 60%)
# TO-DO
* How will we measure the metric? (e.g. A/B test on a specified subset for a specified period; or comparison of performance after implementation to baseline)
* We will compare our improved baseline with market common implementations with several datasets.

## Plan
* Phases (milestones), timeline, short description of what we'll do in each phase.
* Phase 1 - Getting datasets, EDA.
* Phase 2 - Getting baseline models.
* Phase 3 - Research for existing tools to answer our problem.
* Phase 4 - Focus on several tools and test them.
* Phase 5 - Create a pipeline with best tools.

## Architecture # TO-DO
* Data
  * What data do we expect? Raw data in the customer data sources (e.g. on-prem files, SQL, on-prem Hadoop etc.)
* Data movement from on-prem to Azure using ADF or other data movement tools (Azcopy, EventHub etc.) to move either
  * all the data, 
  * after some pre-aggregation on-prem,
  * Sampled data enough for modeling 

* What tools and data storage/analytics resources will be used in the solution e.g.,
  * ASA for stream aggregation
  * HDI/Hive/R/Python for feature construction, aggregation and sampling
  * AzureML for modeling and web service operationalization
* How will the score or operationalized web service(s) (RRS and/or BES) be consumed in the business workflow of the customer? If applicable, write down pseudo code for the APIs of the web service calls.
  * How will the customer use the model results to make decisions
  * Data movement pipeline in production
  * Make a 1 slide diagram showing the end to end data flow and decision architecture
    * If there is a substantial change in the customer's business workflow, make a before/after diagram showing the data flow.

## Communication
* Our team for this project:
	* Daniel Sabba
	* Yossi Gavriel
	* Jonathan Erell
	* Guy Sedan 
	
* Who are the contact persons on both sides?
* Yossi Gavriel
* DR. Ishay
