import pandas as pd
from collections.abc import Sequence, Callable

def read_excel(
    spreadsheet_path: str,
    games_sheet: str,
    teams_sheet: str
):
    '''Reads the Excel spreadsheet at the given path, extracting game and team data as pandas DataFrame objects.
    
    The sheet containing games data should include columns Team1, Team2, Winner, and the games should be in chronological order.
    
    The sheet containing team data should include the team name in the first column, as well as columns ImagePath and LineColour.'''
    games_xl = pd.read_excel(spreadsheet_path,sheet_name=games_sheet)
    teams_xl = pd.read_excel(spreadsheet_path,sheet_name=teams_sheet,index_col=0)
    return games_xl,teams_xl

def process_team(
    team: str,
    games_xl: pd.DataFrame,
    points_from_result: Callable[[str,str],int]
):
    '''Intermediate function to parse data for one specific team. See `produce_data_frames`.'''
    # Filter games for just those containing team
    games_filtered = games_xl[(games_xl.Team1 == team) | (games_xl.Team2 == team)]
    games_filtered_list = list(games_filtered.itertuples(index=False))

    # Initialize dicts
    team_dots_dict = {"games":[0],"points":[0],"team":[team]}
    team_segments_dict = {"games":[],"points":[],"team":[],"result":[],"modifier1":[]}

    games_count = 0
    for game in games_filtered_list:
        result = points_from_result(team,str(game.Winner))

        team_dots_dict["games"].append(team_dots_dict["games"][-1] + 1)
        team_dots_dict["points"].append(team_dots_dict["points"][-1] + result)
        team_dots_dict["team"].append(team)

        team_segments_dict["games"].append(games_count)
        team_segments_dict["points"].append(team_dots_dict["points"][games_count])
        team_segments_dict["team"].append(team)
        team_segments_dict["result"].append(result)
        team_segments_dict["modifier1"].append(game.Modifier1)

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

def shared_with(
    data: pd.DataFrame,
    row: pd.Series,
    cols: Sequence[str]
):
    '''Given a pandas DataFrame, one row within and labels for several columns:
    Find the number of rows whose values at the columns specified are identical to that of the given row.

    See `num_in_group`.'''
    for col in cols:
        data = data[data[col] == row[col]]
    return data.shape[0]

def num_in_group(
    data: pd.DataFrame,
    row: pd.Series,
    cols: Sequence[str]
):
    '''Given a pandas DataFrame, one row within and labels for several columns:
    Find the number of rows whose values at the columns specified are identical to that of the given row.
    
    See `shared_with`.'''
    for col in cols:
        data = data[data[col] == row[col]]
    data = data[data.team <= row.team]
    return data.shape[0]

def produce_data_frames(
    teams: Sequence[str],
    games_xl: pd.DataFrame,
    teams_xl: pd.DataFrame,
    points_from_result: Callable[[str,str],int],
    coords_from_state: Callable[[int,int],tuple[int,float]]
):
    '''Given a list of teams, DataFrames containing game and team data, as well as functions to find points from a result as well as coordinates from a given (Games, Wins) tuple:
    
    Produce DataFrames `dots_data`, `segments_data`, `labels_data`, `teams_data`, which can be used to plot graphical standings.'''
    dots_data = pd.DataFrame()
    segments_data = pd.DataFrame()
    labels_data = pd.DataFrame()
    teams_data: pd.DataFrame = teams_xl.loc[teams] # type: ignore

    # Process data into DataFrames
    for team in teams:
        team_dots_data,team_segments_data,team_labels_data = process_team(team,games_xl,points_from_result)
        dots_data = pd.concat([dots_data,team_dots_data],axis=0,ignore_index=True)
        segments_data = pd.concat([segments_data,team_segments_data],axis=0,ignore_index=True)
        labels_data = pd.concat([labels_data,team_labels_data],axis=0,ignore_index=True)
    
    # Add sharedWith and numInGroup columns
    segments_data["sharedWith"] = segments_data.apply(lambda row : shared_with(segments_data,row,["games","points","result"]),axis=1)
    segments_data["numInGroup"] = segments_data.apply(lambda row : num_in_group(segments_data,row,["games","points","result"]),axis=1)
    labels_data["sharedWith"] = labels_data.apply(lambda row : shared_with(labels_data,row,["games","points"]),axis=1)
    labels_data["numInGroup"] = labels_data.apply(lambda row : num_in_group(labels_data,row,["games","points"]),axis=1)
    
    # Add position columns
    dots_data["pos"] = dots_data.apply(lambda row : coords_from_state(row.games,row.points),axis=1)
    segments_data["pos1"] = segments_data.apply(lambda row : coords_from_state(row.games,row.points),axis=1)
    segments_data["pos2"] = segments_data.apply(lambda row : coords_from_state(row.games + 1,row.points + row.result),axis=1)
    labels_data["pos"] = labels_data.apply(lambda row : coords_from_state(row.games,row.points),axis=1)

    # Add x and y columns
    dots_data[["x","y"]] = dots_data["pos"].apply(pd.Series)
    segments_data[["x1","y1"]] = segments_data["pos1"].apply(pd.Series)
    segments_data[["x2","y2"]] = segments_data["pos2"].apply(pd.Series)
    labels_data[["x","y"]] = labels_data["pos"].apply(pd.Series)

    # Add modifier columns

    return dots_data,segments_data,labels_data,teams_data
