import gradio as gr
from PIL import Image, ImageDraw, ImageFont
import os
import json
import subprocess
import platform
import requests
import re
import pyperclip
# Assuming these are in a local file as per your original code
from font_generator import download_google_font, create_character_image, char_name_map, generate_character_mapping

def open_folder(path):
    """Open the output folder based on the operating system"""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux
        subprocess.run(["xdg-open", path])
    return "Opened folder: " + path

def read_mapping_file():
    """Read and return the contents of the character mapping file"""
    try:
        with open('../character_mapping.txt', 'r') as f:
            return f.read()
    except:
        return "Character mapping will appear here after generation"

def validate_font_name(input_text):
    """
    Validates font name or extracts it from Google Fonts URL.
    Returns (is_valid, font_name, message)
    """
    # Clean up input
    input_text = input_text.strip()
    
    # Check if it's a URL
    url_match = re.search(r'fonts\.google\.com/specimen/([^/?&#]+)', input_text)
    if url_match:
        # Extract font name from URL and replace '+' with spaces
        font_name = url_match.group(1).replace('+', ' ')
    else:
        font_name = input_text

    # Check if font exists on Google Fonts
    api_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/css,*/*;q=0.1',
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        return True, font_name, f"✓ Font '{font_name}' is valid"
    else:
        return False, "", f"✗ Font '{font_name}' not found on Google Fonts"

def check_font(input_text):
    """Gradio wrapper for font validation"""
    if not input_text:
        return "", ""
    is_valid, font_name, message = validate_font_name(input_text)
    return message, font_name if is_valid else input_text

# MODIFIED: A corrected version of the function to fix the error

def generate_font_images(font_name, local_font, font_size, image_size, output_folder, characters):
    font_path = None
    validated_font_name = "local_font"
    is_temp_font = False # Flag to check if we need to delete the font file later

    # Logic to prioritize local font file over Google Font name
    if local_font is not None:
        font_path = local_font.name
        validated_font_name = os.path.splitext(os.path.basename(font_path))[0]
    elif font_name:
        is_valid, validated_font_name, message = validate_font_name(font_name)
        if not is_valid:
            return [], message, "Font validation failed"
        font_path = download_google_font(validated_font_name)
        is_temp_font = True
    else:
        return [], "Please provide a font by name or by uploading a file.", "No font specified"

    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Convert sizes to integers, just in case
        font_size_int = int(font_size)
        image_size_int = int(image_size)

        font = ImageFont.truetype(font_path, font_size_int)

        generated_images = []
        for char in characters:
            if char.isalpha():
                # FIX: Pass 'image_size_int' directly, not a tuple
                create_character_image(char.lower(), font, image_size_int, output_folder, 'L_')
                create_character_image(char.upper(), font, image_size_int, output_folder, 'U_')

                # Load and append the generated images for preview
                lower_char_name = char_name_map.get(char.lower(), char.lower())
                upper_char_name = char_name_map.get(char.upper(), char.upper())

                lower_path = os.path.join(output_folder, f"custom_font_L_{lower_char_name}.png")

                upper_path = os.path.join(output_folder, f"custom_font_U_{upper_char_name}.png")
            
                paths_to_add = set()
                if os.path.exists(lower_path): paths_to_add.add(lower_path)
                if os.path.exists(upper_path): paths_to_add.add(upper_path)
            else:
                # FIX: Pass 'image_size_int' directly, not a tuple
                create_character_image(char, font, image_size_int, output_folder, 'S_')
                
                # Load and append the generated images for preview
                symbol_char_name = char_name_map.get(char, char)

                symbol_path = os.path.join(output_folder, f"custom_font_S_{symbol_char_name}.png")
            
                paths_to_add = set()
                if os.path.exists(symbol_path): paths_to_add.add(symbol_path)
            for path in paths_to_add:
                generated_images.append(Image.open(path))

        if is_temp_font and font_path:
            try:
                os.unlink(font_path)
            except OSError as e:
                print(f"Note: Could not delete temp font file: {e}")

        generate_character_mapping(characters, output_folder)
        mapping_content = read_mapping_file()
        
        return generated_images, f"Success! Generated images for '{validated_font_name}'.", mapping_content
    except Exception as e:
        return None, f"Error: {str(e)}", "Error generating character mapping"

def copy_to_clipboard(text):
    """Copy text to clipboard and return status"""
    pyperclip.copy(text)
    return "✓ Mapping copied to clipboard!"

# Create the Gradio interface
with gr.Blocks(title="Font to Images Generator") as iface:
    gr.Markdown("""
    # Font to Images Generator
    Enter a Google Font name OR upload a local font file.
    """)
    
    with gr.Row():
        # Left Column - Input Controls
        with gr.Column():
            with gr.Group():
                gr.Markdown("### 1. Choose Font")
                font_name = gr.Textbox(
                    label="Google Font Name or URL", 
                    value="Roboto",
                    placeholder="e.g., 'Roboto' or a Google Fonts URL"
                )
                with gr.Row():
                    check_btn = gr.Button("Check Font", size="sm", variant="secondary")
                    font_status = gr.Textbox(
                        label="Status", interactive=False, show_label=False, container=False
                    )
                
                gr.Markdown("<p style='text-align: center; margin: 5px;'>OR</p>")
                
                # NEW: File uploader for local fonts
                local_font_upload = gr.File(
                    label="Upload Local Font (.ttf, .otf)",
                    file_types=[".ttf", ".otf"]
                )

            with gr.Group():
                gr.Markdown("### 2. Settings")
                with gr.Row():
                    font_size = gr.Number(label="Font Size", value=64, container=True)
                    image_size = gr.Number(label="Image Size", value=128, container=True)
                output_folder = gr.Textbox(label="Output Folder", value="output")
                characters = gr.Textbox(
                    label="Characters", 
                    value="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/\\ ",
                    lines=3
                )
            
            with gr.Row():
                generate_btn = gr.Button("3. Generate Images", variant="primary")
                open_folder_btn = gr.Button("Open Output Folder", variant="secondary")
        
        # Right Column - Output Display
        with gr.Column():
            with gr.Group():
                gr.Markdown("### Preview")
                gallery = gr.Gallery(label="Generated Images", show_label=False, columns=8, height="auto")
                status = gr.Textbox(label="Status", show_label=False, interactive=False)
            
            with gr.Group():
                gr.Markdown("### Character Mapping")
                with gr.Row():
                    mapping = gr.Textbox(
                        label="Generated Mapping", value=read_mapping_file(), lines=10, max_lines=10, show_label=False
                    )
                    copy_btn = gr.Button("📋 Copy", size="sm")
                copy_status = gr.Textbox(
                    label="Copy Status", show_label=False, container=False, interactive=False
                )
    
    # Event handlers
    check_btn.click(fn=check_font, inputs=[font_name], outputs=[font_status, font_name])
    
    # MODIFIED: Add 'local_font_upload' to the inputs list
    generate_btn.click(
        fn=generate_font_images,
        inputs=[font_name, local_font_upload, font_size, image_size, output_folder, characters],
        outputs=[gallery, status, mapping]
    )
    
    open_folder_btn.click(fn=open_folder, inputs=[output_folder], outputs=[status])
    copy_btn.click(fn=copy_to_clipboard, inputs=[mapping], outputs=[copy_status])

if __name__ == "__main__":
    iface.launch()