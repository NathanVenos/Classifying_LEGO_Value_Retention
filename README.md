# Secondary Market Analysis for LEGOs
We sought to classify whether a given LEGO set will retain its inflation-adjusted value over time, affording the owner the ability to enjoy the product and eventually sell it in the secondary market at cost or for a profit, so they can sustain their hobby while continually purchase new sets.

Data on approximately 3,800 sets was sourced from brickset.com and kaggle.com. Continuous and categorical features were engineered from data on the parts and themes of the sets to predict whether a set is currently worth as much or more than it original purchase price when adjusted for inflation. The final prediction accuracy was 81.3% using an XGBoost model. Hyperparameter tuning was performed using grid search, and the final results were cross-validated. To prevent data leakage, pipelines containing data standardization transformations, and where relevant class balancing transformations, were utilized throughout the grid search and cross-validation processes.

Presentation link: https://docs.google.com/presentation/d/1p3eqReoSEz2ut75-WD99ZIlFgdN_etg459Ask3iq8E0/edit?usp=sharing
