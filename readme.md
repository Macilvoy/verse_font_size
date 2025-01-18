# Custom Verse Text Widget

A custom verse UI widget that gives you more control over the appearance of texts in your UEFN UIs.

## Features
- Acts like a normal text widget, meaning that all the already existing functions that can be called on a normal text widget can be called on this widget as well!
- Adjustable font size, color, character spacing, and more!
- Comes with a python tool to help convert Google Fonts into images that can be used for this widget.

## Font Generator Tool

Comes with a Python tool that converts Google Fonts into individual character images so they can be used for custom UI text widgets in UEFN/Verse.

## Features

- Supports any font from Google Fonts (maybe any)
- Generate individual PNG images for each character
- Support for uppercase, lowercase, numbers, and special characters
- Consistent character sizing and alignment
- Transparent backgrounds
- Automatic verse character mapping generation
- Simple user-friendly GUI interface

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/imcouri/verse_font_size.git
cd verse_font_size
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Method

1. Run the main file to start up the Gradio interface:
```bash
python main.py
```

2. Open your web browser and navigate to the displayed local URL (usually http://127.0.0.1:7860)

3. Enter a Google Font name or URL (e.g., "Roboto" or "https://fonts.google.com/specimen/Roboto")

4. Adjust settings if needed:
   - Font Size (default: 64)
   - Image Size (default: 128)
   - Output Folder
   - Characters to generate

5. Click "Generate Images" to create the character images

### Command Line Method

1. Configure your settings in `config.json`:
```json
{
    "font_name": "Roboto",
    "font_size": 64,
    "image_size": 128,
    "output_folder": "output",
    "characters": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/\\ "
}
```

2. Run the generator:
```bash
python font_generator.py
```

## Output

The generator creates:
- Individual PNG images for each character in the specified output folder
- A character mapping file (`character_mapping.txt`)  which is a verse wrapper function that maps characters to specific images

Images are named using the format:
- Uppercase: `custom_font_U_[char].png`
- Lowercase: `custom_font_L_[char].png`
- Special characters use descriptive names (e.g., `custom_font_L_exclamation.png`)
- *NOTE : Using custom characters that are not included in this tool by default may cause naming issues inside UEFN or even the auto generated wrapper function.

## Configuration

You can modify the following settings:
- `font_name`: Name of the Google Font to use
- `font_size`: Base font size for generation
- `image_size`: Size of the output images (width and height)
- `output_folder`: Where to save the generated images
- `characters`: String of characters to generate

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

