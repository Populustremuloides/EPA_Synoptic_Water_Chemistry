# -*- coding: utf-8 -*-
"""Stream Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F-fLMbC7RWOZvTKbJdTPmP6SE8KYNi0A

# TODO LIST
- [x] resample data
- [ ] pdp plots? 
- [ ] k-fold cross val 
- [x] improve plots? 
- [ ] once final data is decided remove `use_leverage` var

# Stream Model

You can run individual cells by pressing shift-enter. Alternatively you can run the entire notebook by going to Runtime --> Restart and run all.

## Upload Data
Before running the notebook upload the csv files into local memory.
1. Click on the folder icon on the left.
2. Either click "Upload" at the top or drag the files into the file manager.

## Stream Data Summary
"""

import pandas as pd
import matplotlib.pyplot as plt

for use_leverage in [True, False]:

    plt.style.use("seaborn-poster")

    if use_leverage:
        stream_data = pd.read_csv('Leverage_Stream_Data_ML.csv')
    else:
        stream_data = pd.read_csv('Stream_Data_ML.csv')

    stream_data = stream_data.drop(stream_data.columns[0], axis=1)  # remove extra index col

    stream_data.head()

    stream_data.info()

    stream_data.describe()

    print("Number of null values per column")
    stream_data.isnull().sum()

    import numpy as np

    print("Number of infinite values per column")
    for col in stream_data:
        num_inf = stream_data.loc[stream_data[col] == np.inf, col].count()
        print(f"{col}\t\t{num_inf}")

    """## Data preprocessing for training

    Remove unwanted columns.
    """

    stream_data = stream_data.drop(columns=['lat', 'long', 'siteid', 'roads'])
    if use_leverage:
        stream_data = stream_data.drop(columns=['area'])
    stream_data.columns.values

    """Replace any infinite values with NaN"""

    # generic solution
    for col in stream_data:
        stream_data.loc[stream_data[col] == np.inf, col] = np.nan

    # # for the one col with inf values
    # stream_data.loc[stream_data['lev_no3'] == np.inf, 'lev_no3'] = np.nan

    print("Number of infinite values per column")
    for col in stream_data:
        num_inf = stream_data[col].loc[stream_data[col] == np.inf].count()
        print(f"{col}\t\t{num_inf}")

    """Remove instances that have an undefined target."""

    if use_leverage:
        targets = ['lev_doc', 'lev_no3', 'lev_tn', 'lev_tp']
    else:
        targets = ['doc', 'no3', 'tn', 'tp']
    
    stream_data = stream_data.dropna(subset=targets)

    """#### Split into training and validation sets by 'era'."""

    # stream_data['era'].unique()

    # stream_train_data = stream_data.loc[stream_data['era'] == 'Year2004']._get_numeric_data()
    # stream_valid_data = stream_data.loc[stream_data['era'] == 'Year2008']._get_numeric_data()
    # print(f'training data has {len(stream_train_data)} observations')
    # print(f'validation data has {len(stream_valid_data)} observations')

    """### Split into random training and validation sets.

    Convert 'era' with unique values 'Year2008' and 'Year2004' into something numeric for the model to use.
    """

    stream_data.loc[stream_data['era'] == 'Year2004', 'era'] = 0
    stream_data.loc[stream_data['era'] == 'Year2008', 'era'] = 1

    from sklearn.model_selection import train_test_split

    # normalize the data
    straem_data = (stream_data - stream_data.min()) / (stream_data.max() - stream_data.min())
    stream_train_data, stream_valid_data = train_test_split(stream_data, test_size=0.2, random_state=0)

    """### Impute missing values

    There are multiple ways to do this. This function is a simple imputation that puts the median for the whole set in. A better way to do this would be to go through the sites and use a median/mean from only its own site. Perhaps dropping sites that never measure the six missing features.
    """

    from sklearn.impute import SimpleImputer

    def simple_impute(data_train, data_valid):
        imputer = SimpleImputer(strategy='median')

        # impute missing vals in training data
        imp_train = pd.DataFrame(imputer.fit_transform(data_train))
        imp_train.columns = data_train.columns  # replace cols after imp
        imp_train.index = data_train.index  # replace ind after imp

        # impute missing vals in validation data
        imp_valid = pd.DataFrame(imputer.transform(data_valid))
        imp_valid.columns = data_valid.columns
        imp_valid.index = data_valid.index

        return imp_train, imp_valid

    """Another option is simply to remove all observations that have missing values. The way I learned, this is discouraged because by doing this you are throwing out valuable data. Theoretically imputation should let you keep the data you have without messing things up."""

    def remove_missing_values(data_train, data_valid):
        return data_train.dropna(), data_valid.dropna()

    """Pick which way you would like to deal with missing values."""

    # missing_val_strategy = simple_impute
    missing_val_strategy = remove_missing_values

    stream_train_data, stream_valid_data = missing_val_strategy(stream_train_data, stream_valid_data)

    print(f'training data has {stream_train_data.isnull().sum().sum()} NAN values')
    print(f'validation data has {stream_valid_data.isnull().sum().sum()} NAN values')

    print(f'training data has {len(stream_train_data)} observations')
    print(f'validation data has {len(stream_valid_data)} observations')

    """### Separate targets from the rest of the data and normalize non-targets."""

    X_train = stream_train_data.drop(targets, axis=1)
    Y_train = stream_train_data[targets]
    print(f'X_train has {len(X_train.columns)} columns')
    print(f'Y_train has {len(Y_train.columns)} columns')

    X_valid = stream_valid_data.drop(targets, axis=1)
    Y_valid = stream_valid_data[targets]
    print(f'X_valid has {len(X_valid.columns)} columns')
    print(f'Y_valid has {len(Y_valid.columns)} columns')

    # normalize non-target columns
    # X_train = ((X_train - X_train.min()) / (X_train.max() - X_train.min()))  # norm train 0-1
    # X_valid = ((X_valid - X_valid.min()) / (X_valid.max() - X_valid.min()))  # norm valid according to train
    X_train.describe()  # show normalization

    """### Resampling

    These distribution plots show how skewed the data are.
    """

    import matplotlib.pyplot as plt

    # for target in targets:
        # ax = sns.distplot(
        #     stream_data[target],
        #     hist=True,
        #     kde=False,
        #     rug=True,
        #     )
        # ax.set(xlabel='target values', ylabel = 'occurrence', title=f'Distribution of {target}')
        # plt.show()


    from collections import Counter

    weights = {}
    for target in targets:

        num_bins = 1000

        # create bin edges
        bins = np.linspace(
            start=Y_train[target].values.min(),
            stop=Y_train[target].values.max(),
            num=num_bins
        )

        # sort target values into bins
        bin_inds = np.digitize(Y_train[target], bins)

        # get the number of values in each bin
        frequency = Counter(bin_inds)

        # give each target value a weight based on its bin
        def calc_weight(bin_number):
            return 1 / frequency[bin_number]

        target_weights = np.array(list(map(calc_weight, bin_inds)))
        weights[target] = target_weights

    """## Random Forest"""

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.experimental import enable_hist_gradient_boosting
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.datasets import make_regression
    from sklearn.inspection import plot_partial_dependence
    from sklearn.linear_model import LinearRegression
    from sklearn.neural_network import MLPRegressor

    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.inspection import plot_partial_dependence


    colors = ["#01579B"]

    colors = ["#01579B", "#547893"]

    dataDict = {
       "model_type":[],
        "nutrient":[],
        "data_type":[],
        "r^2":[],
        "times_better_than_random":[]
    }

    for col in X_train.columns:
        dataDict[col] = []

    print("""Note on printed results:
    L1 Error is the average absolute difference between the real target
    values and the model's target values. The smaller the value the more
    accurate the model. So, for example if the L1 Error for the validation
    data is 0.05 that means that when the model attempted to predict the
    target value on novel data it was off by an average of 0.05. 

    L2 Error is the average of the *squared* difference between the real
    target values and the model's target values. 



    """)

    print(targets)

    modelType = ""
    for i in range(0,4):
        for target in targets:
            # create model and fit to data
            if i == 0:
                model = MLPRegressor(hidden_layer_sizes=1000, warm_start=True)
                modelType = "MLP"
            elif i == 1:
                model = GradientBoostingRegressor(n_estimators=100)
                modelType = "GBR"
            elif i == 2:
                model = RandomForestRegressor(random_state=0) # Keeper
                modelType = "RFR"
            elif i == 3:
                model = DecisionTreeRegressor(random_state=0) # did the best so far
                modelType = "DTR"
                # model = svm.SVR(kernel="poly", gamma=0.1, epsilon =0.1) # didn't work

            if i == 1 or i == 2 or i == 3:
                model.fit(X_train, Y_train[target], sample_weight=weights[target])
            else:
                model.fit(X_train, Y_train[target])#, sample_weight=weights[target])

            # obtain training predictions
            pred_train = model.predict(X_train)
            L1_train = np.average(np.abs(np.subtract(pred_train, Y_train[target])))
            L2_train = np.average(np.square(np.subtract(pred_train, Y_train[target])))

            # obtain validation predictions
            pred_valid = model.predict(X_valid)
            L1_valid = np.average(np.abs(np.subtract(pred_valid, Y_valid[target])))
            L2_valid = np.average(np.square(np.subtract(pred_valid, Y_valid[target])))

            # make random predictions according to mean and variation for comparison
            mean = np.average(Y_train[target])
            stdev = np.std(Y_train[target])
            random_pred = np.random.normal(mean, stdev, len(Y_valid[target]))

            # calculate errors
            L1_random = np.average(np.abs(np.subtract(random_pred, Y_valid[target])))
            L2_random = np.average(np.square(np.subtract(random_pred, Y_valid[target])))
            percent_error = (np.subtract(pred_train, Y_train[target]) / Y_train[target])

            # print(f'VALIDATION L1 Error: {L1_valid:.6f} vs RANDOM {L1_random:.6f}')
            # print(f'VALIDATION L2 Error: {L2_valid:.6f} vs RANDOM {L2_random:.6f}')
            # print(f'TRAINING   L1 Error: {L1_train:.6f}')
            # print(f'TRAINING   L2 Error: {L2_train:.6f}')
            # print()

            lr = LinearRegression()
            x = np.asarray(Y_valid[target])
            x = x.reshape(-1, 1)
            lr.fit(x, pred_valid)
            print(f'Results for target {target}:')
            print(modelType)
            print("linear regression score")
            print(lr.score(x, pred_valid))



            print(X_train)
            feats = list(X_train.columns)

            dataDict["model_type"].append(modelType)
            dataDict["nutrient"].append(target)
            dataDict["r^2"].append(lr.score(x, pred_valid))
            dataDict["times_better_than_random"].append(L1_random / L1_valid)
            if use_leverage:
                dataDict["data_type"].append("stream_leverage")
            else:
                dataDict["data_type"].append("stream_normal")

            if i > 0:
                for j in range(len(feats)):
                    ft = feats[j]
                    imp = model.feature_importances_[j]
                    dataDict[ft].append(imp)
            else:
                for j in range(len(feats)):
                    ft = feats[j]
                    dataDict[ft].append(np.nan)

            for k in range(0,9):
                print(feats[k])
                print(k)
                plot_partial_dependence(model, X_train, features=[k], feature_names=feats)

                outDir = "C:\\Users\\BCBrown\\Desktop\\Abbott\\EPASynoptic\\Stream2\\"
                name = outDir + target + "_partialDependenceOn_" + feats[k]
                name = name + "_stream_" + modelType
                if use_leverage:
                    name = name + "_lev.svg"
                else:
                    name = name + "_noLev.svg"

                plt.title(target + " partial dependence on " + feats[k])
                plt.savefig(name, format="svg")
                plt.clf()


            # plot_partial_dependence(model, X_train, features=list(range(0, 9)), feature_names=feats)
            # plt.show()
            # sorted_inds = np.argsort(Y_valid[target])  # sort them for easy viewing

            # results = pd.DataFrame({
            #     'predictions': pred_valid[sorted_inds],
            #     'target values': Y_valid[target].values[sorted_inds],
            #     'random guesses': random_pred[sorted_inds]  # uncomment to see what random guesses looks like
            # })
           #
        # print('\nPercent Error')
        # ax = sns.distplot(
        #     percent_error[percent_error < 10e10],
        #     hist=True,
        #     kde=False,
        #     rug=True,
        # )
        # plt.show()
        # plt.scatter(x=Y_train[target], y=percent_error)
        # plt.show()
        #
        # print('\nPercent Error outliers removed')
        # temp = pd.DataFrame({
        #     'target value': Y_train[target],
        #     'percent error': percent_error,
        # })
        # temp.loc[temp['percent error'] == np.inf, 'percent error'] = np.nan
        # temp = temp.dropna()
        #
        # mean = np.mean(temp['percent error'])
        # stdev = np.std(temp['percent error'])
        # print(mean, stdev)
        # temp = temp[temp['percent error'] < mean + 5 * stdev]
        # temp = temp[temp['percent error'] > mean - 5 * stdev]
        # ax = sns.scatterplot(
        #     data=temp,
        #     palette=palette)
        # plt.show()
        #
        # print('\nAll model predictions compared to their targets (and sorted by target)')
        # plt.figure(figsize=(14,5))
        # ax = sns.scatterplot(
        #     data=results,
        #     palette=palette)
        # ax.set(xlabel="x label", ylabel = "y label", title="Title")
        # plt.savefig(f'{target}-all-results.pdf')
        # plt.show()

        # print('\nRandom 100')
        # plt.figure(figsize=(14,5))
        # ax = sns.scatterplot(
        #     data=results.iloc[np.random.randint(0, len(pred_valid), 50)],
        #     palette=palette)
        # ax.set(xlabel="x label", ylabel = "y label", title="Title")
        # plt.savefig(f'./{target}-100-results.pdf')
        # plt.show()

        # feature_importances = model.feature_importances_ * 100  # turn into percentage
        # sorted_inds = np.argsort(feature_importances)  # sort them for easy viewing

        # feature_importance_data = pd.DataFrame({
        #     'features': X_train.columns.values[sorted_inds],
        #     'importance amount':feature_importances[sorted_inds]})

        # plt.figure(figsize=(14,5))
        # ax = sns.barplot(
        #     x='features',
        #     y='importance amount',
        #     data=feature_importance_data,
        #     palette=single_color)
        # ax.set(xlabel="x label", ylabel = "y label", title="Title")
        # plt.savefig(f'./{target}-feature-imp.pdf')
        # plt.show()
    
        # plt.figure(figsize=(14, 14))
        # ax = plt.gca()
        # plot_partial_dependence(model, X_train, features=[0, 1, 2, 3, 4, 5, 6, 7, 8], n_cols=3, ax=ax)
        # plt.show()

        # print('\nDistribution of target')
        # ax = sns.distplot(
        #     stream_data[target],
        #     hist=True,
        #     kde=False,
        #     rug=True,
        # )
        # ax.set(xlabel="x label", ylabel = "y label", title="Title")
        # plt.savefig(f'./{target}-distribution.pdf')
        # plt.show()

        # print('\n\n')

    importancesDf = pd.DataFrame.from_dict(dataDict)
    if use_leverage:
        importancesDf.to_csv("feature_importances_stream_yes_leverage.csv")
    else:
        importancesDf.to_csv("feature_importances_stream_no_leverage.csv")