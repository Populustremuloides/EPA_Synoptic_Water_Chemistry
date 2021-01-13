# -*- coding: utf-8 -*-
"""Lake Model.ipynb

Automatically generated by Colaboratory.

# Lake Model

You can run individual cells by pressing shift-enter. Alternatively you can run the entire notebook by going to Runtime --> Restart and run all.

## Upload Data
Before running the notebook upload the csv files into local memory.
1. Click on the folder icon on the left.
2. Either click "Upload" at the top or drag the files into the file manager.

## Lake Data Summary
"""

import pandas as pd
from sklearn.inspection import plot_partial_dependence
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt
from sklearn import svm
plt.style.use("seaborn-poster")


for use_leverage in [True, False]:


    if use_leverage:
        lake_data = pd.read_csv('Leverage_Lake_Data_ML.csv')
    else:
        lake_data = pd.read_csv('Lake_Data_ML.csv')

    lake_data = lake_data.drop(lake_data.columns[0], axis=1)  # remove extra index col

    lake_data.head()

    lake_data.info()

    lake_data.describe()

    lake_data.isnull().sum()

    import numpy as np

    print("Number of infinite values per column")
    for col in lake_data:
        num_inf = lake_data.loc[lake_data[col] == np.inf, col].count()
        print(f"{col}\t\t{num_inf}")

    """## Data preprocessing for training"""

    lake_data = lake_data.drop(columns=['lat', 'long', 'siteid'])
    if use_leverage:
        lake_data = lake_data.drop(columns=['area'])
    lake_data.columns.values

    """Replace any infinite values with NaN"""

    # generic solution
    for col in lake_data:
        lake_data.loc[lake_data[col] == np.inf, col] = np.nan

    # # for the one col with inf values
    # lake_data.loc[lake_data['lev_no3'] == np.inf, 'lev_no3'] = np.nan

    print("Number of infinite values per column")
    for col in lake_data:
        num_inf = lake_data.loc[lake_data[col] == np.inf, col].count()
        print(f"{col}\t\t{num_inf}")

    """Remove instances with an undefined target."""

    if use_leverage:
        targets = ['lev_doc', 'lev_no3', 'lev_tn', 'lev_tp']
    else:
        targets = ['doc', 'no3', 'tn', 'tp']
    # lake_data = lake_data[lake_data["lev_doc"] < 100] # remove outliers from doc
    # print(lake_data["lev_doc"])
    # plt.hist(lake_data["lev_doc"])
    # plt.show()
    lake_data = lake_data.dropna(subset=targets)

    """### Split into training and validation sets by 'era'."""

    # lake_data['era'].unique()

    # lake_train_data = lake_data.loc[lake_data['era'] == 'Year2007']._get_numeric_data()
    # lake_valid_data = lake_data.loc[lake_data['era'] == 'Year2012']._get_numeric_data()
    # print(f'training data has {len(lake_train_data)} observations')
    # print(f'validation data has {len(lake_valid_data)} observations')

    """### Split into random training and validation sets.

    Convert 'era' with unique values 'Year2008' and 'Year2004' into something numeric for the model to use.
    """

    lake_data.loc[lake_data['era'] == 'Year2007', 'era'] = 0
    lake_data.loc[lake_data['era'] == 'Year2012', 'era'] = 1

    from sklearn.model_selection import train_test_split

    #normalize the data PRIOR to splitting
    #((X_train - X_train.min()) / (X_train.max() - X_train.min()))
    print(lake_data.columns)
    #lake_data = lake_data[lake_data[""] < 0.6]
    lake_data = (lake_data - lake_data.min()) / (lake_data.max() - lake_data.min())

    lake_train_data, lake_valid_data = train_test_split(lake_data, test_size=0.2, random_state=0)

    """### Impute missing values

    There are multiple ways to do this. This function is a simple imputation that puts the median for the whole set in. A better way to do this would be to go through the sites and use a median/mean from only its own site. Perhaps dropping sites that never measure the six missing features.
    """

    from sklearn.impute import SimpleImputer

    # FIXME: I don't really like that we are imputing. I'd rather get rid of the data.
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

    lake_train_data, lake_valid_data = missing_val_strategy(lake_train_data, lake_valid_data)

    print(f'training data has {lake_train_data.isnull().sum().sum()} NAN values')
    print(f'validation data has {lake_valid_data.isnull().sum().sum()} NAN values')

    print(f'training data has {len(lake_train_data)} observations')
    print(f'validation data has {len(lake_valid_data)} observations')

    """### Separate targets from the rest of the data and normalize non-targets."""

    #lake_train_data = (lake_train_data - lake_train_data.min()) / (lake_train_data.max() - lake_train_data.min())

    X_train = lake_train_data.drop(targets, axis=1)
    Y_train = lake_train_data[targets]
    print(f'X_train has {len(X_train.columns)} columns')
    print(f'Y_train has {len(Y_train.columns)} columns')

    X_valid = lake_valid_data.drop(targets, axis=1)
    Y_valid = lake_valid_data[targets]
    print(f'X_valid has {len(X_valid.columns)} columns')
    print(f'Y_valid has {len(Y_valid.columns)} columns')

    # normalize non-target columns
    #X_train = ((X_train - X_train.min()) / (X_train.max() - X_train.min()))  # norm train 0-1
    #X_valid = ((X_valid - X_valid.min()) / (X_valid.max() - X_valid.min()))  # norm valid according to train
    #X_train.describe()  # show normalization

    """### Resampling
    
    These distribution plots show how skewed the data are.
    """

    # import seaborn as sns

    # for target in targets:
    #     ax = sns.distplot(
    #         lake_data[target],
    #         hist=True,
    #         kde=False,
    #         rug=True,
    #         )
    #     ax.set(xlabel='target values', ylabel = 'occurrence', title=f'Distribution of {target}')
    #     plt.show()

    """The model will likely mode collapse, or learn only to predict the most likely target value without taking the features into account. 
    
    There are many ways to rebalance data. One way is to reweight the probability with which each sample is considered so that it is more even.
    """

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

    """##Random Forest"""

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.ensemble import GradientBoostingRegressor
    import numpy as np
    import matplotlib.pyplot as plt

    colors = ["#01579B"]
    # single_color = sns.color_palette(colors)

    colors = ["#01579B", "#547893"]
    # palette = sns.color_palette(colors)


    # print("""Note on printed results:
    # L1 Error is the average absolute difference between the real target
    # values and the model's target values. The smaller the value the more
    # accurate the model. So, for example if the L1 Error for the validation
    # data is 0.05 that means that when the model attempted to predict the
    # target value on novel data it was off by an average of 0.05.

    # L2 Error is the average of the *squared* difference between the real
    # target values and the model's target values.



    # """)
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.experimental import enable_hist_gradient_boosting
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.datasets import make_regression

    dataDict = {
       "model_type":[],
        "nutrient":[],
        "data_type":[],
        "r^2":[],
        "times_better_than_random":[]
    }

    for col in X_train.columns:
        dataDict[col] = []


    # plt.clf()
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


        #        plt.title("partial dependencies for " + str(target) + "using MLPRegressor, hls=1000")

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

            L1_random = np.average(np.abs(np.subtract(random_pred, Y_valid[target])))
            L2_random = np.average(np.square(np.subtract(random_pred, Y_valid[target])))
            percent_error = (np.subtract(pred_train, Y_train[target]) / Y_train[target])

            lr = LinearRegression()
            x = np.asarray(Y_valid[target])
            x = x.reshape(-1,1)
            lr.fit(x, pred_valid)
            print(f'Results for target {target}:')
            print(modelType)
            print("linear regression score")
            print(lr.score(x, pred_valid))

            print(X_train)
            feats = list(X_train.columns)
            #input("")

            dataDict["model_type"].append(modelType)
            dataDict["nutrient"].append(target)
            dataDict["r^2"].append(lr.score(x, pred_valid))
            dataDict["times_better_than_random"].append(L1_random / L1_valid)
            if use_leverage:
                dataDict["data_type"].append("lake_leverage")
            else:
                dataDict["data_type"].append("lake_normal")
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

                outDir = "C:\\Users\\BCBrown\\Desktop\\Abbott\\EPASynoptic\\Lake2\\"
                name = outDir + target + "_partialDependenceOn_" + feats[k]
                name = name + "_lake_" + modelType
                if use_leverage:
                    name = name + "_lev.svg"
                else:
                    name = name + "_noLev.svg"
                
                plt.title(target + " partial dependence on " + feats[k])
                plt.savefig(name, format="svg")
                plt.clf()

            # plt.scatter(Y_valid[target], pred_valid)
            # plt.ylabel("prediciton")
            # plt.xlabel("target")

            # plt.title("prediction vs target, r^2: " + str(lr.score(x, pred_valid)))
            # plt.show()
            # calculate errors

            print(f'VALIDATION L1 Error: {L1_valid:.6f} vs RANDOM {L1_random:.6f}')
            print(f'VALIDATION L2 Error: {L2_valid:.6f} vs RANDOM {L2_random:.6f}')
            print(f'TRAINING   L1 Error: {L1_train:.6f}')
            print(f'TRAINING   L2 Error: {L2_train:.6f}')
            print()

            sorted_inds = np.argsort(Y_valid[target])  # sort them for easy viewing

            results = pd.DataFrame({
                'predictions': pred_valid[sorted_inds],
                'target values': Y_valid[target].values[sorted_inds],
                # 'random guesses': random_pred[sorted_inds]  # uncomment to see what random guesses looks like
            })

    importancesDf = pd.DataFrame.from_dict(dataDict)
    if use_leverage:
        importancesDf.to_csv("feature_importances_lake_yes_leverage.csv")
    else:
        importancesDf.to_csv("feature_importances_lake_no_leverage.csv")
