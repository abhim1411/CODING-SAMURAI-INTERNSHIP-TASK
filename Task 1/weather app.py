import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import urllib.request
import urllib.parse
import urllib.error
import random

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # You'll need to get a free API key from OpenWeatherMap
        # IMPORTANT: New API keys take up to 2 hours to activate!
        self.api_key = "ace557d2c7dded27ddca4265b3de600f"  # Replace with your actual API key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Weather background gradients (CSS-like colors)
        self.weather_backgrounds = {
            'Clear': ['#87CEEB', '#FFD700', '#FFA500'],  # Sky blue to golden yellow
            'Clouds': ['#708090', '#B0C4DE', '#D3D3D3'],   # Gray gradient
            'Rain': ['#2C3E50', '#34495E', '#5D6D7E'],     # Dark blue-gray
            'Drizzle': ['#5D6D7E', '#85929E', '#AEB6BF'],  # Light gray-blue
            'Thunderstorm': ['#1C2833', '#2C3E50', '#566573'], # Very dark
            'Snow': ['#F8F9FA', '#E8F4F8', '#D5DBDB'],     # Light blue-white
            'Mist': ['#85929E', '#AEB6BF', '#D5DBDB'],     # Light gray
            'Fog': ['#85929E', '#AEB6BF', '#D5DBDB'],      # Light gray
            'Haze': ['#F4D03F', '#F7DC6F', '#F9E79F'],     # Light yellow
            'default': ['#2c3e50', '#34495e', '#3f566b']   # Default dark
        }
        
        self.setup_ui()
        self.set_background('default')
        
    def setup_ui(self):
        # Main container - FIXED: Remove transparent background
        main_frame = tk.Frame(self.root, bg='#34495e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Weather App", 
            font=('Arial', 24, 'bold'),
            bg='#34495e', 
            fg='#ecf0f1'
        )
        title_label.pack(pady=(0, 30))
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='#34495e')
        search_frame.pack(fill='x', pady=(0, 30))
        
        # City entry - FIXED: Remove rgba colors
        self.city_var = tk.StringVar()
        city_entry = tk.Entry(
            search_frame,
            textvariable=self.city_var,
            font=('Arial', 14),
            bg='#34495e',
            fg='#ecf0f1',
            insertbackground='#ecf0f1',
            relief='flat',
            bd=10
        )
        city_entry.pack(side='left', fill='x', expand=True, ipady=8)
        city_entry.bind('<Return>', lambda e: self.get_weather())
        
        # Search button
        search_btn = tk.Button(
            search_frame,
            text="Search",
            command=self.get_weather,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=20,
            cursor='hand2'
        )
        search_btn.pack(side='right', padx=(10, 0), ipady=8)
        
        # Weather display frame - FIXED: Remove rgba colors
        self.weather_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        self.weather_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Default display
        self.setup_default_display()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Enter a city name to get weather information")
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=('Arial', 10),
            bg='#34495e',
            fg='#95a5a6'
        )
        status_label.pack(pady=(10, 0))
        
    def setup_default_display(self):
        # Clear existing widgets
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Default message
        default_label = tk.Label(
            self.weather_frame,
            text="🌤️\n\nSearch for a city to view\nweather information",
            font=('Arial', 16),
            bg='#34495e',
            fg='#bdc3c7',
            justify='center'
        )
        default_label.pack(expand=True, fill='both')
        
    def setup_weather_display(self, data, use_celsius=False):
        # Get weather condition for background
        weather_main = data['weather'][0]['main']
        
        # Update background based on weather
        self.set_background(weather_main)
        
        # Update UI elements to match new background
        self.update_ui_colors(weather_main)
        
        # Clear existing widgets
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Weather info container - FIXED: Remove rgba colors
        info_frame = tk.Frame(self.weather_frame, bg='#34495e')
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # City name
        city_label = tk.Label(
            info_frame,
            text=f"{data['name']}, {data['sys']['country']}",
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        )
        city_label.pack(pady=(0, 10))
        
        # Weather icon and description
        weather_desc = data['weather'][0]['description'].title()
        
        # Weather emoji mapping
        weather_emojis = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️'
        }
        
        emoji = weather_emojis.get(weather_main, '🌤️')
        
        weather_icon_label = tk.Label(
            info_frame,
            text=emoji,
            font=('Arial', 48),
            bg='#34495e'
        )
        weather_icon_label.pack(pady=(10, 5))
        
        weather_desc_label = tk.Label(
            info_frame,
            text=weather_desc,
            font=('Arial', 16),
            bg='#34495e',
            fg='#ecf0f1'
        )
        weather_desc_label.pack(pady=(0, 20))
        
        # Temperature
        if use_celsius:
            # API returns in Celsius when units=metric
            temp_celsius = round(data['main']['temp'], 1)
            temp_fahrenheit = round((temp_celsius * 9/5) + 32, 1)
        else:
            # API returns in Kelvin by default
            temp_celsius = round(data['main']['temp'] - 273.15, 1)
            temp_fahrenheit = round((temp_celsius * 9/5) + 32, 1)
        
        temp_label = tk.Label(
            info_frame,
            text=f"{temp_celsius}°C / {temp_fahrenheit}°F",
            font=('Arial', 24, 'bold'),
            bg='#34495e',
            fg='#e74c3c'
        )
        temp_label.pack(pady=(0, 20))
        
        # Additional info frame
        details_frame = tk.Frame(info_frame, bg='#34495e')
        details_frame.pack(fill='x', pady=(0, 10))
        
        # Feels like temperature
        if use_celsius:
            feels_like = round(data['main']['feels_like'], 1)
        else:
            feels_like = round(data['main']['feels_like'] - 273.15, 1)
            
        feels_like_label = tk.Label(
            details_frame,
            text=f"Feels like: {feels_like}°C",
            font=('Arial', 12),
            bg='#34495e',
            fg='#bdc3c7'
        )
        feels_like_label.pack()
        
        # Humidity and pressure info
        info_frame2 = tk.Frame(info_frame, bg='#34495e')
        info_frame2.pack(fill='x', pady=10)
        
        # Left column
        left_frame = tk.Frame(info_frame2, bg='#34495e')
        left_frame.pack(side='left', fill='x', expand=True)
        
        humidity_label = tk.Label(
            left_frame,
            text=f"💧 Humidity: {data['main']['humidity']}%",
            font=('Arial', 11),
            bg='#34495e',
            fg='#3498db'
        )
        humidity_label.pack(anchor='w')
        
        pressure_label = tk.Label(
            left_frame,
            text=f"🌡️ Pressure: {data['main']['pressure']} hPa",
            font=('Arial', 11),
            bg='#34495e',
            fg='#3498db'
        )
        pressure_label.pack(anchor='w', pady=(5, 0))
        
        # Right column
        right_frame = tk.Frame(info_frame2, bg='#34495e')
        right_frame.pack(side='right', fill='x', expand=True)
        
        if 'visibility' in data:
            visibility_km = data['visibility'] / 1000
            visibility_label = tk.Label(
                right_frame,
                text=f"👁️ Visibility: {visibility_km} km",
                font=('Arial', 11),
                bg='#34495e',
                fg='#3498db'
            )
            visibility_label.pack(anchor='e')
        
        wind_speed = data['wind']['speed']
        wind_label = tk.Label(
            right_frame,
            text=f"💨 Wind: {wind_speed} m/s",
            font=('Arial', 11),
            bg='#34495e',
            fg='#3498db'
        )
        wind_label.pack(anchor='e', pady=(5, 0))
        
        # Last updated
        current_time = datetime.now().strftime("%H:%M")
        updated_label = tk.Label(
            info_frame,
            text=f"Last updated: {current_time}",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6'
        )
        updated_label.pack(pady=(20, 0))
    
    def set_background(self, weather_condition):
        """Set background color based on weather condition"""
        colors = self.weather_backgrounds.get(weather_condition, self.weather_backgrounds['default'])
        
        # Use simple solid background color instead of gradient
        try:
            # Remove any existing background canvas
            if hasattr(self, 'bg_canvas'):
                self.bg_canvas.destroy()
                delattr(self, 'bg_canvas')
            
            # Set simple background color
            self.root.configure(bg=colors[0])
            
        except Exception as e:
            # Fallback to default color
            self.root.configure(bg='#2c3e50')
    
    def create_gradient(self, canvas, color1, color2, color3):
        """Create a vertical gradient effect"""
        try:
            # Convert hex colors to RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            rgb3 = hex_to_rgb(color3)
            
            height = 700
            # Create gradient in three sections
            section_height = height // 3
            
            # Top section (color1 to color2)
            for i in range(section_height):
                ratio = i / section_height
                r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio)
                g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio)
                b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                canvas.create_line(0, i, 500, i, fill=color, width=1)
            
            # Middle section (color2 to color3)
            for i in range(section_height):
                ratio = i / section_height
                r = int(rgb2[0] + (rgb3[0] - rgb2[0]) * ratio)
                g = int(rgb2[1] + (rgb3[1] - rgb2[1]) * ratio)
                b = int(rgb2[2] + (rgb3[2] - rgb2[2]) * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                canvas.create_line(0, section_height + i, 500, section_height + i, fill=color, width=1)
            
            # Bottom section (continue color3)
            for i in range(height - 2 * section_height):
                canvas.create_line(0, 2 * section_height + i, 500, 2 * section_height + i, fill=color3, width=1)
                
        except Exception:
            # Fallback to solid color
            canvas.configure(bg=color1)
    
    def add_weather_decorations(self, weather_condition):
        """Add decorative elements based on weather"""
        try:
            if weather_condition == 'Clear':
                # Add sun rays
                self.add_sun_rays()
            elif weather_condition in ['Rain', 'Drizzle']:
                # Add rain drops
                self.add_rain_drops()
            elif weather_condition == 'Snow':
                # Add snowflakes
                self.add_snowflakes()
            elif weather_condition == 'Thunderstorm':
                # Add lightning effect
                self.add_lightning()
            
            # Lower decorations so they don't cover UI elements
            if hasattr(self, 'bg_canvas'):
                self.bg_canvas.lower()
                
        except Exception:
            pass  # Skip decorations if they fail
    
    def add_sun_rays(self):
        """Add sun rays decoration"""
        try:
            # Create sun rays in corners
            sun_color = "#FFD700"
            for i in range(8):
                angle = i * 45
                x1 = 50 + 30 * (i % 2)
                y1 = 50 + 30 * (i % 2)
                x2 = x1 + 40
                y2 = y1 + 40
                self.bg_canvas.create_line(x1, y1, x2, y2, fill=sun_color, width=2, capstyle='round')
        except Exception:
            pass
    
    def add_rain_drops(self):
        """Add rain drops decoration"""
        try:
            rain_color = "#4682B4"
            for _ in range(15):
                x = random.randint(0, 500)
                y = random.randint(0, 200)
                self.bg_canvas.create_line(x, y, x+2, y+15, fill=rain_color, width=1)
        except Exception:
            pass
    
    def add_snowflakes(self):
        """Add snowflakes decoration"""
        try:
            snow_color = "#FFFFFF"
            for _ in range(20):
                x = random.randint(0, 500)
                y = random.randint(0, 300)
                # Create simple snowflake
                self.bg_canvas.create_oval(x, y, x+3, y+3, fill=snow_color, outline=snow_color)
        except Exception:
            pass
    
    def add_lightning(self):
        """Add lightning effect"""
        try:
            lightning_color = "#FFFF00"
            # Simple lightning bolt
            points = [100, 50, 110, 100, 90, 150, 120, 200]
            self.bg_canvas.create_line(points[0], points[1], points[2], points[3], 
                                     fill=lightning_color, width=3)
            self.bg_canvas.create_line(points[2], points[3], points[4], points[5], 
                                     fill=lightning_color, width=3)
            self.bg_canvas.create_line(points[4], points[5], points[6], points[7], 
                                     fill=lightning_color, width=3)
        except Exception:
            pass
    
    def update_ui_colors(self, weather_condition):
        """Update UI element colors to match weather background"""
        try:
            # Get current background color
            bg_colors = self.weather_backgrounds.get(weather_condition, self.weather_backgrounds['default'])
            main_bg = bg_colors[0]
            
            # Update main frame background
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=main_bg)
                    for child in widget.winfo_children():
                        if isinstance(child, (tk.Label, tk.Frame)):
                            child.configure(bg=main_bg)
        except Exception:
            pass  # Skip if color update fails
        
    def get_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return
            
        self.status_var.set("Fetching weather data...")
        self.root.update()
        
        try:
            # Check if API key is set
            if self.api_key == "YOUR_API_KEY_HERE" or not self.api_key.strip():
                # Sample data for demonstration
                sample_data = self.get_sample_data(city)
                self.setup_weather_display(sample_data)
                self.status_var.set("Showing sample data - Add your API key for real data")
            else:
                # Validate API key format (should be 32 characters)
                if len(self.api_key.strip()) != 32:
                    messagebox.showerror("API Key Error", 
                        "Invalid API key format. OpenWeatherMap API keys are 32 characters long.")
                    self.status_var.set("Invalid API key")
                    return
                
                # Actual API call using urllib
                params = urllib.parse.urlencode({
                    'q': city,
                    'appid': self.api_key.strip(),
                    'units': 'metric'  # Get temperature in Celsius directly
                })
                url = f"{self.base_url}?{params}"
                
                print(f"API URL: {url}")  # Debug print
                
                # Create request with headers
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'WeatherApp/1.0')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        print(f"API Response: {data}")  # Debug print
                        self.setup_weather_display(data, use_celsius=True)
                        self.status_var.set("Weather data updated successfully")
                    else:
                        raise Exception(f"HTTP Error: {response.status}")
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code}"
            if e.code == 401:
                error_msg += " - Invalid API key"
            elif e.code == 404:
                error_msg += " - City not found"
            elif e.code == 429:
                error_msg += " - API rate limit exceeded"
            
            messagebox.showerror("API Error", f"Failed to fetch weather data: {error_msg}")
            self.status_var.set("API request failed")
        except urllib.error.URLError as e:
            messagebox.showerror("Network Error", f"Connection error: {str(e.reason)}")
            self.status_var.set("Connection error")
        except json.JSONDecodeError as e:
            messagebox.showerror("Data Error", "Invalid response format from weather service")
            self.status_var.set("Invalid response format")
        except KeyError as e:
            messagebox.showerror("Data Error", f"Missing data in response: {str(e)}")
            self.status_var.set("Incomplete weather data")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.status_var.set("An error occurred")
    
    def get_sample_data(self, city):
        """Generate sample weather data for demonstration"""
        weather_conditions = [
            {'main': 'Clear', 'description': 'clear sky'},
            {'main': 'Clouds', 'description': 'few clouds'},
            {'main': 'Rain', 'description': 'light rain'},
            {'main': 'Snow', 'description': 'light snow'}
        ]
        
        return {
            'name': city.title(),
            'sys': {'country': 'XX'},
            'weather': [random.choice(weather_conditions)],
            'main': {
                'temp': random.uniform(15, 30),  # Random temp between 15-30°C
                'feels_like': random.uniform(15, 32),
                'humidity': random.randint(40, 80),
                'pressure': random.randint(1000, 1020)
            },
            'wind': {'speed': random.uniform(1, 8)},
            'visibility': random.randint(8000, 10000)
        }

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()