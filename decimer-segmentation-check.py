from decimer_segmentation import segment_chemical_structures_from_file

result = segment_chemical_structures_from_file(
    "D:\\Projects\\DECIMER Project\\core\\output\\rendered_pages\\sample_pdf_1\\sample_pdf_1_page_007.png",
    expand=True
)

print(type(result))
print(len(result))

if len(result):
    print(type(result[0]))