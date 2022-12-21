# Project Charter

## Business background
**Who is the client, what business domain the client is in?**<br>
Gydy TM is a strong player in the datascience-consult arena, providing end-to-end mlops pipelines customized for the customer.<br>
With variety of service from creating your simple machine-learning research to deployment at scale.<br>
We exemined our different customers and concluded that genereic pipelines will shorten their research time by up to 40%.<br>

## Scope
**What data science solutions are we trying to build?**<br>
As a solution to our research question, we aim to develop generic pipeline that will clean, preprocess and transform all data types.<br>
further more we wish to imporve our data with feature selection techniques and data resampling/reweighting in order to imporve our baselines.<br>
**What will we do?**   <br>

In our pipeline, we will also check the fairness of the model. The data we use for modeling is mostly a reflection of the real world, and the real world can be biased, so the data and therefore the model will likely reflect that bias. To check the fairness of the model, we will examine each feature of our dataset to see if it is biased by a subclass of that feature. For example, we might define a group based on the sex of the sample, and a subgroup based on age. We might then define the privileged subgroup as old males, who may be privileged in cases of house pricing.

To check for bias in each feature, we will use the Dalex package to measure fairness. If we detect unfairness, we will try one or both of the following options:

 - Reweighting the data: We will obtain weights for the model training pipeline and mitigate bias in statistical parity. This method will produce weights for the given subgroup for each class.

 - Resampling the data: We will return indices of observations for the data. Similar to reweighting, this method computes the desired number of observations as if the protected variable were independent of the outcome variable (y), and based on this, it determines if the subgroup with a certain class (favorable or not) should be more or less numerous. It then performs oversampling or undersampling, depending on the case.

By using one or both of these options, we can build a more balanced dataset for the model training pipeline.

We'll also use outliers detection and removal.
Outliers are data points significantly different from most of the other data points in a dataset.
The outlier's detection is performed per feature separately and is possible only in continuous values. If some feature of the data point is detected as an outlier, this data point will be determined as an outlier.
Once we have identified the outliers in our dataset, we will choose to remove them if they are causing problems with the predictions.
For example, removing outliers may be appropriate if they skew the results. However, we should be careful about removing outliers, as they may contain valuable information about our data.

So, we'll check whether removing the outliers improves results in the pipeline. 
There are a few different ways to identify and remove outliers from a dataset.

We'll examine two well-known methods for outliers' detection and use the one that will give us the best results: 
1. Z-score: The z-score measures how many standard deviations a value is from the mean. If the z-score of a value is greater than a certain threshold (commonly 3 or 4), it can be considered an outlier.
2. Interquartile range (IQR): 
The IQR is a measure of the dispersion of a dataset and can be used to identify values that fall outside the range of "typical" values.
To calculate the quartiles of a dataset, we first need to arrange the values in numerical order.
Quartiles are values that divide a dataset into four equal parts. The first quartile (Q1) is the value that separates the lowest 25% of the data from the highest 75%. The second quartile, or median, is the value that separates the lowest 50% of the data from the highest 50%. The third quartile (Q3) is the value that separates the lowest 75% of the data from the highest 25%.

	So, we'll use the following formulas to calculate the quartiles:

	Q1 = (n+1) * (1/4)

	Median = (n+1) * (1/2)

	Q3 = (n+1) * (3/4)

	Where n is the number of values in the dataset.
	Outliers can then be identified as values that are more than x times the IQR below Q1 or above Q3.


**How is it going to be consumed by the customer?**<br>
To all of our cool customers, you can simply copy our pipeline implementation and run it in your environments.<br>
Playing with different pipeline params is advised !<br>

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
**What are the qualitative objectives?**<br>
We will provide number of possible qualitative objectives: <br>
* Providing a more scalable ML framework <br>
* Less biased predictor <br>

**What are the quantifiable metric?** <br>
We will provide number of possible qualitative metrics: <br>
* Reducing machine learning research time <br>
* Improvement of your baselines scores by providing generic pipelines <br>
* Increase baseline models' MAE <br>
* Quantify what improvement in the values of the metrics are useful for the customer scenario <br>
* Performing generic feature-selection, data reweighting and cleaning will ensure reduced deployment time and increase model scores <br>

**What is the baseline (current) value of the metric?**<br>
We benchmark xgb regressor with two datasets, boston house price (2.87 MAE) and french motor (0.003 MAE) <br>

**How will we measure the metric?**<br>
We will compare our improved baseline with market common implementations with several datasets.<br>

## Plan
* Phases (milestones), timeline, short description of what we'll do in each phase.
* Phase 1 - Getting datasets, EDA.
* Phase 2 - Getting baseline models.
* Phase 3 - Research for existing tools to answer our problem.
* Phase 4 - Focus on several tools and test them.
* Phase 5 - Create a pipeline with best tools.

## Architecture
* Data
  * What data do we expect? Raw data in the customer data sources (e.g. on-prem files, SQL, on-prem Hadoop etc.)
  * We expact that customer's data will be able to fit in a dataframe (csv, parquet, json etc) and on prem files, further integration with spark will be supported.
* Data movement from on-prem to Azure using ADF or other data movement tools (Azcopy, EventHub etc.) to move either
  * Sampled data enough for modeling 

* What tools and data storage/analytics resources will be used in the solution e.g.,
  * Pandas for data storage
  * SKlearn's stat filters and models.
  * SKlearn's pipeline for pipeline creation
* How will the score or operationalized web service(s) (RRS and/or BES) be consumed in the business workflow of the customer? If applicable, write down pseudo code for the APIs of the web service calls.
our pipeline will be fused in each of the data-scientists day-to-day work, with easy implementation and customization.
  * How will the customer use the model results to make decisions
  * The customer will view model scores and will decide whether to choose different pipeline params or not.
  * Data movement pipeline in production
  * In production, a serving function / serving graph holding the pipeline implementation for easy data manipulation in production.
  * When files are stored on cloud providers, proper credentials has to be declared.
  * Make a 1 slide diagram showing the end to end data flow and decision architecture
  ![my diagram](my_diagram.png)
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
