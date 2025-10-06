import xml.etree.ElementTree as ET

def svg_line(x1,x2,y1,y2,stroke="black",stroke_width=1,stroke_linecap="butt"):
    return ET.Element("line",
                      attrib={
                          "x1":str(x1),
                          "x2":str(x2),
                          "y1":str(y1),
                          "y2":str(y2),
                          "stroke":str(stroke),
                          "stroke-width":str(stroke_width),
                          "stroke-linecap":str(stroke_linecap)
                      })
def svg_rect(x,y,width,height,stroke="none",stroke_width=1,fill="black"):
    return ET.Element("rect",
                      attrib={
                          "x":str(x),
                          "y":str(y),
                          "width":str(width),
                          "height":str(height),
                          "stroke":str(stroke),
                          "stroke-width":str(stroke_width),
                          "fill":fill
                      })
def svg_circle(cx,cy,r,stroke="none",stroke_width=1,fill="black"):
    return ET.Element("circle",
                      attrib={
                          "cx":str(cx),
                          "cy":str(cy),
                          "r":str(r),
                          "stroke":str(stroke),
                          "stroke-width":str(stroke_width),
                          "fill":fill
                      })
def svg_polygon(x,y,stroke="none",stroke_width=1,fill="black"):
    points_intermediate = [str(a)+","+str(b) for (a,b) in zip(x,y)]
    points = " ".join(points_intermediate)
    return ET.Element("polygon",
                      attrib={
                          "points":str(points),
                          "stroke":str(stroke),
                          "stroke-width":str(stroke_width),
                          "fill":str(fill)
                      })
def svg_text(x,y,text,stroke="none",fill="black",font_size="12pt",font_family="auto",text_anchor="start",dx=0,dy=0,transform="none",identity=""):
    text_el = ET.Element("text",
                      attrib={
                          "x":str(x),
                          "y":str(y),
                          "stroke":str(stroke),
                          "fill":str(fill),
                          "font-size":str(font_size),
                          "font-family":str(font_family),
                          "text-anchor":str(text_anchor),
                          "dx":str(dx),
                          "dy":str(dy),
                          "transform":str(transform),
                          "id":str(identity)
                      })
    text_el.text = text
    return text_el

def svg_image(x,y,href,width=None,height=None):
    match (width,height):
        case (None,None):
            raise ValueError("width or height required")
        case (_,None):
            return ET.Element("image",
                                attrib={
                                    "x":str(x),
                                    "y":str(y),
                                    "width":str(width),
                                    "xlink:href":str(href),
                                    "href":str(href)
                                })
        case (None,_):
            return ET.Element("image",
                                attrib={
                                    "x":str(x),
                                    "y":str(y),
                                    "height":str(height),
                                    "xlink:href":str(href),
                                    "href":str(href)
                                })
        case (_,_):
            return ET.Element("image",
                                attrib={
                                    "x":str(x),
                                    "y":str(y),
                                    "width":str(width),
                                    "height":str(height),
                                    "xlink:href":str(href),
                                    "href":str(href)
                                })

def scale(from_range,to_range,value):
    (from_min,from_max) = from_range
    (to_min  ,to_max  ) = to_range
    proportion = (value-from_min)/(from_max-from_min)
    return to_min + (proportion * (to_max-to_min))

# SVG Graphic Class
class SVG:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.root = ET.Element("svg",attrib={"width":str(width),"height":str(height),"xmlns":"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink","version":"2.0"})
        self.tree = ET.ElementTree(self.root)   

