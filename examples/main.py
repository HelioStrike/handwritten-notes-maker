from handwritten_notes_maker import HandwrittenNotesMaker

hnmaker = HandwrittenNotesMaker(left_margin=140, right_margin=40, top_margin=200, bottom_margin=40, line_space=120, papers_dir='./paper_images/blank', font_path='./fonts/1.ttf', human_error=4)
hnmaker.make_font("normal", 80)
hnmaker.make_font("heading", 120)
hnmaker.make_font("subheading", 80)

hnmaker.write_heading("heading", "Lorem Ipsum!!!")
hnmaker.write_heading("subheading", "- Lorem Ipsum", align="right")
hnmaker.insert_vertical_space(60)

hnmaker.write_text("normal", "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
hnmaker.insert_image('img.jpeg', dims=(700,1200))
hnmaker.save_to_pdf('ok.pdf')