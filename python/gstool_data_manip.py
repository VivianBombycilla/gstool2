import pandas as pd

# Reads the sheet into a pandas DataFrame object.
def read_excel(spreadsheet_path,games_sheet,teams_sheet):
    games_xl = pd.read_excel(spreadsheet_path,sheet_name=games_sheet)
    teams_xl = pd.read_excel(spreadsheet_path,sheet_name=teams_sheet,index_col=0)
    return games_xl,teams_xl

# Find the points earned from a result. This must be adjusted for each sport.
def points_from_result_WNBA(team_won):
    return int(team_won)

# From the number of games and points give the X and Y coordinates from a given state.
def coords_from_state_WNBA(games,points):
    return games,2*points-games

# Produce the dots, labels, segments intermediate tables for a team.
def process_team(team,games_xl):
    games_filtered = games_xl[(games_xl.Team1 == team) | (games_xl.Team2 == team)]
    games_filtered
    games_filtered_list = list(games_filtered.itertuples(index=False))

    team_dots_dict = {"games":[0],"points":[0],"team":[team]}
    team_segments_dict = {"games":[],"points":[],"team":[],"result":[]}

    games_count = 0
    for game in games_filtered_list:
        result = points_from_result_WNBA(game.Winner == team)
        team_dots_dict["games"].append(team_dots_dict["games"][-1] + 1)
        team_dots_dict["points"].append(team_dots_dict["points"][-1] + result)
        team_dots_dict["team"].append(team)
        team_segments_dict["games"].append(games_count)
        team_segments_dict["points"].append(team_dots_dict["points"][games_count])
        team_segments_dict["team"].append(team)
        team_segments_dict["result"].append(result)
        games_count += 1
    team_labels_dict = {
        "games" : [team_dots_dict["games"][-1]],
        "points": [team_dots_dict["points"][-1]],
        "team"  : [team]
    }
    team_dots_data = pd.DataFrame(data=team_dots_dict)
    team_segments_data = pd.DataFrame(data=team_segments_dict)
    team_labels_data = pd.DataFrame(data=team_labels_dict)

    return team_dots_data,team_segments_data,team_labels_data

# Finds the number of rows whose values at cols specified are identical to that of the given row.
def shared_with(data,row,cols):
    for col in cols:
        data = data[data[col] == row[col]]
    return data.shape[0]
# Finds the number of rows whose values at cols specified are identical to that of the given row, and also are <= in the alphabetical ordering of teams.
def num_in_group(data,row,cols):
    for col in cols:
        data = data[data[col] == row[col]]
    data = data[data.team <= row.team]
    return data.shape[0]

# From a list of teams, produce DataFrames for plotting dots, segments, labels, as well as a DataFrame for the teams data.
def produce_data_frames(teams,games_xl,teams_xl):
    dots_data = pd.DataFrame()
    segments_data = pd.DataFrame()
    labels_data = pd.DataFrame()
    teams_data = teams_xl.loc[teams]

    # Process data into DataFrames
    for team in teams:
        team_dots_data,team_segments_data,team_labels_data = process_team(team,games_xl)
        dots_data = pd.concat([dots_data,team_dots_data],axis=0,ignore_index=True)
        segments_data = pd.concat([segments_data,team_segments_data],axis=0,ignore_index=True)
        labels_data = pd.concat([labels_data,team_labels_data],axis=0,ignore_index=True)
    
    # Add sharedWith and numInGroup columns
    segments_data["sharedWith"] = segments_data.apply(lambda row : shared_with(segments_data,row,["games","points","result"]),axis=1)
    segments_data["numInGroup"] = segments_data.apply(lambda row : num_in_group(segments_data,row,["games","points","result"]),axis=1)
    labels_data["sharedWith"] = labels_data.apply(lambda row : shared_with(labels_data,row,["games","points"]),axis=1)
    labels_data["numInGroup"] = labels_data.apply(lambda row : num_in_group(labels_data,row,["games","points"]),axis=1)
    
    # Add X and Y columns
    dots_data["pos"] = dots_data.apply(lambda row : coords_from_state_WNBA(row.games,row.points),axis=1)
    segments_data["pos1"] = segments_data.apply(lambda row : coords_from_state_WNBA(row.games,row.points),axis=1)
    segments_data["pos2"] = segments_data.apply(lambda row : coords_from_state_WNBA(row.games + 1,row.points + row.result),axis=1)
    labels_data["pos"] = labels_data.apply(lambda row : coords_from_state_WNBA(row.games,row.points),axis=1)
    dots_data[["x","y"]] = dots_data["pos"].apply(pd.Series)
    segments_data[["x1","y1"]] = segments_data["pos1"].apply(pd.Series)
    segments_data[["x2","y2"]] = segments_data["pos2"].apply(pd.Series)
    labels_data[["x","y"]] = labels_data["pos"].apply(pd.Series)

    return dots_data,segments_data,labels_data,teams_data