# Weather Application - Module 6 Lab

## Student Information
- **Name**: Elyssa Olivares
- **Student ID**: 231002284
- **Course**: CCCS 106
- **Section**: Bachelor of Science in Computer Science

## Project Overview

This is a weather up that enables user to search locations in the world and their current temperature in celcius. It has added features like light/dark theme toggle, 5 - day forecast of the location's temperature with dates, geolocation feature which enables to locate the user's location and temperature by only clicking an icon, and a map for the current ir searched location. 

## Features Implemented

### Base Features
- [✓] City search functionality
- [✓] Current weather display
- [✓] Temperature, humidity, wind speed
- [✓] Weather icons
- [✓] Error handling
- [✓] Modern UI with Material Design

### Enhanced Features
1. **[5-Day Temperature Forecast]**
   - This feature used to predict the possibe temperature forcast for a specific location with dates.

   - I chose this feature as it might be useful in predicting temperature especially when having future plans and moght as well as be prepared for upcoming weather.

   - I had no experienced having difficulty in updating the code using this feature, I just adjusted it's appearance to be more pleasing. 

2. **[Current Location Weather]**
   - This feauture is for the user to check his/her current location's temperature, humidity, and windspeed together with it's 5-day forecasts and specific location using map.

   - I chose this feature as it made me curious how it will work knowing that it will access the users location and it will makae the temperature check for current location much easier.

   -  I had experience having hardtime especially in accessing the current location as it is not very specific but i just adjusted the location format and settled with it.

3. **[Weather Map Integration]**
   - This feauture is for the user to access a web-based interactive map of the searched location and had some feature of Clouds, Precipitation, and Temperature.

   - I chose this feature as it can be useful for correct checking locations.

   -  I had experience having hardtime especially in the web map as sometimes it won't appear and it can't be closed at first but I just turned it to a web-based map so it can be easily navigated and seen.

4. **[Toggle for Temperature Unit to be Celcius or Fahrenheit]**
   - This feauture is for the user to to swap their most known temperature, celcius or fahrenheit.

   - I chose this feature as sometimes people have more known unit of measurements.

   -  I do not had a hard time in adding this feature.

5. **[Weather Condition Icons and Colors]**
   - This feauture enables the weather display more pleasing by changing the background color according to the weather conditions.

   - I chose this feature as it can provide interactive display for the users.

   -  I do not had a hard time in adding this feature.


## Screenshots

**Searched Location**
![alt text](<screenshots/Screenshot 2025-11-21 at 1.16.58 PM.png>)
![alt text](<screenshots/Screenshot 2025-11-21 at 1.17.09 PM.png>)

**Current Location**
![alt text](<screenshots/Screenshot 2025-11-21 at 1.17.21 PM.png>)
![alt text](<screenshots/Screenshot 2025-11-21 at 1.17.24 PM.png>)

**Togle for Temperature Unit**
![alt text](<screenshots/Screenshot 2025-11-21 at 1.17.33 PM.png>)

**Map with the Current Location and Searched Location**
![alt text](<screenshots/Screenshot 2025-11-21 at 1.18.30 PM.png>)

**Desktop View**
![alt text](<screenshots/Screenshot 2025-11-21 at 1.26.55 PM.png>)

**Testing**
![alt text](<screenshots/Screenshot 2025-11-21 at 1.25.29 PM.png>)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/elysaolivares/cccs106-projects.git
cd cccs106-projects/mod6_labs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OpenWeatherMap API key to .env
