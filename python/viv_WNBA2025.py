from gstool import *
import subprocess # for inkscape command line tool

games_xl,teams_xl = read_excel("data_WNBA2025.xlsx","Input_Games","Input_Teams")

all_teams = teams_xl.index
east_teams = teams_xl[teams_xl.Conference == "Eastern"].index
west_teams = teams_xl[teams_xl.Conference == "Western"].index

teams_lists = (east_teams,west_teams)
confs = ("Eastern","Western")

# Find the points earned from a result. This must be adjusted for each sport, and should use integers.
def points_from_result_WNBA(team,winner):
    return int(team == winner)

# From the number of games and points give the X and Y coordinates from a given state.
def coords_from_state_WNBA(games,points):
    return games,2*points-games

# Obtain DataFrames for all_teams, in order to obtain max absolute y value.
dots_data,segments_data,labels_data,teams_data = produce_data_frames(all_teams,games_xl,teams_xl,points_from_result_WNBA,coords_from_state_WNBA)

# Obtain maximum absolute y value.
x_max = max(dots_data.x)
y_max = max(abs(dots_data.y))

# WEEK TO WEEK
date = "Final"
week = 18

wnba_annotations = [
    svg_text(
        x = 254.5,
        y = 142,
        text = "Graphic by Vivian (vbbcla)",
        font_size = 4,
        font_family = "auto",
        text_anchor = "end"
    )
]

def make_WNBA_plot(
    teams,
    plot_title,
    path_output
    ):
    make_GS_Plot(
        # DATA
        teams = teams,
        games_xl = games_xl,
        teams_xl = teams_xl,
        points_from_result = points_from_result_WNBA,
        coords_from_state = coords_from_state_WNBA,

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
        segment_rel_width = 4, # how many times thicker the segments should be than the spaces between the segments
        
        # TEXT
        plot_title = plot_title,
        plot_title_size = 8,
        vertical_axis_title = "Wins above .500",
        horizontal_axis_title = "Game",
        
        # LABELS
        label_size = 3.5,
        label_shared_x_offset = 0.7,
        label_x_offset = 0.7,
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
        # font_family = "Merriweather Sans",
        annotations = wnba_annotations,

        # COLOURS
        background_colour = "#f8ece1",

        # AUXILIARY FILE PATHS
        path_logos = "./../outputs/logos/wnba/",
        path_output = path_output
    )

make_WNBA_plot(
    teams = all_teams,
    plot_title = "WNBA Graphical Standings – "+date,
    path_output = "outputs/WNBA2025_W"+str(week)+".svg"
)

subprocess.run(["inkscape","./outputs/WNBA2025_W"+str(week)+".svg","-o","./outputs/WNBA2025_W"+str(week)+".png","-d",str(960*2)],shell=True)

for team_list,conf in zip(teams_lists,confs):
    make_WNBA_plot(
        teams = team_list,
        plot_title = "WNBA Graphical Standings – "+date+" – " + conf,
        path_output = "outputs/WNBA2025_W"+str(week)+"_"+conf+".svg"
    )
    subprocess.run(["inkscape","outputs/WNBA2025_W"+str(week)+"_"+conf+".svg","-o","outputs/WNBA2025_W"+str(week)+"_"+conf+".png","-d",str(960*2)],shell=True)
    

