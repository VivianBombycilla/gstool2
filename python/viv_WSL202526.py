import math
from gstool import *
import subprocess # for inkscape command line tool

games_xl,teams_xl = read_excel("data_WSL202526.xlsx","Input_Games","Input_Teams")

all_teams = teams_xl.index

# count number of ties
num_ties = games_xl[games_xl.Winner == "TIE"].shape[0]
num_games = games_xl[games_xl.Completed].shape[0]
avg_points = (num_games*3-num_ties)/(num_games*2)

# Find the points earned from a result. This must be adjusted for each sport.
def points_from_result_WSL(team,winner):
    if winner == team:
        return 3
    elif winner == "TIE":
        return 1
    else:
        return 0

# From the number of games and points give the X and Y coordinates from a given state.
def coords_from_state_WSL(games,points):
    return games,(points-(avg_points*games))

# Obtain DataFrames for all_teams
dots_data,segments_data,labels_data,teams_data = produce_data_frames(all_teams,games_xl,teams_xl,points_from_result_WSL,coords_from_state_WSL)

print("Average points:",round(avg_points,2))
# print(segments_data)


# Obtain maximum absolute y value.
x_max = int(max(dots_data.x))
y_max = math.ceil(max(dots_data.y))
y_min = math.floor(min(dots_data.y))

# WEEK TO WEEK
date = "Sep 09, 2025"
week = 1

wsl_annotations = [
    svg_text(
        x = 254.5,
        y = 142,
        text = "Graphic by Vivian (vbbcla)",
        font_size = 4,
        font_family = "auto",
        text_anchor = "end"
    ),
    svg_text(
        x = 254.5,
        y = 137,
        text = "Average points per match: "+str(round(avg_points,2)),
        font_size = 4,
        font_family = "auto",
        text_anchor = "end"
    )
]

def make_WSL_plot(
    dots_data,
    segments_data,
    labels_data,
    teams_data,
    plot_title,
    path_output
    ):
    make_GS_Plot(
        # DATA
        dots_data,
        segments_data,
        labels_data,
        teams_data,

        # PLOT SETTINGS
        plot_width = 160,#224,
        x_lims = (0,x_max), # either tuple (x_min,x_max) or "auto"
        y_lims = (y_min,y_max), # either tuple (x_min,x_max) or "auto"
        expand_y = 0.2,#0.5, # amount of padding to add
        
        # BREAKS
        x_break_size = 1,
        y_break_size = 1,
        axis_labels_size = 5,

        # DOTS AND SEGMENTS
        dot_size = 0.15, # radius (y) of dots
        segment_scale = 0.8, # relative height of segments compared to dot_size 
        segment_rel_width = 4, # how many times thicker the segments should be than the spaces between the segments
        
        # TEXT
        plot_title = plot_title,
        plot_title_size = 8,
        vertical_axis_title = "Points above average",
        horizontal_axis_title = "Match",
        
        # LABELS
        label_size = 0.5, # label size in y
        label_shared_x_offset = 0.05,
        label_x_offset = 0.07,
        label_y_offset = 1,
        
        # AESTHETICS
        style = """
* {
font-family: "Merriweather Sans";
font-weight: 300;
}
#title {
font-weight: normal
}
""",
        # font_family = "Alegreya Sans",
        annotations = wsl_annotations,

        # COLOURS
        background_colour = "#e6f2e7",

        # AUXILIARY FILE PATHS
        path_logos = "./../outputs/logos/wsl/",
        path_output = path_output
    )

make_WSL_plot(
    dots_data,
    segments_data,
    labels_data,
    teams_data,
    plot_title = "WSL Graphical Standings – "+date,
    path_output = "outputs/WSL202526_W"+str(week)+".svg"
)

subprocess.run(["inkscape","./outputs/WSL202526_W"+str(week)+".svg","-o","./outputs/WSL202526_W"+str(week)+".png","-d",str(960*2)],shell=True)