## File: DateAndTimeFeatures.py
## Author: Alexis Fexy (alexisfexy@gmail.com)
## Date: June 19th, 2019
## Description: Program reads a tsv and outputs a tsv with date components as
##      directed by the user


import csv
import sys
import datetime 
import pandas as pd
import dateutil.parser
import itertools
from datetime import datetime
import time
import math

# Constants of Date Formats Interested in:

# ALL patterns (time, date, datetime)
DATE_PATTERNS = ['%I:%M:%S %p',
                     '%m/%d/%Y %I:%M:%S %p',
                     '%m/%d/%Y',
                     '%m/%d/%Y %H:%M:%S %p',
                     '%m/%d/%Y %H:%M',
                     '%m/%d/%y %I:%M:%S %p',
                     '%m/%d/%y',
                     '%m/%d/%y %H:%M:%S %p',

                     '%m/%d/%y %H:%M']
# Just Date Patterns: 
JUST_DATE = ['%m/%d/%Y','%m/%d/%y']

# Just Time Patterns: 
JUST_TIME = ['%I:%M:%S %p', '%H:%M:%S']
DATETIME = ['%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M',
            '%m/%d/%y %I:%M:%S %p', '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M']
    

# createDataFrame:
#   @params: 
#   @return: DataFrame - from user's tsv
#   description: ask the user for tsv file name, read it, & make a data frame  
def createDataFrame():
    input_name = input("What is the name of your tsv file? \n")
    got_file = False
    while got_file is False: 
        try:
            data_frame = pd.read_csv(input_name + ".tsv", encoding = "ISO-8859-1", sep= '\t')
            got_file = True
        except:
            input_name = input("Could not find a TSV file with that name. What is the name of your tsv file? \n")
    return data_frame


# findNonNullIndex:
#   @params: data_frame // DataFrame - dataframe column is in 
#           column // String - name of column you want to search
#   @return: the first non null index if there is one
#   description: given a data frame and column name, returns the index of the first non-null value in that column
def findNonNullIndex(data_frame, column):
    null_check = data_frame[column].notnull()
    i = False
    # check to see if all NaN values
    if null_check.sum().sum() != 0: # they are not all NaN values 
        # get first value that is NOT NaN 
        for i in data_frame.index:
            if null_check[i] == True: # found a value that is not null
                break
    return i

# findTimeColumns: 
#   @params: df_name // DataFrame - data frame of user's tsv
#   @return: Dictionary - keys = columns names, values = format of column
#   description: scans DataFrame for column with date, time, datetime format. creates dictionary
#                   of column names, and keys of the format of their dates
def findTimeColumns (df_name):
    columns = list(df_name)
    column_dict = {} # dictionary to hold column name & format 
    for col in columns:
        non_null_index = findNonNullIndex(df_name, col)
        if non_null_index is not False : # there is a valid item
            check_type = df_name[col][non_null_index]
            for pattern in DATE_PATTERNS:
                try:
                    datetime.strptime(check_type, pattern) # if it fits one of the patterns                   
                    column_dict[col] = pattern
                except:
                    pass
    return column_dict



'''
######
######
######


DURATION RELATED FUNCTIONS:

'''

# makeCombinations: 
#   @params: col_dict // Dictionary - column names as keys, format of columns as values
#   @return: List - of all combinations of keys
#   description: takes a dictionary and makes a list of all the possible combinations of keys
def makeCombinations(col_dict):
    list_of_columns = list(col_dict.keys())
    combo_list = list(itertools.combinations(list_of_columns, 2))
    return combo_list



