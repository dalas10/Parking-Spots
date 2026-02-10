# ParkingSpots Brand Guidelines

**Version**: 1.0  
**Date**: February 10, 2026  
**Logo**: urbee.jpg

---

## Brand Identity

### Logo

**Primary Logo**: `urbee.jpg`  
**Dimensions**: 543 x 554 pixels  
**Format**: JPEG  
**File Locations**:
- Main: `/urbee.jpg`
- Web: `/web/assets/logo.jpg`
- Mobile: `/mobile/assets/logo.jpg`
- Backend: `/backend/app/static/logo.jpg`

### Usage Guidelines

**Clear Space**: Minimum 20px padding around logo  
**Minimum Size**: 64px width for digital, 1 inch for print  
**Background**: Works best on white or dark backgrounds

---

## Color Palette

### Primary Colors

#### Brand Orange (Primary)
```
Name: Urbee Gold
HEX: #fdb82e
RGB: 253, 186, 46
CMYK: 0%, 27%, 82%, 1%
Usage: Primary brand color, CTAs, highlights
```

#### Golden Orange (Accent 1)
```
Name: Golden Hour
HEX: #fdba2e
RGB: 253, 186, 46
CMYK: 0%, 27%, 82%, 1%
Usage: Hover states, secondary buttons
```

#### Vibrant Orange (Accent 2)
```
Name: Sunset Orange
HEX: #fe9f1d
RGB: 254, 159, 29
CMYK: 0%, 37%, 89%, 0%
Usage: Active states, notifications, alerts
```

#### Light Orange (Accent 3)
```
Name: Morning Glow
HEX: #fec538
RGB: 254, 197, 56
CMYK: 0%, 22%, 78%, 0%
Usage: Backgrounds, subtle highlights
```

### Secondary Colors

#### Dark Gray (Text)
```
HEX: #2c3e50
RGB: 44, 62, 80
Usage: Primary text, headings
```

#### Medium Gray (Secondary Text)
```
HEX: #7f8c8d
RGB: 127, 140, 141
Usage: Secondary text, captions
```

#### Light Gray (Background)
```
HEX: #ecf0f1
RGB: 236, 240, 241
Usage: Background, cards, containers
```

### Semantic Colors

#### Success Green
```
HEX: #27ae60
RGB: 39, 174, 96
Usage: Success messages, confirmed bookings
```

#### Error Red
```
HEX: #e74c3c
RGB: 231, 76, 60
Usage: Error messages, cancellations
```

#### Warning Yellow
```
HEX: #f39c12
RGB: 243, 156, 18
Usage: Warnings, pending actions
```

#### Info Blue
```
HEX: #3498db
RGB: 52, 152, 219
Usage: Info messages, links
```

---

## Color Usage Examples

### Web Interface

```css
/* CSS Variables */
:root {
  /* Primary Brand Colors */
  --primary-color: #fdb82e;
  --primary-hover: #fdba2e;
  --primary-active: #fe9f1d;
  --primary-light: #fec538;
  
  /* Text Colors */
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  --text-light: #95a5a6;
  
  /* Background Colors */
  --bg-primary: #ffffff;
  --bg-secondary: #ecf0f1;
  --bg-dark: #2c3e50;
  
  /* Semantic Colors */
  --success: #27ae60;
  --error: #e74c3c;
  --warning: #f39c12;
  --info: #3498db;
}

/* Button Styles */
.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:active {
  background-color: var(--primary-active);
}
```

### Mobile App (React Native)

```javascript
// colors.ts
export const Colors = {
  // Primary Brand
  primary: '#fdb82e',
  primaryHover: '#fdba2e',
  primaryActive: '#fe9f1d',
  primaryLight: '#fec538',
  
  // Text
  textPrimary: '#2c3e50',
  textSecondary: '#7f8c8d',
  textLight: '#95a5a6',
  
  // Background
  bgPrimary: '#ffffff',
  bgSecondary: '#ecf0f1',
  bgDark: '#2c3e50',
  
  // Semantic
  success: '#27ae60',
  error: '#e74c3c',
  warning: '#f39c12',
  info: '#3498db',
};
```

### API/Backend

```python
# app/core/branding.py
BRAND_COLORS = {
    "primary": "#fdb82e",
    "primary_hover": "#fdba2e",
    "primary_active": "#fe9f1d",
    "primary_light": "#fec538",
    "success": "#27ae60",
    "error": "#e74c3c",
    "warning": "#f39c12",
    "info": "#3498db",
}

LOGO_URL = "/static/logo.jpg"
```

---

## Typography

### Font Families

**Primary Font**: Inter, SF Pro, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
**Monospace Font**: "SF Mono", Monaco, "Courier New", monospace

### Font Weights

- **Light**: 300 (rarely used)
- **Regular**: 400 (body text)
- **Medium**: 500 (subheadings, buttons)
- **Semibold**: 600 (headings)
- **Bold**: 700 (emphasis, important headings)

### Font Sizes

```
Heading 1: 2.5rem (40px) - Bold
Heading 2: 2rem (32px) - Semibold
Heading 3: 1.5rem (24px) - Semibold
Heading 4: 1.25rem (20px) - Medium
Body Large: 1.125rem (18px) - Regular
Body: 1rem (16px) - Regular
Body Small: 0.875rem (14px) - Regular
Caption: 0.75rem (12px) - Regular
```

