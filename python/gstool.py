from gstool_svg import *
from gstool_data_manip import *

def compute_segment_coords(shared_with,num_in_group,segment_size,segment_rel_width):
    parts = shared_with * (segment_rel_width + 1) - 1
    y_per_part = 2*segment_size/parts 
    low_part = (shared_with-num_in_group)*(segment_rel_width+1)
    high_part = low_part + segment_rel_width
    low_y_adj  = -segment_size + low_part  * y_per_part
    high_y_adj = -segment_size + high_part * y_per_part
    return low_y_adj,high_y_adj

def make_GS_Plot(
    # DATA
    dots_data,
    segments_data,
    labels_data,
    teams_data,

    # PLOT SETTINGS
    plot_width = 224,
    x_lims = "auto", # either tuple (x_min,x_max) or "auto"
    y_lims = "auto", # either tuple (x_min,x_max) or "auto"
    expand_y = 0.5, # amount of padding to add
    
    # BREAKS
    x_break_size = 3,
    y_break_size = 3,
    axis_labels_size = 6,

    # DOTS AND SEGMENTS
    dot_size = 0.4, # radius (y) of dots
    segment_scale = 0.8, # relative height of segments compared to dot_size 
    segment_rel_width = 4, # how many times thicker the segments should be than the spaces between the segments
    
    # TEXT
    plot_title = "WNBA Graphical Standings – Jul 29, 2025",
    plot_title_size = 10,
    vertical_axis_title = "Wins above .500",
    horizontal_axis_title = "Game",

    # LABELS
    label_size = 2.5,
    label_shared_x_offset = 0.45,
    label_x_offset = 0.7,
    label_y_offset = 1,
    
    # AESTHETICS
    style = "", # provide the contents of the <style> object at the start of the file
    font_family="Saira",

    # AUXILIARY FILE PATHS
    path_logos = "Logos/",
    path_output = "test3.svg"
    ):

    # Find plot limits
    if x_lims == "auto":
        # Automatically compute limits of graph
        x_min,x_max = (min(dots_data.x),max(dots_data.x))
        y_min,y_max = (min(dots_data.y),max(dots_data.y))
    else:
        x_min,x_max = x_lims
        y_min,y_max = y_lims
    expand_x = expand_y*112/plot_width*(x_max-x_min)/(y_max-y_min)
    x_lims = [x_min-expand_x,x_max+expand_x]
    y_lims = [y_min-expand_y,y_max+expand_y]

    # Initialize SVG Object
    svg = SVG(256,144)

    # STYLE
    style_element = ET.Element("style")
    style_element.text = style
    svg.root.append(style_element)

    # Background
    svg.root.append(svg_rect(0,0,256,144,stroke="none",fill="white"))

    ### PLOT LABELS
    # Plot Title
    svg.root.append(svg_text(
        x = 128,
        y = 12,
        text = plot_title,
        font_size = plot_title_size,
        font_family = font_family,
        text_anchor = "middle"
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
        x = 128,
        y = 140,
        text = horizontal_axis_title,
        font_family = font_family,
        font_size = 6,
        text_anchor = "middle"
    ))
    # Tag
    svg.root.append(svg_text(
        x = 254.5,
        y = 142,
        text = "Graphic by Vivian (vbbcla)",
        font_size = 4,
        font_family = font_family,
        text_anchor = "end"
    ))

    ### PLOT
    plot = SVG_Plot((20,16),plot_width,112,x_lims=x_lims,y_lims=y_lims)
    
    ## Draw axes and grid lines
    # Minors
    plot.add_grid(
        x_breaks = range(0,x_max+1,1),
        y_breaks = range(y_min,y_max+1,1),
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
        poly_x = (seg_row.x1,seg_row.x2,seg_row.x2,seg_row.x1)
        poly_y = (
            seg_row.y1+seg_row.y_adj_high,
            seg_row.y2+seg_row.y_adj_high,
            seg_row.y2+seg_row.y_adj_low,
            seg_row.y1+seg_row.y_adj_low,
        )
        plot.annotate_polygon(poly_x,poly_y,fill=teams_data.loc[seg_row.team].LineColour)
    # Dots
    dots_rows = list(dots_data.itertuples(index=False))
    for dot_row in dots_rows:
        # plot.annotate_dot(dot_row.x,dot_row.y,dot_size,"y",fill="rgb(30%,30%,30%)")
        plot.annotate_pill_v(dot_row.x,dot_row.y,size = dot_size*0.7,r=dot_size*0.3,fill="rgb(30%,30%,30%)")
    # Teams
    labels_rows = list(labels_data.itertuples(index=False))
    for label_row in labels_rows:
        plot.annotate_image(
            x=label_row.x+label_shared_x_offset+label_x_offset*(label_row.numInGroup-1),
            y=label_row.y,#+logo_y_offset*team_row.YOffset,
            href=path_logos+teams_data.loc[label_row.team].ImagePath,
            width=label_size,
            height=label_size
        )

    svg.root.append(plot.element)
    svg.tree.write(path_output)