# getUserDurationSelections:
#   @param: combination_list // List - a list of all possible durations
#   @return: List - list of indexes of the desired durations 
#   description: Asks users what durations they would like. Returns a new list of the
#               corresponding indexes of these desired durations locations in the combination_list
def getUserDurationSelections(combination_list):
    print("You indicated you would like to create duration columns.\n")
    print("Below are all of the duration combinations. The order listed does not matter: \n")
    print(pd.DataFrame(combination_list)) # for ease of viewing, show them the duration combinations in a data frame
    print("\n")
    
    combo_indexes = []
    input_combo= input("Enter indexes of combinations desired. If done, type DONE: \n")
    combination_list_last_index = len(combination_list)- 1

    # Get the indexes of desired durations
    while not input_combo == "DONE":
        # check for invalid input
        index_selected = -10
        try:
            index_selected = int(input_combo)
        except:
            pass 
        while input_combo != "DONE" and index_selected not in range(0, (combination_list_last_index + 1)):
            input_combo = input("Invalid Response. Please type a valid index between 0 and {}. If done, type DONE: \n"
                                .format(combination_list_last_index))
            try:
                index_selected = int(input_combo)
            except:
                pass
        # end of error checking
        if input_combo == "DONE":
            break
 
        # valid input and not DONE
        else:
            combo_indexes.append(index_selected)
            input_combo = input("Enter indexes of combinations desired. If done, type DONE: \n")
    return combo_indexes





# getDurationHelper:
#   @param: column1 // String - name of column for duration
#           column2 // String - name of other column for duration
#           data_frame // DataFrame - original DataFrame
#           Days // Boolean - True if want return value in Days, False if you want return value in Seconds#
#   @return: DataFrame - updated dataframe with new column of duration between column1 and column2 
#   description: computes the durations between column1 and column2 & makes a new dataframe including the computed duration column
def getDurationHelper(column1, column2, data_frame, Days):
    ## at this point we know the whole column is not null,
    ## so we dont need to check for "false"
    null_check1 = data_frame[column1].notnull()
    null_check2 = data_frame[column2].notnull()
    duration_values = list()
    name_duration_column = "{} {} Duration".format(column1, column2)
    for ind in data_frame.index:
        #check to see if values in both columns to comupte duration 
        if null_check1[ind] == False or null_check2[ind] == False:
            duration_values.append(float('nan'))
        elif null_check1[ind] == True and null_check2[ind] == True:
            datetime_1 = dateutil.parser.parse(data_frame[column1][ind])
            datetime_2 = dateutil.parser.parse(data_frame[column2][ind])
            # greater time is YOUNGER: 
            if datetime_1 > datetime_2: #dtime1 is YOUNGER than dtime1
                difference = datetime_1 - datetime_2
            else:
                difference = datetime_2 - datetime_1
            # check which format you want:
            if Days == True:
                duration_values.append(difference.days)
            else: # we want seconds
                duration_values.append(difference.total_seconds())
    data_frame[name_duration_column] = duration_values
    return data_frame

# createDurations
#   @params: duration_indexes // List - indexes of the durations the user selected 
#       duration_combination_list // List - all possible durations 
#       column_format_dict // Dictionary - column names & their formats 
#       original_df // DataFrame - original data frame of users tsv
#   @return: DataFrame - original data frame with new duration columns
#   description: computes the requested durations and adds the corresponding columns to the data frame
def createDurations(duration_indexes, duration_combination_list, column_format_dict, data_frame):
    for ind in duration_indexes: # for each pair of columns, compute their durations:
        pair = duration_combination_list[ind]
        column_name_1  = pair[0]
        column_name_2 = pair[1] 
        format_1 = column_format_dict[column_name_1] # determine the format of the columns
        format_2 = column_format_dict[column_name_2]
    
        # error checking -- make sure both columns have the same format       
        if format_1 != format_2: # not the same format, check if the same type (date, time, datetime)
            print("\n The following two columns do not have the same date format: \n {} has format {} and {} has format {}"
                            .format(column_name_1, format_1, column_name_2, format_2))
            print("This duration will not be computed. \n")

        else:

            if format_1 in JUST_DATE: # duration should be in DAYS
                data_frame = getDurationHelper(column_name_1, column_name_2, data_frame, True)
        
            else: # duration should be in SECONDS
                data_frame = getDurationHelper(column_name_1, column_name_2, data_frame, False)
    return data_frame



