import fitz  # PyMuPDF
import os
import argparse

def generate_html(page_data, html_path):
    """Generates the HTML file from the extracted page data."""

    # HTML head with CSS styles from the example output.html
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Conversion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .page {
            background-color: #fff;
            border: 1px solid #ddd;
            width: 90%;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .page img {
            width: 100%;
            height: auto;
            display: block;
            margin-bottom: 20px;
        }
        .text-content {
            font-size: 1.2em;
            line-height: 1.6;
            text-align: justify;
        }
        .page-number {
            text-align: right;
            color: #888;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
"""

    # Add each page's content
    for i, page in enumerate(page_data):
        html_content += f'    <!-- Page {i + 1} -->\\n'
        html_content += '    <div class="page">\\n'

        # Add images
        for img_path in page['images']:
            html_content += f'        <img src="{img_path}" alt="Image from page {i + 1}">\\n'

        # Add text
        if page['text'].strip():
            html_content += '        <div class="text-content">\\n'
            # Replace newlines with <br> tags for basic formatting
            formatted_text = page['text'].strip().replace('\n', '<br>')
            html_content += f'            <p>{formatted_text}</p>\\n'
            html_content += '        </div>\\n'

        html_content += f'        <div class="page-number">{i + 1}/{len(page_data)}</div>\\n'
        html_content += '    </div>\\n\\n'

    # HTML closing tags
    html_content += """
</body>
</html>
"""

    # Write the content to the HTML file
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def convert_pdf_to_html(pdf_path, html_path, images_dir="images"):
    """
    Converts a PDF file to an HTML file with extracted images.
    """
    print(f"Starting conversion of '{pdf_path}'...")

    # Ensure the images directory exists
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        return

    page_data = []

    # Process each page
    for page_num, page in enumerate(doc):
        page_content = {'images': [], 'text': ''}

        # 1. Extract Images
        img_list = page.get_images(full=True)
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Get image extension
            ext = base_image["ext"]
            image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{ext}"
            image_path = os.path.join(images_dir, image_filename)

            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            page_content['images'].append(image_path)

        # 2. Extract Text
        page_content['text'] = page.get_text()

        page_data.append(page_content)
        print(f"Processed page {page_num + 1}/{len(doc)}")

    doc.close()

    # 3. Generate HTML
    print("Generating HTML file...")
    generate_html(page_data, html_path)

    print(f"Conversion complete. Output saved to '{html_path}' and '{images_dir}/'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a PDF file to an HTML file with extracted images.")
    parser.add_argument("input_pdf", help="The path to the input PDF file.")
    parser.add_argument("-o", "--output_html", default="output.html", help="The path to the output HTML file.")
    parser.add_argument("-i", "--images_dir", default="images", help="The directory to save extracted images.")

    args = parser.parse_args()

    # Check if input PDF exists
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' not found.")
    else:
        convert_pdf_to_html(args.input_pdf, args.output_html, args.images_dir)