# This class represents the plotted area.
# I'm not using an svg object with viewBox attribute because I will want to draw things outside of the box defined by the plot limits, such as axis titles and other annotations. 
class SVG_Plot:
    def __init__(self,pos,width,height,x_lims,y_lims):
        self.pos = pos
        self.x,self.y = self.pos
        self.width = width
        self.height = height
        self.x_lims = x_lims
        self.x_min,self.x_max = self.x_lims
        self.y_lims = y_lims
        self.y_min,self.y_max = self.y_lims
        self.element = ET.Element("g")
    # Translates x-y coordinates from the plot axis to absolute coordinates
    def coords_plot2abs(self,coords):
        x,y = coords
        new_x = scale(self.x_lims,(self.x            ,self.x+self.width),x)
        new_y = scale(self.y_lims,(self.y+self.height,self.y           ),y)
        return (new_x,new_y)
    def coords_plot2abs_x(self,x):
        return scale(self.x_lims,(self.x,self.x+self.width),x)
    def coords_plot2abs_y(self,y):
        return scale(self.y_lims,(self.y+self.height,self.y),y)
    def coords_length2abs_x(self,length):
        return length*self.width/(self.x_max-self.x_min)
    def coords_length2abs_y(self,length):
        return length*self.height/(self.y_max-self.y_min)

    # Check if value is in the graph
    def inbounds_x(self,x):
        return (x >= self.x_min) and (x <= self.x_max)
    def inbounds_y(self,y):
        return (y >= self.y_min) and (y <= self.y_max)

    # Adds grid to element using the breaks given
    def add_grid(self,x_breaks,y_breaks,stroke="black",stroke_width=1):
        grid_group = ET.Element("g")
        for x_break in x_breaks:
            if not self.inbounds_x(x_break): continue
            x1,y1 = self.coords_plot2abs((x_break,self.y_min))
            x2,y2 = self.coords_plot2abs((x_break,self.y_max))
            grid_group.append(svg_line(
                x1 = x1,
                y1 = y1,
                x2 = x2,
                y2 = y2,
                stroke = stroke,
                stroke_width = stroke_width,
                stroke_linecap="square"
        ))
        for y_break in y_breaks:
            if not self.inbounds_y(y_break): continue
            x1,y1 = self.coords_plot2abs((self.x_min,y_break))
            x2,y2 = self.coords_plot2abs((self.x_max,y_break))
            grid_group.append(svg_line(
                x1 = x1,
                y1 = y1,
                x2 = x2,
                y2 = y2,
                stroke = stroke,
                stroke_width = stroke_width,
                stroke_linecap="square"
        ))
        self.element.append(grid_group)

    # Adds axis labels
    def add_axis_labels(self,x_breaks,y_breaks,x_labels,y_labels,stroke="none",fill="black",font_size="12pt",font_family="auto"):
        group = ET.Element("g")
        num_breaks_x = len(x_breaks)
        num_breaks_y = len(y_breaks)
        if num_breaks_x != len(x_labels):
            raise ValueError("Number of x breaks/labels not equal!")
        if num_breaks_y != len(y_labels):
            raise ValueError("Number of y breaks/labels not equal!")
        for (x_break,x_label) in zip(x_breaks,x_labels):
            # x_break = x_breaks[i]
            # x_label = x_labels[i]
            if not self.inbounds_x(x_break): continue
            x,y = self.coords_plot2abs((x_break,self.y_min))
            group.append(svg_text(
                x = x,
                y = y,
                dy = "1em",
                text = str(x_label),
                stroke = stroke,
                fill = fill,
                font_size = font_size,
                font_family = font_family,
                text_anchor = "middle"
            ))
        for (y_break,y_label) in zip(y_breaks,y_labels):
            if not self.inbounds_y(y_break): continue
            x,y = self.coords_plot2abs((self.x_min,y_break))
            group.append(svg_text(
                x = x-0.5,
                y = y,
                # dx = "-0.5ex",
                dy = "0.5ex",
                text = str(y_label),
                stroke = stroke,
                fill = fill,
                font_size = font_size,
                font_family = font_family,
                text_anchor = "end"
            ))
        self.element.append(group)

    ### ANNOTATIONS
    # These methods add graphics to the plot defined by the plot's x and y coordinates.
    # DOT: Geometric circle whose radius is defined either relative to the x-axis or y-axis; this data is encoded in the "axis" parameter.
    def annotate_dot(self,x,y,r,axis="y",stroke="none",stroke_width=1,fill="black"):
        abs_x,abs_y = self.coords_plot2abs((x,y))
        match axis:
            case "x":
                abs_r = self.coords_length2abs_x(r)
            case "y":
                abs_r = self.coords_length2abs_y(r)
        self.element.append(svg_circle(abs_x,abs_y,abs_r,stroke=stroke,stroke_width=stroke_width,fill=fill))
    # POLYGON: Takes lists of x and y coordinates. 
    def annotate_polygon(self,x,y,stroke="none",stroke_width=1,fill="black"):
        abs_x = map(self.coords_plot2abs_x,x)
        abs_y = map(self.coords_plot2abs_y,y)
        self.element.append(svg_polygon(abs_x,abs_y,stroke=stroke,stroke_width=stroke_width,fill=fill))
    # IMAGE: Centrally aligned. preserveAspectRatio is set to xMidYMid meet by default, maybe I'll add customization later.
    def annotate_image(self,x,y,href,height):
        abs_x,abs_y = self.coords_plot2abs((x,y+height/2))
        # abs_width = self.coords_length2abs_x(width)
        abs_height = self.coords_length2abs_y(height)
        self.element.append(svg_image(abs_x-self.width/2,abs_y,href,width=self.width,height=abs_height))
    # PILL_V: Pill, vertical. Centrally aligned. "Size" is half the length of the flat side.
    def annotate_pill_v(self,x,y,size,r,fill="black",dash_size = 0.1):
        group = ET.Element("g")
        abs_height = self.coords_length2abs_y(size)
        abs_width = self.coords_length2abs_y(r)
        abs_x1 = self.coords_plot2abs_x(x) - abs_width
        abs_y1 = self.coords_plot2abs_y(y) - abs_height
        abs_x2 = abs_x1+2*abs_width
        abs_y2 = abs_y1+2*abs_height
        # abs_midy1 = abs_y1+0.9*abs_height
        abs_midy = abs_y1+(1-(dash_size/2))*abs_height
        path = (
            "M %f,%f" % (abs_x1,abs_y1)
            + "A%f,%f 0 0 1 %f,%f" % (abs_width,abs_width,abs_x2,abs_y1)
            + "L%f,%f" % (abs_x2,abs_y2)
            + "A%f,%f 0 0 1 %f,%f" % (abs_width,abs_width,abs_x1,abs_y2)
            + "Z"
        )
        pill = ET.Element("path",d = path,fill=fill)
        rect = svg_rect(x = abs_x1,y = abs_midy,width = abs_width*2,height = abs_height*dash_size,fill = "white")
        group.append(pill)
        group.append(rect)    
        self.element.append(group)

    
