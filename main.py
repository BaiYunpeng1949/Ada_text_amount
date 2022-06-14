from pptx import Presentation
from pptx.enum.dml import MSO_THEME_COLOR_INDEX
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Inches
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.chart import XL_TICK_MARK
from pptx.util import Pt


# For testing fetch function
# I made a new comment
# 14 June 2022

def generate_slide_trials():
    pr1 = Presentation()

    # Refers to the layout of each slide.
    # 0 = Title slide, 1 = Title and Content, 3 = Section Header.
    slide1_register = pr1.slide_layouts[0]

    # Slide 1:
    # Add initial slide to presentation
    slide1 = pr1.slides.add_slide(slide1_register)

    # Add text to layouts.
    title = slide1.shapes.title
    # Placeholder = Item in the layout.
    subtitle = slide1.placeholders[1]

    # Insert text into the placeholders.
    title.text = "Test xixixi"
    subtitle.text = "lah lah lah"

    # Slide 2:
    slide2_register = pr1.slide_layouts[1]
    slide2 = pr1.slides.add_slide(slide2_register)
    # Edit bullet point slide.
    title2 = slide2.shapes.title
    title2.text = "Now for some bullet points"

    bullet_point_box = slide2.shapes
    bullet_points_lvl1 = bullet_point_box.placeholders[1]
    bullet_points_lvl1.text = "lah lah lah hei hei hei"

    # Create the second level of bullet points.
    bullet_points_lvl2 = bullet_points_lvl1.text_frame.add_paragraph()
    bullet_points_lvl2.text = "du du du"
    bullet_points_lvl2.level = 1

    bullet_points_lvl3 = bullet_points_lvl1.text_frame.add_paragraph()
    bullet_points_lvl3.text = "du du du 2"
    bullet_points_lvl3.level = 2

    bullet_points_lvl4 = bullet_points_lvl1.text_frame.add_paragraph()
    bullet_points_lvl4.text = "du du du 3"
    bullet_points_lvl4.level = 3

    # Slide 3:
    slide3_register = pr1.slide_layouts[5]
    slide3 = pr1.slides.add_slide(slide3_register)

    title3 = slide3.shapes.title
    title3.text = "Picture"

    # Add image
    img1 = "image_1.jpg"

    from_left = Inches(3)
    from_top = Inches(2)
    add_picture = slide3.shapes.add_picture(img1, from_left, from_top)

    # Slide 4
    slide4_register = pr1.slide_layouts[5]
    slide4 = pr1.slides.add_slide(slide4_register)

    title4 = slide4.shapes.title
    title4.text = "Shapework"

    # Create shapes
    # Shape 1
    left1 = top1 = width1 = height1 = Inches(2)
    add_shape1 = slide4.shapes.add_shape(MSO_SHAPE_TYPE.PICTURE, left1, top1, width1, height1)

    # Shape 2
    left2 = Inches(6)
    top2 = Inches(2)
    width2 = height2 = Inches(2)
    shape2 = slide4.shapes.add_shape(MSO_SHAPE_TYPE.PICTURE, left2, top2, width2, height2)

    # Change the shape's main color
    fill_shape2 = shape2.fill
    fill_shape2.solid()
    fill_shape2.fore_color.theme_color = MSO_THEME_COLOR_INDEX.LIGHT_2

    # Slide 4:
    slide5_register = pr1.slide_layouts[5]
    slide5 = pr1.slides.add_slide(slide5_register)

    # Title:
    title5 = slide5.shapes.title
    title5.text = "Graphs"

    # Build graph
    graph_info = CategoryChartData()
    graph_info.categories = ["A", "B", "C"]
    graph_info.add_series("Series 1", (15, 11, 18))

    # Add graph to slide with positioning
    left_graph = Inches(2)
    top_graph = Inches(2)
    width_graph = Inches(6)
    height_graph = Inches(4)
    # slide5.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    #                         left_graph, top_graph, width_graph, height_graph,
    #                         graph_info)
    graph1_frame = slide5.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                                           left_graph, top_graph, width_graph, height_graph,
                                           graph_info)
    graph1 = graph1_frame.chart

    # Edit graph
    category_axis = graph1.category_axis
    category_axis.has_major_gridlines = True
    category_axis.minor_tick_mark = XL_TICK_MARK.OUTSIDE
    category_axis.tick_labels.font.italic = True
    category_axis.tick_labels.font.size = Pt(24)

    # Slide 6:
    slide6_register = pr1.slide_layouts[5]
    slide6 = pr1.slides.add_slide(slide6_register)

    title6 = slide6.shapes.title
    title6.text = "Table"

    # Add Graph to slide
    left_table = Inches(1)
    top_table = Inches(2)
    width_table = Inches(8)
    height_table = Inches(3)
    # slide6.shapes.add_table(3,4, left_table, top_table,
    #                         width_table, height_table)
    table1_frame = slide6.shapes.add_table(3,4, left_table, top_table,
                                          width_table, height_table)

    # Populating a table
    table1 = table1_frame.table
    cell = table1.cell(0, 0)
    cell.text = "Insert the title here"

    cell = table1.cell(1, 0)
    cell.text = "Insert Value here"

    # Rotate the shape
    shape2.rotation = 90

    # Slide 7
    slide7_register = pr1.slide_layouts[0]
    slide7 = pr1.slides.add_slide(slide7_register)

    title7 = slide7.shapes.title
    title7.text = "Hyperlink"

    # Adding hyperlinks
    para1 = slide7.placeholders[1].text_frame.paragraphs[0]
    addrun1 = para1.add_run()
    addrun1.text = "Google Hyperlink"
    hlink1 = addrun1.hyperlink
    hlink1.address = "https://www.google.com"

    pr1.save("trial_slides.pptx")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    generate_slide_trials()
