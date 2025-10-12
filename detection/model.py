import numpy as np
from sklearn.ensemble import IsolationForest

def analyze_dataframe(df):
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(df.select_dtypes(include=np.number))
    df['anomaly'] = model.predict(df.select_dtypes(include=np.number))
    df['anomaly_label'] = df['anomaly'].map({1: "✅ Normal", -1: "⚠️ Suspicious"})
    return df
