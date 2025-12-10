# CCCS 106 Projects
Application Development and Emerging Technologies  
Academic Year 2025-2026

## Student Information
- **Name:** Elyssa Olivares
- **Student ID:** 23100****
- **Program:** Bachelor of Science in Computer Science
- **Section:** BSCS 3B

## Repository Structure

### Week 1 Labs - Environment Setup and Python Basics
- `week1_labs/hello_world.py` - Basic Python introduction
- `week1_labs/basic_calculator.py` - Simple console calculator

### Week 2 Labs - Git and Flet GUI Development
- `week2_labs/hello_flet.py` - First Flet GUI application
- `week2_labs/personal_info_gui.py` - Enhanced personal information manager
- `week2_labs/enhanced_calculator.py` - GUI calculator (coming soon)

### Week 3 Labs - User Login App
- `db_connection.py` - Database connection fot the app using SQLite.
- `main.py` - Application code using flet framewok.

### Week 4 Labs - Contact Book App
- `app_logic.py` - Include the app logics to be used.
- `database.py` - Database connection fot the app using SQLite.
- `main.py` - The main flet application file.

### Module 6 - Weather App
- `main.py` - The main flet file.
- `config.py` - The API keys and network comfigurations file.
- `test_weather_service.py` - The test code for cmpleteng the requiremnts.
- `Weather_service.py` - The weather services file.
  
### Module 1 Final Project
- `module1_final/` - Final integrated project (TBD)

## Technologies Used
- **Python 3.8+** - Main programming language
- **Flet 0.28.3** - GUI framework for cross-platform applications
- **Git & GitHub** - Version control and collaboration
- **VS Code** - Integrated development environment

## Development Environment
- **Virtual Environment:** cccs106_env
- **Python Packages:** flet==0.28.3
- **Platform:** Windows 10/11

## How to Run Applications

### Prerequisites
1. Python 3.8+ installed
2. Virtual environment activated: `cccs106_env\Scripts\activate`
3. Flet installed: `pip install flet==0.28.3`

### Running GUI Applications
```cmd
# Navigate to project directory
cd week2_labs

# Run applications
python hello_flet.py
python personal_info_gui.py
