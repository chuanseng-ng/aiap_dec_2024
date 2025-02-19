import sqlite3
import pandas as pd
import time

import setup.setup as setup
import setup.duration_cal as duration_cal
import EDA.eda_step as eda_step
import model_select.model_select as model_select
import model_eval.model_eval as model_eval

start_time = time.time()
step_cnt = 1  # Initialize step count

(
    db_path,
    part1_target_col,
    part1_enc_col_list,
    part1_corr_thresh,
    part2_target_list,
    part2_target_comb,
    part2_corr_thresh,
    low_case_col_list,
    nutrient_col_list,
    drop_col_list,
    model_test_size,
    model_random_state,
    model_search_method,
    model_cv_num,
    model_num_iter,
    model_num_jobs,
    part1_model_name_list,
    part2_model_name_list,
    part1_model_task_type,
    part2_model_task_type,
    part1_model_scoring,
    part2_model_scoring,
    part1_model_save_model,
    part2_model_save_model,
    part1_model_param_dict,
    part2_model_param_dict,
) = setup.setup_stage()

# Create connection to SQL database
print(f"{step_cnt}. Connecting to SQL database....")
conn = sqlite3.connect(db_path)
print("Connection done!")

part1_time, step_cnt = duration_cal.duration_print(start_time, step_cnt)

# Get data from SQL database table
print(f"{step_cnt}. Extract SQL database table as DataFrame...")
farm_data_table_query = "SELECT name FROM sqlite_master WHERE type='table';"
farm_data_table_name = pd.read_sql(farm_data_table_query, conn).iloc[0, 0]
farm_data_query = f"SELECT * FROM {farm_data_table_name};"
farm_data_df = pd.read_sql_query(farm_data_query, conn)
print("Extraction done!")

part2_time, step_cnt = duration_cal.duration_print(part1_time, step_cnt)

# Using analysis from task_1 EDA, perform data pre-processing and feature engineering
print(f"{step_cnt}. Performing EDA on DataFrame....")
(
    part1_feat_farm_data_df,  # For part 1 regression task
    part1_X_train,
    part1_X_test,
    part1_Y_train,
    part1_Y_test,
    part2_feat_farm_data_df,  # For part 2 classifier task
    part2_X_train,
    part2_X_test,
    part2_Y_train,
    part2_Y_test,
) = eda_step.ml_eda_step(
    farm_data_df,
    part1_target_col,
    part1_enc_col_list,
    part1_corr_thresh,
    part2_target_list,
    part2_target_comb,
    part2_corr_thresh,
    low_case_col_list,
    nutrient_col_list,
    drop_col_list,
    model_test_size,
    model_random_state,
)
print("EDA done!")

part3_time, step_cnt = duration_cal.duration_print(part2_time, step_cnt)

# Pre-select a few models and train models to get best optimized parameters
print(f"{step_cnt}. Training machine learning models....")
print("Starting with part 1 - Regression...")
part1_best_estimator_dict = model_select.model_selection(
    part1_X_train,
    part1_Y_train,
    model_random_state,
    model_num_jobs,
    model_cv_num,
    part1_model_scoring,
    model_num_iter,
    part1_model_param_dict,
    model_search_method,
    "Regression",  # task_type
)
print("Regression done!")
print("Starting with part 2 - Classification...")
part2_best_estimator_dict = model_select.model_selection(
    part2_X_train,
    part2_Y_train,
    model_random_state,
    model_num_jobs,
    model_cv_num,
    part2_model_scoring,
    model_num_iter,
    part2_model_param_dict,
    model_search_method,
    "Classification",  # task_type
)
print("Classification done!")
print("Training done!")

part4_time, step_cnt = duration_cal.duration_print(part3_time, step_cnt)

# Evaluate performance of selected models and provide metric results
print("{step_cnt}. Evaluating machine learning model....")
print("Starting with part 1 - Regression...")
model_eval.model_evaluation(
    part1_X_test,
    part1_Y_test,
    part1_best_estimator_dict,
    part1_model_save_model,
    "Regression",
)
print("Regression done!")
print("Starting with part 2 - Classification...")
model_eval.model_evaluation(
    part2_X_test,
    part2_Y_test,
    part2_best_estimator_dict,
    part2_model_save_model,
    "Classification",
)
print("Classification done!")
print("Evaluation done!")

part5_time, step_cnt = duration_cal.duration_print(part4_time, step_cnt)

# Best regression model decision -
## If model variance is priority, look for highest R^2
## If predictive accuracy is priority, look for lowerst MSE (0 == Perfect model)

# Best classification model decision -
## If false positives are more costly, look for higher precision
## If false negatives are more problematic, look for higher recall
## Look for higher F1-score to determine how well model balances precision and recall

end_time = time.time()
final_time = end_time - start_time
final_duration, final_tag = duration_cal.duration_cal(final_time)

print("Script has reached end of line - It will terminate now!")
print(f"Script has run for {final_duration:.3f} {final_tag}!")
print("Please refer to ml_model.log for model metric results!")
