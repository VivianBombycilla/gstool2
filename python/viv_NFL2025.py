from gstool import *
import subprocess # for inkscape command line tool

games_xl,teams_xl = read_excel("data_NFL2025.xlsx","Input_Games","Input_Teams")

all_teams = teams_xl.index

confs_teams = [
    teams_xl[teams_xl.Conference == "AFC"].index,
    teams_xl[teams_xl.Conference == "NFC"].index
]

divs = ["AFCE","AFCN","AFCS","AFCW","NFCE","NFCN","NFCS","NFCW"]
divs_long = [
    "AFC East",
    "AFC North",
    "AFC South",
    "AFC West",
    "NFC East",
    "NFC North",
    "NFC South",
    "NFC West"
]
divs_teams = []
for div in divs:
    divs_teams.append(teams_xl[teams_xl.Division == div].index)

# Find the points earned from a result. This must be adjusted for each sport.
def points_from_result_NFL(team,winner):
    if winner == team:
        return 1
    elif winner == "TIE":
        return 0
    else:
        return -1

# From the number of games and points give the X and Y coordinates from a given state.
def coords_from_state_NFL(games,points):
    return games,points

# Obtain DataFrames for all_teams
dots_data,segments_data,labels_data,teams_data = produce_data_frames(all_teams,games_xl,teams_xl,points_from_result_NFL,coords_from_state_NFL)


# Obtain maximum absolute y value.
x_max = max(dots_data.x)
y_max = max(abs(dots_data.y))

# WEEK TO WEEK
date = "Sep 09, 2025"
week = 1

nfl_annotations = [
    svg_text(
        x = 254.5,
        y = 142,
        text = "Graphic by Vivian (vbbcla)",
        font_size = 4,
        font_family = "auto",
        text_anchor = "end"
    )
]

def make_NFL_plot(
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
        plot_width = 176,
        x_lims = (0,x_max), # either tuple (x_min,x_max) or "auto"
        y_lims = (-y_max,y_max), # either tuple (x_min,x_max) or "auto"
        expand_y = 0.4,#0.5, # amount of padding to add
        
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
        vertical_axis_title = "Wins above .500",
        horizontal_axis_title = "Week",
        
        # LABELS
        label_size = 0.4, # label size in y
        label_shared_x_offset = 0.1,
        label_x_offset = 0.12,
        label_y_offset = 0.23,
        label_loop_threshold = 4,
        
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
        annotations = nfl_annotations,

        # COLOURS
        background_colour = "#ffeceb",

        # AUXILIARY FILE PATHS
        path_logos = "./../outputs/logos/nfl/",
        path_output = path_output
    )

make_NFL_plot(
    dots_data,
    segments_data,
    labels_data,
    teams_data,
    plot_title = "NFL Graphical Standings – Week "+str(week)+", 2025",
    path_output = "outputs/NFL2025_W"+str(week)+".svg"
)

subprocess.run(["inkscape","./outputs/NFL2025_W"+str(week)+".svg","-o","./outputs/NFL2025_W"+str(week)+".png","-d",str(960*2)],shell=True)

for team_list,conf in zip(confs_teams,["AFC","NFC"]):
    dots_data,segments_data,labels_data,teams_data = produce_data_frames(team_list,games_xl,teams_xl,points_from_result_NFL,coords_from_state_NFL)
    make_NFL_plot(
        dots_data,
        segments_data,
        labels_data,
        teams_data,
        plot_title = "NFL Graphical Standings – Week "+str(week)+", 2025"+" – " + conf,
        path_output = "outputs/NFL2025_W"+str(week)+"_"+conf+".svg"
    )
    subprocess.run(["inkscape","outputs/NFL2025_W"+str(week)+"_"+conf+".svg","-o","outputs/NFL2025_W"+str(week)+"_"+conf+".png","-d",str(960*2)],shell=True)
    

for team_list,div,div_long in zip(divs_teams,divs,divs_long):
    dots_data,segments_data,labels_data,teams_data = produce_data_frames(team_list,games_xl,teams_xl,points_from_result_NFL,coords_from_state_NFL)
    make_NFL_plot(
        dots_data,
        segments_data,
        labels_data,
        teams_data,
        plot_title = "NFL Graphical Standings – Week "+str(week)+", 2025"+" – " + div_long,
        path_output = "outputs/NFL2025_W"+str(week)+"_"+div+".svg"
    )
    subprocess.run(["inkscape","outputs/NFL2025_W"+str(week)+"_"+div+".svg","-o","outputs/NFL2025_W"+str(week)+"_"+div+".png","-d",str(960*2)],shell=True)
    

