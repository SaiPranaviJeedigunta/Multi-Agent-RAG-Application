import logging
import time
from pathlib import Path
import pandas as pd
import json
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling_core.transforms.chunker import HierarchicalChunker

# Configure logging
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

# Define the resolution scale for images
IMAGE_RESOLUTION_SCALE = 2.0

# Paths to local PDF files
file_paths = [
    "The Economics of Private Equity: A Critical Review.pdf",
    "Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios.pdf",
    "An Introduction to Alternative Credit.pdf"
]

# Output directory
output_dir = Path("parsed_content")  # Replace with your desired output directory path
output_dir.mkdir(parents=True, exist_ok=True)

# Function to process PDF files
def process_pdf(file_path):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    conv_res = doc_converter.convert(file_path)
    doc_filename = Path(file_path).stem

    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_image_filename = output_dir / f"{doc_filename}-page-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")
        _log.info(f"Saved page image: {page_image_filename}")

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            table_image_filename = output_dir / f"{doc_filename}-table-{table_counter}.png"
            with page_image_filename.open("wb") as fp:
                element.image.pil_image.save(fp, "PNG")
            _log.info(f"Saved table image: {table_image_filename}")

            # Save the table as CSV and HTML
            table_df: pd.DataFrame = element.export_to_dataframe()
            table_csv_filename = output_dir / f"{doc_filename}-table-{table_counter}.csv"
            table_df.to_csv(table_csv_filename)
            table_html_filename = output_dir / f"{doc_filename}-table-{table_counter}.html"
            with table_html_filename.open("w") as fp:
                fp.write(element.export_to_html())
            _log.info(f"Saved table CSV: {table_csv_filename} and HTML: {table_html_filename}")

        if isinstance(element, PictureItem):
            picture_counter += 1
            picture_image_filename = output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            with picture_image_filename.open("wb") as fp:
                element.image.pil_image.save(fp, "PNG")
            _log.info(f"Saved picture image: {picture_image_filename}")

    # Apply hierarchy-aware chunking for further processing
    chunks = list(HierarchicalChunker(min_chunk_length=500, max_chunk_length=1500, split_by='paragraph', overlap=50).chunk(conv_res.document))

    # Prepare to save chunk data
    chunk_data = []

    # Process each chunk and display metadata
    for i, chunk in enumerate(chunks):
        text_content = chunk.text  # Directly access 'text' attribute
        # Convert meta information to a dictionary, or extract relevant fields to avoid serialization issues
        meta_info = chunk.meta.dict() if hasattr(chunk.meta, "dict") else str(chunk.meta)

        # Store each chunk's content and metadata for further use
        chunk_metadata = {
            "document": doc_filename,
            "chunk_id": i,
            "text": text_content,
            "meta": meta_info
        }
        chunk_data.append(chunk_metadata)
        print(f"Chunk {i}: {chunk_metadata['text'][:100]}...")  # Preview the first 100 characters

    # Save chunks data to a JSON file for each document
    chunks_json_filename = output_dir / f"{doc_filename}_chunks.json"
    with chunks_json_filename.open("w") as json_fp:
        json.dump(chunk_data, json_fp, indent=4)
    _log.info(f"Chunks saved to JSON file: {chunks_json_filename}")

    # Export markdown with embedded images for content
    content_md = conv_res.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    with md_filename.open("w") as fp:
        fp.write(content_md)
    _log.info(f"Markdown with images saved: {md_filename}")

    end_time = time.time() - start_time
    _log.info(f"{doc_filename} converted and figures exported in {end_time:.2f} seconds.")

# Process each file in the list
for file_path in file_paths:
    process_pdf(file_path)
