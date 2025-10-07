from gstool_svg import *
from gstool_data_manip import *

def compute_segment_coords(
    shared_with: int,
    num_in_group: int,
    segment_size: float,
    segment_rel_width: float
):
    """Computes the relative y position of the segment, given aesthetic settings."""
    parts = shared_with * (segment_rel_width + 1) - 1
    y_per_part = 2*segment_size/parts 
    low_part = (shared_with-num_in_group)*(segment_rel_width+1)
    high_part = low_part + segment_rel_width
    low_y_adj  = -segment_size + low_part  * y_per_part
    high_y_adj = -segment_size + high_part * y_per_part
    return low_y_adj,high_y_adj

def find_label_offsets(
    label_loop_threshold: int,
    num_in_group: int,
    shared_with: int
):
    """Computes the appropriate adjustments to be made to a label, taking into consideration wrapping settings."""
    col = (num_in_group-1) % label_loop_threshold
    row = (num_in_group-1) // label_loop_threshold
    rows = (shared_with-1) // label_loop_threshold + 1
    x_offset = col
    y_offset = - row + 0.5*(rows-1)
    return x_offset,y_offset

def dashed_segment(
    pos1,
    pos2,
    y_adj,
    dashes: Sequence[int]
):
    x1,y1 = pos1
    x2,y2 = pos2
    total_length = sum(dashes)
    curr_length = 0
    polygon_xs = []
    polygon_ys = []
    for i in range(len(dashes)):
        new_length = dashes[i]
        if i % 2 == 1:
            curr_length += new_length
            continue
        coeff1 = curr_length/total_length
        coeff2 = (curr_length+new_length)/total_length
        new_x1 = x1 + coeff1 * (x2-x1)
        new_x2 = x1 + coeff2 * (x2-x1)
        new_y1 = y1 + coeff1 * (y2-y1)
        new_y2 = y1 + coeff2 * (y2-y1)
        new_poly_x = (
            new_x1,
            new_x2,
            new_x2,
            new_x1
        )
        new_poly_y = (
            new_y1+y_adj[1],
            new_y2+y_adj[1],
            new_y2+y_adj[0],
            new_y1+y_adj[0],
        )
        polygon_xs.append(new_poly_x)
        polygon_ys.append(new_poly_y)
        curr_length += new_length
    return polygon_xs,polygon_ys 

