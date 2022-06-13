from pptx import Presentation
from pptx.enum.dml import MSO_THEME_COLOR_INDEX
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Inches


# For testing fetch function
# I made a new comment

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

    # Rotate the shape
    shape2.rotation = 90


    pr1.save("trial_slides.pptx")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    generate_slide_trials()
