import streamlit as st
import pydicom
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from io import BytesIO

st.title("DICOM Viewer and Downloader")

uploaded_file = st.file_uploader("Upload a DICOM file", type=["dcm"])

if uploaded_file:
    dicom_data = pydicom.dcmread(uploaded_file)

    # Normalize image to 0–255 for display
    pixel_array = dicom_data.pixel_array.astype(np.float32)
    pixel_array -= pixel_array.min()
    pixel_array /= pixel_array.max()
    pixel_array *= 255.0
    pixel_array = pixel_array.astype(np.uint8)

    # Display the image
    st.image(pixel_array, caption="DICOM Image", use_container_width=True)

    # Show metadata
    metadata = {elem.keyword: str(elem.value) for elem in dicom_data if elem.keyword}
    df = pd.DataFrame(list(metadata.items()), columns=["Attribute", "Value"])
    st.dataframe(df)

    # Download as CSV
    csv = df.to_csv(index=False).encode()
    st.download_button("Download Metadata as CSV", csv, file_name="dicom_metadata.csv")

    # Download as PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 800, "DICOM Metadata Summary")
    y = 780
    for i, (k, v) in enumerate(metadata.items()):
        pdf.drawString(50, y, f"{k}: {v}")
        y -= 15
        if y < 50:
            pdf.showPage()
            y = 800
    pdf.save()
    buffer.seek(0)
    st.download_button("Download Metadata as PDF", buffer, file_name="dicom_metadata.pdf")
