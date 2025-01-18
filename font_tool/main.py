import gradio as gr
from PIL import Image, ImageDraw, ImageFont
import os
import json
import subprocess
import platform
import requests
import re
import pyperclip
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
    is_valid, font_name, message = validate_font_name(input_text)
    return message, font_name if is_valid else input_text

def generate_font_images(font_name, font_size, image_size, output_folder, characters):
    # Validate font first
    is_valid, validated_font_name, message = validate_font_name(font_name)
    if not is_valid:
        return None, message, "Font validation failed"

    try:
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Download and load the Google Font
        font_path = download_google_font(validated_font_name)
        font = ImageFont.truetype(font_path, font_size)

        generated_images = []
        # Generate images for each character in both cases
        for char in characters:
            # Generate lowercase
            create_character_image(
                char.lower(),
                font,
                image_size,
                output_folder,
                'L_'
            )
            
            # Generate uppercase
            create_character_image(
                char.upper(),
                font,
                image_size,
                output_folder,
                'U_'
            )

            # Load and append the generated images for preview
            lower_char_name = char_name_map.get(char.lower(), char.lower())
            upper_char_name = char_name_map.get(char.upper(), char.upper())
            
            lower_path = os.path.join(output_folder, f"custom_font_L_{lower_char_name}.png")
            upper_path = os.path.join(output_folder, f"custom_font_U_{upper_char_name}.png")
            
            if os.path.exists(lower_path):
                generated_images.append(Image.open(lower_path))
            if os.path.exists(upper_path):
                generated_images.append(Image.open(upper_path))

        # Clean up the temporary font file
        try:
            os.unlink(font_path)
        except:
            pass

        # Generate the mapping file
        generate_character_mapping(characters, output_folder)
        
        # Read the mapping file
        mapping_content = read_mapping_file()
        
        return generated_images, "Font images generated successfully!", mapping_content
    except Exception as e:
        return None, f"Error: {str(e)}", "Error generating character mapping"

def copy_to_clipboard(text):
    """Copy text to clipboard and return status"""
    pyperclip.copy(text)
    return "✓ Mapping copied to clipboard!"

# Create the Gradio interface
with gr.Blocks(title="Google Font to Images Generator") as iface:
    gr.Markdown("""
    # Google Font to Images Generator
    
    ### Instructions:
    1. Enter a Google Font name OR paste a Google Fonts URL (e.g., https://fonts.google.com/specimen/Roboto)
    2. Click "Check Font" to validate the font name
    3. Adjust font size and image size if needed
    4. Specify an output folder name
    5. Click "Generate Images" to create the font images
    6. Use "Open Output Folder" to view the generated files
    7. Copy the character mapping to clipboard using "📋 Copy"
    8. Put the folder with images in your UEFN project's content folder
    9. Paste the character mappings copied at the bottom of the code (look for "CHARACTER MAPPING" in the code)
    
    ### Notes:
    - Font names are case-sensitive
    - You can paste the full Google Fonts URL instead of the font name
    - The character mapping will be generated automatically
    - Images are generated with transparent backgrounds
    - You may need to adjust specific images manually
    """)
    
    with gr.Row():
        # Left Column - Input Controls
        with gr.Column():
            # Font Selection Section
            with gr.Group():
                gr.Markdown("### Font Selection")
                font_name = gr.Textbox(
                    label="Font Name or Google Fonts URL", 
                    value="Roboto",
                    placeholder="Enter font name or paste Google Fonts URL"
                )
                with gr.Row():
                    check_btn = gr.Button("Check Font", size="sm", variant="secondary")
                    font_status = gr.Textbox(
                        label="Status", 
                        interactive=False,
                        show_label=False,
                        container=False
                    )
            
            # Settings Section
            with gr.Group():
                gr.Markdown("### Settings")
                with gr.Row():
                    font_size = gr.Number(label="Font Size", value=64, container=True)
                    image_size = gr.Number(label="Image Size", value=128, container=True)
                output_folder = gr.Textbox(label="Output Folder", value="output")
                characters = gr.Textbox(
                    label="Characters", 
                    value="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/\\ ",
                    lines=3
                )
            
            # Action Buttons
            with gr.Row():
                generate_btn = gr.Button("Generate Images", variant="primary")
                open_folder_btn = gr.Button("Open Output Folder", variant="secondary")
        
        # Right Column - Output Display
        with gr.Column():
            # Preview Section
            with gr.Group():
                gr.Markdown("### Preview")
                gallery = gr.Gallery(label="Generated Images", show_label=False)
                status = gr.Textbox(label="Status", show_label=False)
            
            # Mapping Section
            with gr.Group():
                gr.Markdown("### Character Mapping")
                with gr.Row():
                    mapping = gr.Textbox(
                        label="Generated Mapping", 
                        value=read_mapping_file(),
                        lines=10,
                        max_lines=10,
                        show_label=False
                    )
                    copy_btn = gr.Button("📋 Copy", size="sm")
                copy_status = gr.Textbox(
                    label="Copy Status",
                    show_label=False,
                    container=False
                )
    
    # Event handlers
    check_btn.click(
        fn=check_font,
        inputs=[font_name],
        outputs=[font_status, font_name]
    )
    
    generate_btn.click(
        fn=generate_font_images,
        inputs=[font_name, font_size, image_size, output_folder, characters],
        outputs=[gallery, status, mapping]
    )
    
    open_folder_btn.click(
        fn=open_folder,
        inputs=[output_folder],
        outputs=[status]
    )
    
    copy_btn.click(
        fn=copy_to_clipboard,
        inputs=[mapping],
        outputs=[copy_status]
    )

if __name__ == "__main__":
    iface.launch()