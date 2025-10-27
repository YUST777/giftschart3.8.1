import os
import colorsys
from PIL import Image, ImageDraw
import numpy as np
from main import names

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Directory paths - use os.path.join for cross-platform compatibility
input_dir = os.path.join(script_dir, "downloaded_images")
backgrounds_dir = os.path.join(script_dir, "pregenerated_backgrounds")
assets_dir = os.path.join(script_dir, "assets")
background_template_path = os.path.join(assets_dir, "Background color this.png")

# Create output directory if it doesn't exist
os.makedirs(backgrounds_dir, exist_ok=True)

# Function to get dominant color from an image
def get_dominant_color(image_path):
    try:
        img = Image.open(image_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create a smaller version of the image to speed up processing
        img.thumbnail((100, 100))
        
        # Get color data
        pixels = np.array(img)
        
        # Remove transparent pixels (alpha < 128)
        pixels = pixels[pixels[:,:,3] > 128]
        
        if len(pixels) == 0:
            return (128, 128, 128)  # Default to gray if all pixels are transparent
        
        # Remove alpha channel for clustering
        pixels = pixels[:,:3]
        
        # Simple average color (mean of all non-transparent pixels)
        avg_color = pixels.mean(axis=0).astype(int)
        
        # Enhance saturation a bit for better visual appeal
        h, s, v = colorsys.rgb_to_hsv(avg_color[0]/255, avg_color[1]/255, avg_color[2]/255)
        s = min(s * 1.5, 1.0)  # Increase saturation by 50%, but not above 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        
        return (int(r*255), int(g*255), int(b*255))
    except Exception as e:
        print(f"Error getting dominant color from {image_path}: {e}")
        return (128, 128, 128)  # Default to gray on error

# Function to create a gradient background
def create_gradient_background(background_img, color):
    try:
        # Create a gradient background instead of solid color
        width, height = background_img.size
        
        # Create a new image with the same size and mode
        gradient_bg = Image.new('RGBA', background_img.size, (0, 0, 0, 0))
        
        # Extract the base color components
        r, g, b = color
        
        # Create a darker shade for the edges
        darker_r = max(0, int(r * 0.65))
        darker_g = max(0, int(g * 0.65))
        darker_b = max(0, int(b * 0.65))
        darker_color = (darker_r, darker_g, darker_b, 255)
        
        # Create a lighter shade for the center
        lighter_r = min(255, int(r * 1.15))
        lighter_g = min(255, int(g * 1.15))
        lighter_b = min(255, int(b * 1.15))
        lighter_color = (lighter_r, lighter_g, lighter_b, 255)
        
        # Create a slightly different hue for added depth
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = (h + 0.05) % 1.0  # Shift hue slightly
        s = min(1.0, s * 1.2)  # Increase saturation
        accent_r, accent_g, accent_b = colorsys.hsv_to_rgb(h, s, v)
        accent_color = (int(accent_r*255), int(accent_g*255), int(accent_b*255), 255)
        
        # Create a radial gradient using a more efficient method
        # First create a small gradient image and then resize it
        small_size = (200, 200)  # Increased for smoother gradient
        small_gradient = Image.new('RGBA', small_size, (0, 0, 0, 0))
        small_draw = ImageDraw.Draw(small_gradient)
        
        # Draw concentric circles with decreasing radius
        center = (small_size[0] // 2, small_size[1] // 2)
        max_radius = int(((small_size[0] // 2) ** 2 + (small_size[1] // 2) ** 2) ** 0.5)
        
        # Draw from outside in with more gradual transitions
        num_steps = 40  # More steps for smoother gradient
        for i in range(num_steps):
            # Calculate radius for this step
            radius = max_radius * (1 - (i / num_steps))
            
            # Calculate interpolation factor (0 at edge, 1 at center)
            factor = i / num_steps
            
            # Create multi-point gradient with darker outer edges and lighter center
            if factor < 0.25:  # Outer 25% transitions from darker to base
                t = factor / 0.25
                r_val = int(darker_color[0] * (1-t) + color[0] * t)
                g_val = int(darker_color[1] * (1-t) + color[1] * t)
                b_val = int(darker_color[2] * (1-t) + color[2] * t)
            elif factor < 0.5:  # Next 25% transitions from base to accent
                t = (factor - 0.25) / 0.25
                r_val = int(color[0] * (1-t) + accent_color[0] * t)
                g_val = int(color[1] * (1-t) + accent_color[1] * t)
                b_val = int(color[2] * (1-t) + accent_color[2] * t)
            else:  # Inner 50% transitions from accent to lighter
                t = (factor - 0.5) / 0.5
                r_val = int(accent_color[0] * (1-t) + lighter_color[0] * t)
                g_val = int(accent_color[1] * (1-t) + lighter_color[1] * t)
                b_val = int(accent_color[2] * (1-t) + lighter_color[2] * t)
            
            current_color = (r_val, g_val, b_val, 255)
            
            # Draw a filled circle
            bbox = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
            small_draw.ellipse(bbox, fill=current_color)
        
        # Resize the small gradient to the full size
        gradient_bg = small_gradient.resize(background_img.size, Image.BICUBIC)
        
        # Use the original background's alpha channel as a mask
        if background_img.mode == 'RGBA':
            r, g, b, a = background_img.split()
            gradient_bg.putalpha(a)
            
        return gradient_bg
    except Exception as e:
        print(f"Error creating gradient background: {e}")
        return background_img  # Return original background on error

def main():
    print("Pre-generating gradient backgrounds for all gifts...")
    
    # Check if template background exists
    if not os.path.exists(background_template_path):
        print(f"Error: Background template not found at {background_template_path}")
        return
    
    # Load background template
    background_img = Image.open(background_template_path).convert("RGBA")
    
    # Make sure the image is the target size
    target_size = (1600, 1000)
    background_img = background_img.resize(target_size)
    
    # Process each gift
    for gift_name in names:
        print(f"Processing {gift_name}...")
        
        # Normalize gift name for file matching
        safe_name = gift_name.replace(' ', '_').replace('-', '_').replace("'", '')
        
        # Find the gift image file
        gift_file = None
        for filename in os.listdir(input_dir):
            if filename.lower().startswith(safe_name.lower()) and (filename.lower().endswith(".png") or filename.lower().endswith(".jpg")):
                gift_file = filename
                break
        
        if not gift_file:
            print(f"Error: Image file for {gift_name} not found, skipping...")
            continue
        
        # Get the gift image path
        gift_path = os.path.join(input_dir, gift_file)
        
        # Get the dominant color
        dominant_color = get_dominant_color(gift_path)
        
        # Create the gradient background
        gradient_bg = create_gradient_background(background_img, dominant_color)
        
        # Save the background
        output_path = os.path.join(backgrounds_dir, f"{safe_name}_background.png")
        gradient_bg.save(output_path)
        print(f"Saved background to {output_path}")
    
    print("Done pre-generating all backgrounds!")

if __name__ == "__main__":
    main() 