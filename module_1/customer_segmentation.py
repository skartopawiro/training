import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
# Create rfmTable
def rfm_analysis(df, customerID='CustomerID', invoiceDate='InvoiceDate', invoiceNo='InvoiceNo', revenue='TotalPrice'):
    df = df.assign(date = lambda x: pd.to_datetime(x[invoiceDate].astype(str), infer_datetime_format=True)) # try to get the date
    now= df['date'].max() + dt.timedelta(days=1)
    rfmTable = df.groupby(customerID).agg({'date': lambda x: (now - x.max()).days, invoiceNo: lambda x: len(x), revenue: lambda x: x.sum()})
    rfmTable['date'] = rfmTable['date'].astype(int)
    rfmTable.rename(columns={'date': 'days_since_last_order', 
                             'InvoiceNo': 'frequency', 
                             'TotalPrice': 'total_revenue'}, inplace=True)
    quantiles = rfmTable.quantile(q=[0.25,0.5,0.75]).to_dict()
    segmented_rfm = rfmTable
    def RScore(x,p,d):
        if x <= d[p][0.25]:
            return 1
        elif x <= d[p][0.50]:
            return 2
        elif x <= d[p][0.75]: 
            return 3
        else:
            return 4
    
    def FMScore(x,p,d):
        if x <= d[p][0.25]:
            return 4
        elif x <= d[p][0.50]:
            return 3
        elif x <= d[p][0.75]: 
            return 2
        else:
            return 1
    segmented_rfm['r_quartile'] = segmented_rfm['days_since_last_order'].apply(RScore, args=('days_since_last_order',quantiles,))
    segmented_rfm['f_quartile'] = segmented_rfm['frequency'].apply(FMScore, args=('frequency',quantiles,))
    segmented_rfm['m_quartile'] = segmented_rfm['total_revenue'].apply(FMScore, args=('total_revenue',quantiles,))
    segmented_rfm['RFMScore'] = segmented_rfm.r_quartile.map(str) + segmented_rfm.f_quartile.map(str) + segmented_rfm.m_quartile.map(str)
    
    #Calulate # Kmeans clusters
    segmentedv2 = segmented_rfm[['r_quartile','f_quartile','m_quartile']]
    wcss = []
    for i in range(1,11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=0)
        kmeans.fit(segmentedv2)
        wcss.append(kmeans.inertia_)
    
    return segmented_rfm

# refine clusters with KMEANS
def kmeans_analysis(df, n_clusters=4):
    segments= df[['r_quartile','f_quartile','m_quartile']]
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=0)
    clusters = kmeans.fit_predict(segments)
    df['clusters'] = clusters
    grouped = df.groupby(['clusters'])['days_since_last_order','frequency','total_revenue'].agg('mean')
    print(grouped)
    return df