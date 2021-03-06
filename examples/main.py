from handwritten_notes_maker import HandwrittenNotesMaker

hnmaker = HandwrittenNotesMaker(left_margin=140, right_margin=40, top_margin=200, bottom_margin=40, line_space=120, space_width=50, character_rotation_error=(5,-15), \
    papers_dir='./paper_images/blank', font_path='./fonts/1.ttf', spacing_error=3, vertical_error=3, character_padding_x=2, character_padding_y=3,
    character_scale_x_min=0.6, character_scale_y_min=0.75)
hnmaker.make_font("normal", 80)
hnmaker.make_font("heading", 120)
hnmaker.make_font("subheading", 80)

hnmaker.write_heading("heading", "Lorem Ipsum!!!", new_line=True)
hnmaker.write_heading("subheading", "- Lorem Ipsum", align="right", new_line=True)
hnmaker.insert_vertical_space(60)

hnmaker.write_text("normal", "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.", new_line=True)
hnmaker.insert_image('img.jpeg', dims=(800,1200))
hnmaker.save_to_pdf('ok.pdf')