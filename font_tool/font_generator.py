from PIL import Image, ImageDraw, ImageFont
import os
import json
import requests
import tempfile


# Character name mapping for special characters
char_name_map = {
    '!': 'exclamation',
    '@': 'at',
    '#': 'hash',
    '$': 'dollar',
    '%': 'percent',
    '^': 'caret',
    '&': 'ampersand',
    '*': 'asterisk',    
    '(': 'lparen',
    ')': 'rparen',
    '-': 'hyphen',
    '_': 'underscore',
    '+': 'plus',
    '=': 'equals',
    '[': 'lbracket',
    ']': 'rbracket',
    '{': 'lcurly',
    '}': 'rcurly',
    '|': 'pipe',
    '\\': 'backslash',
    ';': 'semicolon',
    ':': 'colon',
    "'": 'quote',
    '"': 'dblquote',
    ',': 'comma',
    '.': 'period',
    '/': 'slash',
    '?': 'question',
    '<': 'lt',
    '>': 'gt',
    '~': 'tilde',
    '`': 'backtick',
    ' ': 'space'
}

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)


def download_google_font(font_family):
    """Download a font from Google Fonts API"""
    # Format font family name for URL (replace spaces with plus signs)
    formatted_font_name = font_family.replace(' ', '+')
    
    # Get the font information from Google Fonts API
    api_url = f"https://fonts.googleapis.com/css2?family={formatted_font_name}:wght@400&display=swap"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/css,*/*;q=0.1',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://fonts.googleapis.com/',
    }
    
    print(f"\nRequesting font: {font_family}")
    print(f"URL: {api_url}")
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch font information: {response.status_code}")
    
    # Extract the font URL from the CSS
    css_content = response.text
    print("\nCSS Response:")
    print(css_content)
    
    # First try to find the basic latin version
    font_url = None
    for line in css_content.split('\n'):
        if '.woff2' in line and 'url' in line and '/* latin */' in css_content[:css_content.find(line)]:
            start = line.find('url(') + 4
            end = line.find(')', start)
            font_url = line[start:end]
            if font_url.startswith("'") or font_url.startswith('"'):
                font_url = font_url[1:-1]
            break
    
    # If no latin version found, use the first available font URL
    if not font_url:
        for line in css_content.split('\n'):
            if '.woff2' in line and 'url' in line:
                start = line.find('url(') + 4
                end = line.find(')', start)
                font_url = line[start:end]
                if font_url.startswith("'") or font_url.startswith('"'):
                    font_url = font_url[1:-1]
                break
    
    if not font_url:
        raise Exception("Could not find font URL in CSS")
    
    print(f"\nFont URL: {font_url}")
    
    # Download the font file
    font_response = requests.get(font_url, headers=headers)
    if font_response.status_code != 200:
        raise Exception(f"Failed to download font: {font_response.status_code}")
    
    # Save to a temporary file
    temp_font_file = tempfile.NamedTemporaryFile(delete=False, suffix='.woff2')
    temp_font_file.write(font_response.content)
    temp_font_file.close()
    
    print(f"\nDownloaded WOFF2 file size: {os.path.getsize(temp_font_file.name)} bytes")
    
    # Convert WOFF2 to TTF using fontTools
    from fontTools.ttLib import TTFont
    
    try:
        # Load the WOFF2 font
        font = TTFont(temp_font_file.name)
        
        # Save as TTF
        ttf_path = temp_font_file.name[:-6] + '.ttf'  # Remove .woff2 and add .ttf
        font.save(ttf_path)
        
        print(f"Converted to TTF: {ttf_path}")
        print(f"TTF file size: {os.path.getsize(ttf_path)} bytes")
        
        # Test the font
        test_font = ImageFont.truetype(ttf_path, 64)
        # Get font info
        print("\nFont information:")
        print(f"Font family: {test_font.getname()}")
        print(f"Font size: {test_font.size}")
        
        # Test metrics
        test_char = "A"
        bbox = test_font.getbbox(test_char)
        print(f"\nBounding box for '{test_char}': {bbox}")
        
        # Create test image
        test_size = 128
        test_img = Image.new('RGB', (test_size, test_size), color='black')
        test_draw = ImageDraw.Draw(test_img)
        
        # Get test character dimensions
        test_bbox = test_draw.textbbox((0, 0), test_char, font=test_font)
        test_width = test_bbox[2] - test_bbox[0]
        test_height = test_bbox[3] - test_bbox[1]
        
        # Center the test character
        test_x = (test_size - test_width) // 2
        test_y = (test_size - test_height) // 2
        
        # Draw test character
        test_draw.text((test_x, test_y), test_char, font=test_font, fill='white')
        print(f"Test character dimensions: {test_width}x{test_height}")
        print(f"Test character position: ({test_x}, {test_y})")
        
        # Save test image for inspection
        test_img.save('font_test.png')
        print("Saved test image as 'font_test.png'")
        
    except Exception as e:
        print(f"\nError during font processing: {str(e)}")
        raise e
    finally:
        # Clean up the WOFF2 file
        try:
            os.unlink(temp_font_file.name)
        except:
            pass
    
    return ttf_path