# durations: 
#   @params: col_format_dict // Dictionary - column name, format dictionary
#           data_frame // DataFrame - original DataFrame from users tsv
#   @return: DataFrame - original DataFrame with new duration columns
#   description: calls helper functions to create a data frame with new duration columns
def durations(col_format_dict, data_frame):
    combination_list = makeCombinations(col_format_dict)
    user_selected_indexes = getUserDurationSelections(combination_list)
    new_duration_data_frame = createDurations(user_selected_indexes, combination_list, col_format_dict, data_frame)
    return new_duration_data_frame


'''

DURATION END 

####################
####################


COLUMN EXPANSION FUNCTIONS: 

'''


# getPartOfDay
#   @params: hour // int - indexes of the durations the user selected 
#   @return: string - part of day (night, morning, afternoon, evening)
#   description: given an hour of the day, returns the part of the day 
def getPartOfDay(hour):
    return (
        "night" if 0 <= hour < 6
        else
        "morning" if 6 <= hour < 12
        else
        "afternoon" if 12 <= hour < 17
        else
        "evening" )  #if 17 <= hour < 24


# featureEngineerHelper
#   @params: column // String - name of column to feature engineer
#           orignal_df // DataFrame - dataframe 
#           Date // Boolean - True if need to feature engineer date components 
#           Time // Boolean - True if ned to feature engineer time components
#   @return: DataFrame - original dataframe with new
#   descriptions: takes a column and expands it into date, time, or both components. adds these new columns to the original dataframe
def featureEngineerHelper(column, original_df, Date, Time):
    # if date components requested:
    if Date == True:
        quarter_list = list()
        month_list = list()
        day_list = list()
        day_of_week_list = list()

        for ind in original_df.index:
            try:
                datetime_current = dateutil.parser.parse(original_df[column][ind])
                quarter_list.append(((datetime_current.month - 1) // 3) + 1)
                month_list.append(datetime_current.month)
                day_list.append(datetime_current.day)
                day_of_week_list.append(datetime_current.weekday())

            except: # if there is a NaN value at this index
                quarter_list.append(float('nan'))
                month_list.append(float('nan'))
                day_list.append(float('nan'))
                day_of_week_list.append(float('nan'))
        # add to dataframe
        original_df[column + " Quarter"] = quarter_list
        original_df[column + " Month" ] = month_list
        original_df[column + " Day" ] = day_list
        # check if he wants "dow"
        original_df[column + " Day Of Week" ] = day_of_week_list
        
    # if time components requested:               
    if Time == True:
        hour_list = list()
        minute_list = list()
        second_list = list()
        day_part_list = list()
        
        for ind in original_df.index:
            try:
                datetime_current = dateutil.parser.parse(original_df[column][ind])
                hour_list.append(datetime_current.hour)
                minute_list.append(datetime_current.minute)
                second_list.append(datetime_current.second)
                day_part_list.append(getPartOfDay(datetime_current.hour))
    
            except: # if there is a NaN value at this index
                hour_list.append(float('nan'))
                minute_list.append(float('nan'))
                second_list.append(float('nan'))
                day_part_list.append(float('nan'))
        #add to dataframe               
        original_df[column + " Hour"] = hour_list
        original_df[column + " Minutes"] = minute_list
        original_df[column + " Seconds"] = second_list
        # check if he wants DayPart
        original_df[column + " Part Of Day"] = day_part_list

    return original_df

# createFeatureEngineeredColumns:
#   @params: indexes // List - indexes of the durations the user selected 
#       column_list // List - all possible durations 
#       column_format_dict // Dictionary - column names & their formats 
#       original_df // DataFrame - original data frame of users tsv
#   @return: DataFrame - original data frame with new feature engineered columns
#   description: for each requested column, figures out which components needed to computec
#               then calls the helper to compute the requested feature engineered columns
#               and add the corresponding columns to the data frame
def createFeatureEngineeredColumns(indexes, column_list, column_format_dict, feature_df):
    for ind in indexes: # for each column, figure out which components you need to compute
        column_name = column_list[ind]
        # determine the type of this column
        # use the original key name, format value dictionary to see the type of column 
        format_of_column= column_format_dict[column_name]
        if format_of_column in JUST_DATE: # only need date components  
            feature_df = featureEngineerHelper(column_name, feature_df, True, False)
        elif format_of_column in JUST_TIME: # only need time components
            feature_df = featureEngineerHelper(column_name, feature_df, False, True)
        else: # datetime, need both date and time components
            feature_df = featureEngineerHelper(column_name, feature_df, True, True)           
    return feature_df
    

# getUserFeatureSelections:
#   @param: time_col_list // List - a list of all column names that have date, time, or datetime values
#   @return: List - list of indexes of the desired columns to feature engineer 
#   description: Asks users what columns they would like to feature engineer. Returns a new list of the
#               corresponding indexes of these desired columns locations in the time_col_list
def getUserFeatureSelections(time_col_list):
    print("Below are all of columns with date, time, or datetime columns: \n")
    print(pd.DataFrame(time_col_list)) # for ease of viewing, show them the duration combinations in a data frame
    print("\n")
    
    feature_indexes = []
    input_feature_index = input("Enter indexes of columns you'd like to feature engineer. If done, type DONE: \n")
    feature_list_last_index = len(time_col_list) - 1

    # Get the indexes of desired columns to feature engineer 
    while not input_feature_index == "DONE":
        # check for invalid input
        index_selected = -10
        try:
            index_selected = int(input_feature_index)
        except:
            pass 
        while input_feature_index != "DONE" and index_selected not in range(0, (feature_list_last_index + 1)):
            input_feature_index = input("Invalid Response. Please type a valid index between 0 and {}. If done, type DONE: \n"
                                .format(feature_list_last_index))
            try:
                index_selected = int(input_feature_index)
            except:
                pass
        # end of error checking
        if input_feature_index == "DONE":
            break
 
        # valid input and not DONE
        else: 
            feature_indexes.append(index_selected)
            
            input_feature_index = input("Enter indexes of columns you'd like to feature engineer. If done, type DONE: \n")
    return feature_indexes


# features: 
#   @params: col_format_dict // Dictionary - column name, format dictionary
#           data_frame // DataFrame - original DataFrame from users tsv
#   @return: DataFrame - original DataFrame with new duration columns
#   description: calls helper functions to create a data frame with requested feature engineered columns
def features(col_format_dict, data_frame):
    time_column_list = list(col_format_dict.keys())
    user_selected_feature_index = getUserFeatureSelections(time_column_list)
    new_data_frame = createFeatureEngineeredColumns(user_selected_feature_index, time_column_list, col_format_dict, data_frame)
    return new_data_frame


# mainFunction():
#   @params:
#   @return:
#   description: calls all helper functions & interacts with user to produce a new tsv with desired components 
def main():
    # CREATE DATA FRAME
    data_frame = createDataFrame() # create data frame

    # FIND COLUMNS WITH DATE VALUES
    col_format_dict = findTimeColumns(data_frame) # scan data frame for columns with date, datetime, time values

    # DURATION:
    input_combo = "N"
    if len(col_format_dict) > 1: # if more than one column, ask if they would like to make duration columns
        input_combo = input("Your dataset contains more than one date column. Should duration columns be added? Y/N: \n")
        while input_combo not in ["Y", "N"]: # check for invalid inputs
            input_combo = input("Invalid Response. Please indicate Y/N \n")
        if input_combo == "Y": # they have indicated they want duration columns 
            data_frame = durations(col_format_dict, data_frame) # updated data frame with duration columns
    # FEATURE ENGINEERING:
    input_feature = input("Would you like to feature enigneer columns? Y/N \n")
    while input_feature not in ["Y", "N"]:# check for invalid inputs
        input_feature= input("Invalid Response. Please indicate Y/N \n")
    if input_feature == "Y": # they have indicated they want feature engineering columns 
        data_frame = features(col_format_dict, data_frame) # updated data frame with feature engineered columns
        
    # DATA FRAME TO TSV:
    if input_combo == "Y" or input_feature == "Y":
        new_name = input("What would you like to save your file as? \n")
        data_frame.to_csv(new_name + ".tsv", sep='\t')

# Call main function       
main()
