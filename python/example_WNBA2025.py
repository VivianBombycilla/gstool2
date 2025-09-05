from gstool import *

games_xl,teams_xl = read_excel("python/data_WNBA2025.xlsx","Input_Games","Input_Teams")

all_teams = teams_xl.index
east_teams = teams_xl[teams_xl.Conference == "Eastern"].index
west_teams = teams_xl[teams_xl.Conference == "Western"].index

teams_lists = (east_teams,west_teams)
confs = ("Eastern","Western")

# Obtain DataFrames for all_teams
dots_data,segments_data,labels_data,teams_data = produce_data_frames(all_teams,games_xl,teams_xl)

# Obtain maximum absolute y value.
x_max = max(dots_data.x)
y_max = max(abs(dots_data.y))

# WEEK TO WEEK
date = "Sep 02, 2025"
week = 16

def make_WNBA_plot(
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
        plot_width = 224,
        x_lims = (0,x_max), # either tuple (x_min,x_max) or "auto"
        y_lims = (-y_max,y_max), # either tuple (x_min,x_max) or "auto"
        expand_y = 0.5, # amount of padding to add
        
        # BREAKS
        x_break_size = 4,
        y_break_size = 4,
        axis_labels_size = 5,

        # DOTS AND SEGMENTS
        dot_size = 0.5, # radius (y) of dots
        segment_scale = 0.8, # relative height of segments compared to dot_size 
        segment_rel_width = 4, # how many times thicker the segments should be than the spaces between the segments
        
        # TEXT
        plot_title = plot_title,
        plot_title_size = 8,
        vertical_axis_title = "Wins above .500",
        horizontal_axis_title = "Game",
        
        # LABELS
        label_size = 3.5,
        label_shared_x_offset = 0.6,
        label_x_offset = 0.7,
        label_y_offset = 1,
        
        # AESTHETICS
        font_family = "Saira",

        # AUXILIARY FILE PATHS
        path_logos = "./../Logos/",
        path_output = path_output
    )

make_WNBA_plot(
    dots_data,
    segments_data,
    labels_data,
    teams_data,
    plot_title = "WNBA Graphical Standings – "+date,
    path_output = "outputs/WNBA2025_W"+str(week)+".svg"
)

for team_list,conf in zip(teams_lists,confs):
    dots_data,segments_data,labels_data,teams_data = produce_data_frames(team_list,games_xl,teams_xl)
    make_WNBA_plot(
        dots_data,
        segments_data,
        labels_data,
        teams_data,
        plot_title = "WNBA Graphical Standings – "+date+" – " + conf,
        path_output = "outputs/WNBA2025_W"+str(week)+"_"+conf+".svg"
    )