def make_GS_Plot(
    # DATA
    teams,
    games_xl,
    teams_xl,
    points_from_result,
    coords_from_state,
    # # DATA
    # dots_data,
    # segments_data,
    # labels_data,
    # teams_data,

    # PLOT SETTINGS
    plot_width = 224,
    x_lims = "auto", # either tuple (x_min,x_max) or "auto"
    y_lims = "auto", # either tuple (x_min,x_max) or "auto"
    expand_y = 0.5, # amount of padding to add
    
    # BREAKS
    x_break_size = 3,
    y_break_size = 3,
    x_minor_break_size = 1,
    y_minor_break_size = 1,
    axis_labels_size = 6,

    # DOTS AND SEGMENTS
    dot_size = 0.4, # radius (y) of dots
    # segment_scale = 0.8, # relative height of segments compared to dot_size 
    segment_rel_width = 4, # how many times thicker the segments should be than the spaces between the segments
    dashed_segment_style = [2,1,2,1,2,1,2,1,2],
    
    # TEXT
    plot_title = "PLOT TITLE",
    plot_title_size = 10,
    vertical_axis_title = "Vertical axis title",
    horizontal_axis_title = "Horizontal axis title",

    # LABELS
    label_size = 2.5, # label size (y)
    label_shared_x_offset = 0.45,
    label_x_offset = 0.7,
    label_y_offset = 1,
    label_loop_threshold = 5, # max number of logos in a row
    
    # AESTHETICS
    style = "", # provide the contents of the <style> object at the start of the file
    font_family = "auto",
    annotations = [], # additional elements which will be added at the end.
    # COLOURS
    background_colour = "#ffffff",

    # AUXILIARY FILE PATHS
    path_logos = "Logos/",
    path_output = "test.svg"
    ):
    """Creates a Graphical Standings svg file at the path indicated, using the data and aesthetic settings provided."""

    dots_data,segments_data,labels_data,teams_data = produce_data_frames(teams,games_xl,teams_xl,points_from_result,coords_from_state)

    # Find plot limits
    if x_lims == "auto":
        # Automatically compute limits of graph
        x_min,x_max = (min(dots_data.x),max(dots_data.x))
        y_min,y_max = (min(dots_data.y),max(dots_data.y))
    else:
        x_min,x_max = x_lims
        y_min,y_max = y_lims

    # Compute the appropriate amount to expand the x axis.
    # Currently, this expands the x axis proportionally to the y-axis, so that the resulting "ticks" are the same size. In the future, this will probably be called the "square" option.
    expand_x = expand_y*112/plot_width*(x_max-x_min)/(y_max-y_min)
    
    # Expand axes
    x_lims = [x_min-expand_x,x_max+expand_x]
    y_lims = [y_min-expand_y,y_max+expand_y]

    # Initialize SVG Object
    svg = SVG(256,144)

    # Add style
    style_element = ET.Element("style")
    style_element.text = style
    svg.root.append(style_element)

    # Background
    svg.root.append(svg_rect(0,0,256,144,stroke="none",fill=background_colour))

    ### PLOT LABELS
    # Plot Title
    svg.root.append(svg_text(
        x = 128,
        y = 12,
        text = plot_title,
        font_size = plot_title_size,
        font_family = font_family,
        text_anchor = "middle",
        identity = "title"
    ))
    ## Axis Titles
    # Vertical axis title
    svg.root.append(svg_text(
        x = 8,
        y = 72,
        text = vertical_axis_title,
        font_family = font_family,
        font_size = 6,
        text_anchor = "middle",
        transform = "rotate(-90,8,72)"
    ))
    # Horizontal axis title
    svg.root.append(svg_text(
        x = 20+plot_width/2,
        y = 140,
        text = horizontal_axis_title,
        font_family = font_family,
        font_size = 6,
        text_anchor = "middle"
    ))

    ### PLOT
    plot = SVG_Plot((20,16),plot_width,112,x_lims=x_lims,y_lims=y_lims)
    
    ## Draw axes and grid lines
    # Minors
    plot.add_grid(
        x_breaks = range(0,x_max+1,x_minor_break_size),
        y_breaks = range(y_min-y_min%y_minor_break_size,y_max+1,y_minor_break_size),
        stroke_width = 0.5,
        stroke = "rgb(90%,90%,90%)"
    )
    # Majors
    plot.add_grid(
        x_breaks = range(0,x_max+1,x_break_size),
        y_breaks = range(y_min-y_min%y_break_size,y_max+1,y_break_size),
        stroke_width = 0.5,
        stroke = "rgb(80%,80%,80%)"
    )
    # Axes
    plot.add_grid([0],[0],stroke_width=0.5,stroke="rgb(50%,50%,50%)")

    # Axis Labels
    plot.add_axis_labels(
        x_breaks = range(0,x_max+1,x_break_size),
        y_breaks = range(y_min-y_min%y_break_size,y_max+1,y_break_size),
        x_labels = range(0,x_max+1,x_break_size),
        y_labels = range(y_min-y_min%y_break_size,y_max+1,y_break_size),
        font_family = font_family,
        font_size = axis_labels_size,
        fill = "rgb(30%,30%,30%)"
    )

    ### DATA
    # Segments
    segments_data["y_adj"] = segments_data.apply(lambda row: compute_segment_coords(row.sharedWith,row.numInGroup,dot_size,segment_rel_width),axis=1)
    segments_data[["y_adj_low","y_adj_high"]] = segments_data["y_adj"].apply(pd.Series)
    segments_rows = list(segments_data.itertuples(index=False))
    for seg_row in segments_rows:
        if seg_row.modifier1 == False:
            poly_x = (seg_row.x1,seg_row.x2,seg_row.x2,seg_row.x1)
            poly_y = (
                seg_row.y1+seg_row.y_adj_high,
                seg_row.y2+seg_row.y_adj_high,
                seg_row.y2+seg_row.y_adj_low,
                seg_row.y1+seg_row.y_adj_low,
            )
            plot.annotate_polygon(poly_x,poly_y,fill=teams_data.loc[seg_row.team].LineColour)
        else:
            poly_xs,poly_ys = dashed_segment(seg_row.pos1,seg_row.pos2,seg_row.y_adj,dashed_segment_style)
            for poly_x,poly_y in zip(poly_xs,poly_ys):
                plot.annotate_polygon(poly_x,poly_y,fill=teams_data.loc[seg_row.team].LineColour)

    # Dots
    dots_rows = list(dots_data.itertuples(index=False))
    for dot_row in dots_rows:
        # plot.annotate_dot(dot_row.x,dot_row.y,dot_size,"y",fill="rgb(30%,30%,30%)")
        plot.annotate_pill_v(dot_row.x,dot_row.y,size = dot_size*0.7,r=dot_size*0.3,fill="rgb(30%,30%,30%)")
    # Teams
    labels_rows = list(labels_data.itertuples(index=False))
    for label_row in labels_rows:
        x_offset,y_offset = find_label_offsets(label_loop_threshold,label_row.numInGroup,label_row.sharedWith)
        plot.annotate_image(
            x=label_row.x+label_shared_x_offset+label_x_offset*x_offset,
            y=label_row.y+label_y_offset*y_offset,
            href=path_logos+teams_data.loc[label_row.team].ImagePath,
            height=label_size
        )

    svg.root.append(plot.element)
    for annotation in annotations:
        svg.root.append(annotation)
    svg.tree.write(path_output)



# Find the points earned from a result. This must be adjusted for each sport.
def points_from_result_NFL(team: str,winner: str):
    if winner == team:
        return 1
    elif winner == "TIE":
        return 0
    else:
        return -1

# From the number of games and points give the X and Y coordinates from a given state.
def coords_from_state_NFL(games: int,points: int) -> tuple[int,float]:
    return games,points

games_xl,teams_xl = read_excel("data_NFL2025.xlsx","Input_Games","Input_Teams")
team_dots_data,team_segments_data,team_labels_data = process_team("New Orleans Saints",games_xl,points_from_result_NFL)
all_teams = list(teams_xl.index)
# dots_data,segments_data,labels_data,teams_data = produce_data_frames(all_teams,games_xl,teams_xl,points_from_result_NFL,coords_from_state_NFL)
make_GS_Plot(all_teams,games_xl,teams_xl,points_from_result_NFL,coords_from_state_NFL)