---

## UI Components

### Buttons

**Primary Button**:
- Background: #fdb82e
- Text: White (#ffffff)
- Border Radius: 8px
- Padding: 12px 24px
- Font Weight: 500

**Secondary Button**:
- Background: Transparent
- Text: #fdb82e
- Border: 2px solid #fdb82e
- Border Radius: 8px
- Padding: 12px 24px

**Disabled Button**:
- Background: #ecf0f1
- Text: #95a5a6
- Cursor: not-allowed

### Cards

- Background: White (#ffffff)
- Border Radius: 12px
- Box Shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
- Padding: 20px

### Icons

- Primary Color: #fdb82e
- Secondary Color: #7f8c8d
- Size: 24px (standard), 20px (small), 32px (large)

---

## Marketing & Communication

### Voice & Tone

**Voice**: Friendly, professional, helpful
**Tone**: Optimistic, clear, trustworthy

**Do's**:
- Use active voice
- Be concise and clear
- Focus on benefits
- Use inclusive language

**Don'ts**:
- Use jargon without explanation
- Be overly technical with non-technical users
- Make promises you can't keep
- Use negative framing

### Messaging

**Tagline Options**:
- "Find Parking. Earn Money. Simple."
- "Parking Made Easy"
- "Your Parking Marketplace"
- "Smart Parking Solutions"

**Key Messages**:
1. **For Drivers**: Find convenient, affordable parking in seconds
2. **For Owners**: Turn unused spaces into income effortlessly
3. **For Cities**: Optimize parking infrastructure without new construction

---

## Email Templates

### Header
- Background: #fdb82e
- Logo: White or full-color on orange
- Height: 80px

### Body
- Background: #ffffff
- Text: #2c3e50
- Max Width: 600px

### Footer
- Background: #2c3e50
- Text: #ffffff
- Links: #fdb82e

---

## Social Media

### Profile Images
- Use full-color logo on white background
- Ensure logo is centered with even padding
- Export at recommended sizes:
  - Twitter: 400x400px
  - Facebook: 180x180px
  - Instagram: 320x320px
  - LinkedIn: 300x300px

### Cover Images
- Feature logo on left or center
- Use primary orange (#fdb82e) as accent
- Dimensions:
  - Twitter: 1500x500px
  - Facebook: 820x312px
  - LinkedIn: 1584x396px

### Post Graphics
- Always include logo (small, corner placement)
- Use brand colors sparingly as accents
- Maintain readability with high contrast
- Square: 1080x1080px
- Landscape: 1200x630px

---

## Print Materials

### Business Cards
- Logo on front (80x80px minimum)
- Primary color (#fdb82e) as accent
- Standard size: 3.5" x 2" (89mm x 51mm)

### Flyers/Posters
- Logo in top 1/3 of design
- Use orange for headlines and CTAs
- Maintain white space
- Standard sizes: A4 (210x297mm), Letter (8.5"x11")

---

## Accessibility

### Color Contrast Ratios

All color combinations must meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text):

✅ **Pass**: #fdb82e on white (readable with bold text)
✅ **Pass**: #2c3e50 on white (excellent readability)
✅ **Pass**: White on #fdb82e (good readability)
✅ **Pass**: White on #2c3e50 (excellent readability)
⚠️ **Caution**: #fdb82e on light gray (use darker text)

### Alternative Text
Always provide descriptive alt text for the logo:
- Short: "ParkingSpots logo"
- Long: "ParkingSpots - Find parking or earn money from your unused parking space"

---

## File Formats & Exports

### Logo Formats Required

**For Digital Use**:
- PNG with transparency (logo-transparent.png)
- JPG (logo.jpg) - current
- SVG (logo.svg) - scalable, recommended
- ICO (favicon.ico) - 16x16, 32x32, 48x48

**For Print**:
- EPS or AI (vector format)
- PDF (high resolution, 300 DPI)

### Export Settings

**Web/Mobile**:
- Resolution: 72 DPI
- Color Space: RGB
- Format: PNG/JPG

**Print**:
- Resolution: 300 DPI
- Color Space: CMYK
- Format: PDF/EPS

---

## Brand Don'ts

❌ **Don't**:
- Rotate or skew the logo
- Change the logo colors
- Add effects (drop shadows, glows, etc.)
- Place on busy backgrounds without contrast
- Stretch or compress disproportionately
- Use outdated color codes
- Mix different shades of orange inconsistently

✅ **Do**:
- Maintain original proportions
- Use official colors only
- Ensure adequate clear space
- Maintain high contrast
- Test on multiple devices
- Use vector format when possible

---

## Quick Reference

### Hex Codes (Copy & Paste)
```
Primary Orange:  #fdb82e
Hover Orange:    #fdba2e
Active Orange:   #fe9f1d
Light Orange:    #fec538
Dark Text:       #2c3e50
Gray Text:       #7f8c8d
Success:         #27ae60
Error:           #e74c3c
Warning:         #f39c12
Info:            #3498db
```

### RGB Values
```
Primary: rgb(253, 186, 46)
Dark:    rgb(44, 62, 80)
Gray:    rgb(127, 140, 141)
Success: rgb(39, 174, 96)
Error:   rgb(231, 76, 60)
```

---

**For questions about brand usage, contact the design team.**
