library(ggplot2)
library(tidyverse)

theme_update(plot.title = element_text(hjust = 0.5))


df = read.csv("C:\\Users\\BCBrown\\PycharmProjects\\EPASynoptic\\all_data_long.csv")
print(df)

df = filter(df, model_type != "MLP")

df1 = filter(df, leverage == "leverage")
df2 = filter(df, leverage == "non_leverage")
print(df2)

doc = filter(df1, nutrient == "doc")
no3 = filter(df1, nutrient == "no3")
tn = filter(df1, nutrient == "tn")
tp = filter(df1, nutrient == "tp")

doc_stream = filter(doc, data_type == "stream")
doc_stream$importance_stream = doc_stream$importance
doc_lake = filter(doc, data_type == "lake")
doc_lake$importance_lake = doc_lake$importance

doc_combined = full_join(doc_stream, doc_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
doc_combined
ggplot(doc_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for DOC, leverage") + 
    scale_color_brewer(palette="Set1") +
    theme_bw(plot.title = element_text(hjust = 0.5))



no3_stream = filter(no3, data_type == "stream")
no3_stream$importance_stream = no3_stream$importance
no3_lake = filter(no3, data_type == "lake")
no3_lake$importance_lake = no3_lake$importance

no3_combined = full_join(no3_stream, no3_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
no3_combined
ggplot(no3_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for NO3, leverage")



tn_stream = filter(tn, data_type == "stream")
tn_stream$importance_stream = tn_stream$importance
tn_lake = filter(tn, data_type == "lake")
tn_lake$importance_lake = tn_lake$importance

tn_combined = full_join(tn_stream, tn_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
tn_combined
ggplot(tn_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for TN, leverage")



tp_stream = filter(tp, data_type == "stream")
tp_stream$importance_stream = tp_stream$importance
tp_lake = filter(tp, data_type == "lake")
tp_lake$importance_lake = tp_lake$importance

tp_combined = full_join(tp_stream, tp_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
tp_combined
ggplot(tp_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for TP, leverage")





doc = filter(df2, nutrient == "doc")
no3 = filter(df2, nutrient == "no3")
tn = filter(df2, nutrient == "tn")
tp = filter(df2, nutrient == "tp")

doc_stream = filter(doc, data_type == "stream")
doc_stream$importance_stream = doc_stream$importance
doc_lake = filter(doc, data_type == "lake")
doc_lake$importance_lake = doc_lake$importance

doc_combined = full_join(doc_stream, doc_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
doc_combined
ggplot(doc_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for DOC")



no3_stream = filter(no3, data_type == "stream")
no3_stream$importance_stream = no3_stream$importance
no3_lake = filter(no3, data_type == "lake")
no3_lake$importance_lake = no3_lake$importance

no3_combined = full_join(no3_stream, no3_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
no3_combined
ggplot(no3_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for NO3")



tn_stream = filter(tn, data_type == "stream")
tn_stream$importance_stream = tn_stream$importance
tn_lake = filter(tn, data_type == "lake")
tn_lake$importance_lake = tn_lake$importance

tn_combined = full_join(tn_stream, tn_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
tn_combined
ggplot(tn_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for TN")


tp_stream = filter(tp, data_type == "stream")
tp_stream$importance_stream = tp_stream$importance
tp_lake = filter(tp, data_type == "lake")
tp_lake$importance_lake = tp_lake$importance

tp_combined = full_join(tp_stream, tp_lake, by=c("model_type" = "model_type", "nutrient" = "nutrient", "feature"="feature"))
tp_combined
ggplot(tp_combined, aes(x=importance_stream, y=importance_lake)) + 
    geom_point(aes(shape=model_type, color=feature), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for TP") +
    theme_bw()










print(doc_combined)
print(doc_stream)
print(doc_lake)
ggplot(doc, aes(x=feature,y=importance)) +
    geom_jitter(aes(shape=model_type,color=data_type), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for DOC")

ggplot(no3, aes(x=feature,y=importance)) +
    geom_jitter(aes(shape=model_type,color=data_type), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for NO3")

ggplot(tn, aes(x=feature,y=importance)) +
    geom_jitter(aes(shape=model_type,color=data_type), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for TN")


ggplot(tp, aes(x=feature,y=importance)) +
    geom_jitter(aes(shape=model_type,color=data_type), size=5, width=0.2, alpha=0.5) +
    ggtitle("importance of feature predictors for TP")


ggplot()
