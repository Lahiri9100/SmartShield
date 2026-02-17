import os
import pandas as pd

HISTORY_DIR = "history"

# Ensure history directory exists
os.makedirs(HISTORY_DIR, exist_ok=True)


def save_to_history(df: pd.DataFrame, filename: str):
    """
    Save dataframe to history folder as CSV.
    """
    file_path = os.path.join(HISTORY_DIR, f"{filename}.csv")
    df.to_csv(file_path, index=False)


def list_saved_histories():
    """
    List all saved history files.
    """
    files = os.listdir(HISTORY_DIR)
    return [f.replace(".csv", "") for f in files if f.endswith(".csv")]


def load_history_df(filename: str):
    """
    Load a saved history CSV into dataframe.
    """
    file_path = os.path.join(HISTORY_DIR, f"{filename}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None


def delete_history_item(filename: str):
    """
    Delete a specific saved history file.
    """
    file_path = os.path.join(HISTORY_DIR, f"{filename}.csv")
    if os.path.exists(file_path):
        os.remove(file_path)


def clear_history():
    """
    Delete all saved history files.
    """
    for file in os.listdir(HISTORY_DIR):
        if file.endswith(".csv"):
            os.remove(os.path.join(HISTORY_DIR, file))