def create_character_image(char, font, image_size, output_folder, case_prefix=''):
    # Special case for space character
    if char == ' ':
        actual_width = image_size
        image = Image.new('RGBA', (actual_width, image_size), (0, 0, 0, 0))
        filename = f"custom_font_S_space"
        image.save(os.path.join(output_folder, f"{filename}.png"))
        return

    print(f"\nGenerating image for character: '{char}'")
    
    # Get font metrics for proper sizing
    ascent, descent = font.getmetrics()
    total_height = ascent + abs(descent)
    
    # Create a temporary image for measurements
    temp_image = Image.new('RGBA', (image_size * 2, image_size * 2), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_image)
    
    # Determine target height based on character type
    if char.isupper() and char.isalpha():
        target_height = image_size * 0.7  # 70% of image height
        font_scale = 0.7  # Scale down uppercase
    elif char in 'gjpqy':
        target_height = image_size * 0.5  # Same as lowercase, but will extend below
        font_scale = 1.0
    else:
        target_height = image_size * 0.5  # 50% of image height
        font_scale = 1.0
    
    # Calculate scale factor based on em height
    em_scale = target_height / font.size
    
    # Create scaled font
    scaled_font_size = int(font.size * em_scale * font_scale)
    scaled_font = ImageFont.truetype(font.path, scaled_font_size)
    
    # All characters will have the same width as image_size
    actual_width = image_size
    
    # Create the final image
    image = Image.new('RGBA', (actual_width, image_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Get the complete bounding box including any offset
    test_bbox = draw.textbbox((0, 0), char, font=scaled_font)
    char_width = test_bbox[2] - test_bbox[0]
    left_offset = test_bbox[0]
    
    # Calculate horizontal position to center the character
    x = (actual_width - char_width) // 2 - left_offset
    
    # Calculate baseline position (20% from bottom to leave room for descenders)
    baseline_y = int(image_size * 0.8)
    
    # Calculate vertical position relative to baseline
    if char.isupper() and char.isalpha():
        # For uppercase, scale the vertical position by the same factor as the font
        y = baseline_y - int(ascent * em_scale * font_scale)
    elif char in 'gjpqy':
        y = baseline_y - int(ascent * em_scale)
    else:
        y = baseline_y - int(ascent * em_scale)
    
    print(f"Character: {char}")
    print(f"Scale factor: {em_scale:.2f}")
    print(f"Final dimensions - Width: {actual_width}, Height: {image_size}")
    print(f"Position - X: {x}, Y: {y}")
    
    # Draw the character
    draw.text((x, y), char, fill='white', font=scaled_font)
    
    # Get character name and save
    char_name = char_name_map.get(char, char)
    filename = f"custom_font_{case_prefix}{char_name}"
    filename = "".join(c if c.isalnum() else "_" for c in filename)
    image.save(os.path.join(output_folder, f"{filename}.png"))


def generate_character_mapping(characters, output_folder):
    """Generate character mapping in the custom format"""
    mapping = "(InChar : char).ToImage():texture=\n    case(InChar):\n"
    
    for char in characters:
        if char.isalpha():
            # Get character names using the existing char_name_map from create_character_image
            lower_char_name = char_name_map.get(char.lower(), char.lower())
            upper_char_name = char_name_map.get(char.upper(), char.upper())


            # Lowercase mapping
            mapping += f"        '{char.lower()}' => {output_folder}.custom_font_L_{lower_char_name}\n"
            # Uppercase mapping
            mapping += f"        '{char.upper()}' => {output_folder}.custom_font_U_{upper_char_name}\n"
        else:
            symbol_char_name = char_name_map.get(char, char)
            mapping += f"        '{char}' => {output_folder}.custom_font_S_{symbol_char_name}\n"
    


    mapping += f"        _ => {output_folder}.custom_font_S_space\n"
    # Write the mapping to a file
    with open('../character_mapping.txt', 'w') as f:
        f.write(mapping)


def main():
    # Load configuration
    config = load_config()

    # Create output folder if it doesn't exist
    if not os.path.exists(config['output_folder']):
        os.makedirs(config['output_folder'])

    try:
        # Download and load the Google Font
        font_path = download_google_font(config['font_name'])
        font = ImageFont.truetype(font_path, config['font_size'])
    except Exception as e:
        print(f"Error loading font: {e}")
        print("Using default font instead.")
        font = ImageFont.load_default()

    # Generate images for each character in both cases
    for char in config['characters']:
        if char.isalpha():
            # Generate lowercase
            create_character_image(
                char.lower(),
                font,
                config['image_size'],
                config['output_folder'],
                'L_'
            )
            print(f"Generated image for character: {char.lower()}")

            # Generate uppercase
            create_character_image(
                char.upper(),
                font,
                config['image_size'],
                config['output_folder'],
                'U_'
            )
            print(f"Generated image for character: {char.upper()}")

        else:
            create_character_image(
                char,
                font,
                config['image_size'],
                config['output_folder'],
                'S_'
            )
            print(f"Generated image for character: {char}")

    # Clean up the temporary font file
    if 'font_path' in locals():
        try:
            os.unlink(font_path)
        except:
            pass

    # After generating all images, create the mapping
    generate_character_mapping(config['characters'], config['output_folder'])


if __name__ == "__main__":
    main()
