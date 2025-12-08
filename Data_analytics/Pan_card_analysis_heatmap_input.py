
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# -------------------------------
# 1. Load Data
# -------------------------------
def load_data(file_path, sheet_name="Sheet1"):
    return pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# -------------------------------
# 2. Clean Data
# -------------------------------
def clean_data(df, cat_col, group_col):
    df = df.dropna(subset=[cat_col, group_col])
    df[cat_col] = df[cat_col].astype(int)
    return df

# -------------------------------
# 3. Compute Statistics
# -------------------------------
def compute_stats(df, cat_col, group_col):
    result = []
    for category, group in df.groupby(group_col):
        min_val = group[cat_col].min()
        max_val = group[cat_col].max()
        avg_val = round(group[cat_col].mean(), 2)
        median_val = int(group[cat_col].median())
        mode_list = group[cat_col].mode().tolist()
        mode_val = mode_list[0] if mode_list else None
        
        result.append({
            'Category': category,
            'Min': min_val,
            'Max': max_val,
            'Average': avg_val,
            'Median': median_val,
            'Mode': mode_val
        })
    return pd.DataFrame(result).set_index('Category')

# -------------------------------
# 4. Save Stats to Excel
# -------------------------------
def save_stats(stats_df, output_file):
    stats_df.to_excel(output_file)
    print(f"Stats saved to: {output_file}")

# -------------------------------
# 5. Plot Heatmap
# -------------------------------
def plot_heatmap(stats_df, column, output_path, group_col, cat_col):
    plt.figure(figsize=(6, 4))
    sns.heatmap(stats_df[[column]], annot=True, cmap="coolwarm", fmt="g")
    plt.title(f"Heatmap: {group_col} vs {column} of {cat_col}")
    plt.ylabel(group_col)
    plt.xlabel(column)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Heatmap saved to: {output_path}")

# -------------------------------
# 6. Main Function with User Input
# -------------------------------
def main():
    print("PAN Analysis Tool")
    file_path = input("Enter full Excel file path: ").strip()
    sheet_name = input("Enter sheet name (default: Sheet1): ").strip() or "Sheet1"
    Variable_cat = input("Enter numeric column name (e.g., IssueDate): ").strip()
    Variable_distr = input("Enter category column name (e.g., Series): ").strip()
    
    # Output paths
    output_file = file_path.replace(".xlsx", "_stats.xlsx")
    heatmap_path = output_file.replace("_stats.xlsx", "_heatmap.png")
    
    # Workflow
    df = load_data(file_path, sheet_name)
    df = clean_data(df, Variable_cat, Variable_distr)
    stats_df = compute_stats(df, Variable_cat, Variable_distr)
    save_stats(stats_df, output_file)
    plot_heatmap(stats_df, 'Mode', heatmap_path, Variable_distr, Variable_cat)

# Run the script
if __name__ == "__main__":
    main()
