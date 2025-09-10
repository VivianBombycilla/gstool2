# Graphical Standings Tool

`gstool.py` provides a way to turn data from a sports league (as a pandas DataFrame) into a nice SVG graphic.

## Dependencies
The following Python libraries are required:
- **pandas**
- (Optional) pandas has some optional dependencies to use certain useful functions such as `read_excel`.

## Plans
The next new things I want to do with this project:
- Add an option to have dashed lines (e.g., for bye weeks)
- Docstrings
- Add an option to embed image files and fonts in the SVG (for more portability)
- Use CSS to make the SVGs better and easier to handle
- Use kwargs to make the custom SVG API better and easier to handle