# -*- coding: utf-8 -*-
"""STA395_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1x7boO-eUqLsEVdD4czFwX-gA9-yzNKv3

# **STA395 PROJECT**

***Authors: Minh Nguyen, Nam Do***

# **Libraries**
"""

# Standard Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn

# Turn off future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, OneHotEncoder, PowerTransformer
from sklearn.metrics import f1_score, mean_squared_error
from scipy.stats import poisson, uniform
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.tree import plot_tree
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score
from sklearn.metrics import RocCurveDisplay
from sklearn.model_selection import cross_val_predict

"""# **Data Processing**"""

# Mount Google Drive to access files
from google.colab import drive
drive.mount('/content/drive')

songs = pd.read_csv("/content/drive/MyDrive/songs.csv", encoding='unicode_escape')
songs.info()

songs = songs.drop(["No.", "Language", "Song", "Year"], axis=1)

# Perform a 80-20 split
from sklearn.model_selection import train_test_split
train, test = train_test_split(songs, test_size=0.2)

train_X = train.drop(["Tonal"], axis=1)
train_y = train["Tonal"]
test_X = test.drop(["Tonal"], axis=1)
test_y = test["Tonal"]

## Separate numeric and categorical columns
songs_num_cols = train_X.select_dtypes(exclude=['object'])
songs_cat_cols = train_X.select_dtypes(include=['object'])

## Get names of numeric and categorical columns
num_col_names = songs_num_cols.columns.tolist()
cat_col_names = songs_cat_cols.columns.tolist()

"""# **Scatter Matrix**"""

pd.plotting.scatter_matrix(songs_num_cols)

## Seperate pipelines for numeric vs. cat vars
num_transformer = Pipeline([("scaler", StandardScaler()),
                            ("transformer", PowerTransformer()),
                            ("reducer", PCA())])
cat_transformer = Pipeline([("encoder", OneHotEncoder(sparse=False, handle_unknown='ignore'))])

## Preprocessing transformer allowing different actions for numeric and categorical vars
preprocessor = ColumnTransformer([
    ('num', num_transformer, num_col_names),
    ('cat', cat_transformer, cat_col_names)
])

"""# **Baseline Accuracy**"""

print("Baseline accuracy: ", len(train[train["Tonal"] == 0]) / len(train))

"""# **KNN**"""

pipe_knn = Pipeline([
    ("preprocessor", preprocessor),
    ("model", KNeighborsClassifier(n_neighbors = 15, weights='distance'))
])

parms_knn = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
             'preprocessor__num__reducer__n_components': [1, 2, 3, 4, 5, 6, 7],
             'model__n_neighbors': [5, 10, 15, 20],
             'model__weights': ['uniform', 'distance']}

grid_res_knn = GridSearchCV(pipe_knn, parms_knn, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_knn.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model__n_neighbors',
     'param_model__weights',
     'mean_test_score']].head(5)

"""# **SVM**"""

pipe_svm = Pipeline([
    ("preprocessor", preprocessor),
    ("model", SVC())
])

parms_svm = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
             'preprocessor__num__reducer__n_components': [1, 2, 3, 4, 5, 6, 7],
             'model__kernel': ['linear', 'poly', 'rbf'],
             'model__C': [10, 1, .1, .01]}

grid_res_svm = GridSearchCV(pipe_svm, parms_svm, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_svm.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model__kernel',
     'param_model__C',
     'mean_test_score']].head(5)

"""# **Logistic Regression**"""

pipe_log = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression())
])

parms_log = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
              'preprocessor__num__reducer__n_components': [1, 2, 3, 4, 5, 6, 7],
              'model': [LogisticRegression(penalty = None, solver = "newton-cg"),
                        LogisticRegression(penalty = "l2", solver = "newton-cg"),
                        LogisticRegression(penalty = "l2", solver = "liblinear"),
                        LogisticRegression(penalty = "l1", solver = "liblinear"),
                        ]}

grid_res_log = GridSearchCV(pipe_log, parms_log, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_log.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model',
     'mean_test_score']].head(5)

"""# **MLP**"""

pipe_mlp = Pipeline([
    ("preprocessor", preprocessor),
    ("model", MLPClassifier(hidden_layer_sizes=(4,), activation='logistic', solver='lbfgs', learning_rate='constant', learning_rate_init=0.1, max_iter=1000))
])

parms_mlp = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
             'preprocessor__num__reducer__n_components': [1, 2, 3, 4, 5, 6, 7],
             "model__hidden_layer_sizes": [(3,), (4,), (5,)],
             "model__batch_size": [10, 15, 20, 25]}

grid_res_mlp = GridSearchCV(pipe_mlp, parms_mlp, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_mlp.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model__hidden_layer_sizes',
     'param_model__batch_size',
     'mean_test_score']].head(5)

"""# **XGBoost**"""

import xgboost as xgb

pipe_xgb = Pipeline([
    ("preprocessor", preprocessor),
    ("model", xgb.XGBClassifier(eval_metric='error', use_label_encoder=False))
])
parms_xgb = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
             'preprocessor__num__reducer__n_components': [1, 2, 3, 4, 5, 6, 7],
             'model__learning_rate': [.01, .1, .2, .5],
             'model__max_depth': [1, 2, 3, 4]}

