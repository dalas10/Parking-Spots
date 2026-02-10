from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple parking icon
def create_icon(size, filename):
    # Create a green background
    img = Image.new('RGB', (size, size), color='#4CAF50')
    draw = ImageDraw.Draw(img)
    
    # Draw a white "P" 
    try:
        # Try to use a system font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.6))
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw P in center
    text = "P"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2 - int(size * 0.05))
    draw.text(position, text, fill='white', font=font)
    
    # Draw a small circle below P
    circle_radius = size // 15
    circle_y = size - (size // 4)
    draw.ellipse(
        [size//2 - circle_radius, circle_y - circle_radius,
         size//2 + circle_radius, circle_y + circle_radius],
        fill='white'
    )
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

# Create icons
create_icon(192, 'icon-192.png')
create_icon(512, 'icon-512.png')

print("\n✅ Icons created successfully!")
print("Icons are located in the current directory.")