grid_res_xgb = GridSearchCV(pipe_xgb, parms_xgb, cv=5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_xgb.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model__learning_rate',
     'param_model__max_depth',
     'mean_test_score']].head(5)

"""# **Decision Tree**"""

pipe_tree = Pipeline([
    ("preprocessor", preprocessor),
    ("model", DecisionTreeClassifier())
])

parms_tree = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
              'preprocessor__num__reducer__n_components': [1, 2, 3, 4, 5, 6, 7],
              'model__max_depth': [2, 3, 4],
              'model__min_samples_split': [5, 10, 15, 20]}

grid_res_tree = GridSearchCV(pipe_tree, parms_tree, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_tree.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model__max_depth',
     'param_model__min_samples_split',
     'mean_test_score']].head(5)

"""# **Random Forest**"""

pipe_forest = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier())
])

parms_forest = {'preprocessor__num__scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
                'preprocessor__num__reducer__n_components': [1, 2, 3],
                "model__max_depth": [2, 3],
                "model__min_samples_split": [5, 10, 15],
                "model__max_features": [2, 3, 4],
                "model__n_estimators": [30, 50, 70]}

grid_res_forest = GridSearchCV(pipe_forest, parms_forest, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_forest.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_preprocessor__num__scaler',
     'param_preprocessor__num__reducer__n_components',
     'param_model__max_depth',
     'param_model__min_samples_split',
     'param_model__max_features',
     'param_model__n_estimators',
     'mean_test_score']].head(5)

"""# **Compare 7 Models**"""

pipe_7 = Pipeline([
    ("model", KNeighborsClassifier())
])

parms_7 = {"model": [grid_res_knn.best_estimator_,
                     grid_res_svm.best_estimator_,
                     grid_res_log.best_estimator_,
                     grid_res_mlp.best_estimator_,
                     grid_res_xgb.best_estimator_,
                     grid_res_tree.best_estimator_,
                     grid_res_forest.best_estimator_]}

grid_res_7 = GridSearchCV(pipe_7, parms_7, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_7.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_model',
     'mean_test_score']]

"""**The best-performing models on the training set are Logistic Regression, XGBoost, and SVM, with the cross-validated training accuracies of 0.65, 0.64, and 0.63, respectively.**

# **Ensemble**
"""

## Defining the individual models
model1 = grid_res_log.best_estimator_
model2 = grid_res_xgb.best_estimator_
model3 = grid_res_svm.best_estimator_

## Create the ensemble
my_ensemble = VotingClassifier(estimators=[('log', model1), ('xgb', model2), ('svm', model2)], voting='hard', weights=[1, 1, 1])

## Some tuning parameters to search over
parms_ensemble = {'voting': ['soft', 'hard'],
                  'weights': [[1, 1, .8], [1, .8, 1], [.8, 1, 1], [1, 1, .6], [1, .6, 1], [.6, 1, 1], [.6, .8, 1], [.8, .6, 1], [.6, 1, .8], [.8, 1, .6], [1, .6, .8], [1, .8, .6]]}

grid_res_ensemble = GridSearchCV(my_ensemble, parms_ensemble, cv=5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_ensemble.cv_results_).sort_values('mean_test_score', ascending=False)[['param_voting', 'param_weights', 'mean_test_score']]

"""# **Compare 8 Model/Ensemble**"""

pipe_8 = Pipeline([
    ("model", KNeighborsClassifier())
])

parms_8 = {"model": [grid_res_knn.best_estimator_,
                     grid_res_svm.best_estimator_,
                     grid_res_log.best_estimator_,
                     grid_res_mlp.best_estimator_,
                     grid_res_xgb.best_estimator_,
                     grid_res_tree.best_estimator_,
                     grid_res_forest.best_estimator_,
                     grid_res_ensemble.best_estimator_]}

grid_res_8 = GridSearchCV(pipe_8, parms_8, cv = 5, scoring = 'accuracy').fit(train_X, train_y)
pd.DataFrame(grid_res_8.cv_results_).sort_values('mean_test_score', ascending=False)[
    ['param_model',
     'mean_test_score']]

print(grid_res_8.best_estimator_)

"""**The best-performing model in the training set is Logistic Regression, with a cross-validated training accuracy of 0.65.**

# **Confusion Matrix**
"""

## Display confusion matrix on training set
ConfusionMatrixDisplay.from_predictions(train_y, grid_res_8.predict(train_X), labels = [1, 0])
plt.show()

## Display confusion matrix on test set
ConfusionMatrixDisplay.from_predictions(test_y, grid_res_8.predict(test_X), labels = [1, 0])
plt.show()

"""# **ROC AUC**"""

train_y_pred_prob = cross_val_predict(estimator = grid_res_8.best_estimator_, X = train_X, y = train_y, cv = 5, method = 'predict_proba')

# ROC curve plotting:
RocCurveDisplay.from_predictions(train_y, train_y_pred_prob[:,1])
plt.show()

"""# **Testing Accuracy**"""

print("Accuracy on the test set: ", accuracy_score(test_y, grid_res_8.predict(test_X)))

"""**The model generalizes well to new data.**"""