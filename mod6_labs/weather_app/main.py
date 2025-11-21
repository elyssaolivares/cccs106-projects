"""Weather Application using Flet v0.28.3"""

import flet as ft
import asyncio
import httpx
import os
import json
from datetime import datetime
from weather_service import WeatherService, WeatherServiceError
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        # Map markers stored as dicts: {lat, lon, label, popup}
        self.map_markers = []
        # Last geolocation metadata returned by IP services
        self.last_geo_info = None
        self.map_dialog = None
        self.map_webview = None
        # Temperature unit system ("metric" for °C, "imperial" for °F)
        self.current_unit = "metric"
        self.current_temp = None
        self.current_feels_like = None
        
        self.setup_page()
        self.build_ui()

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        # Use a light theme and explicit white background so UI isn't grey.
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.scroll = "auto"
       
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.PURPLE_900,
        )
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = True
        
        # Center the window on desktop
        try:
            self.page.window.center()
        except Exception:
            pass

    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PURPLE_100,
        )

        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Map button (opens map dialog)
        self.map_button = ft.IconButton(
            icon=ft.Icons.MAP,
            tooltip="Open map",
            on_click=self.open_map,
        )

        # Location button (will appear beside the theme toggle)
        self.location_button = ft.IconButton(
            icon=ft.Icons.MY_LOCATION,
            tooltip="Use my location",
            on_click=self.on_get_location,
        )

        # Unit toggle button
        self.unit_button = ft.IconButton(
            icon=ft.Icons.SWAP_VERT,
            tooltip="Toggle °C / °F",
            on_click=self.toggle_units,
        )

        self.title_row = ft.Row(
            [
                self.title,
                ft.Row([
                    self.unit_button,
                    self.map_button,
                    self.location_button,
                    self.theme_button
                ], spacing=6),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.PURPLE_100,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )

        # Search button
        self.search_button = ft.ElevatedButton(
            "Search",
            on_click=self.on_search,
        )

        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.PURPLE_100,
            border_radius=10,
            padding=20,
        )
        
        # Forecast container (five small day cards)
        self.forecast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.PURPLE_50,
            border_radius=8,
            padding=8,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    self.title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    self.search_button,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    self.forecast_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

    def build_map_html(self, center_lat=20.0, center_lon=0.0, zoom=2):
        """Generate a map HTML file (based on the template) with markers and API key injected.
        Returns the file:// URL to the generated HTML file. """
        template_path = os.path.join(os.path.dirname(__file__), "map.html")
        with open(template_path, "r", encoding="utf-8") as f:
            tpl = f.read()

        markers_json = json.dumps(self.map_markers)
        tpl = tpl.replace("__OWM_API_KEY__", Config.API_KEY)
        tpl = tpl.replace("__DEFAULT_LAT__", str(center_lat))
        tpl = tpl.replace("__DEFAULT_LON__", str(center_lon))
        tpl = tpl.replace("__DEFAULT_ZOOM__", str(zoom))
        tpl = tpl.replace("__MARKERS__", markers_json)

        out_path = os.path.join(os.path.dirname(__file__), "map_generated.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(tpl)

        return f"file://{out_path}"

    def open_map(self, e):
        """Open a dialog containing the map WebView. """
        # Clear any previous error messages
        self.error_message.visible = False

        # Determine sensible center
        if self.map_markers:
            center = self.map_markers[-1]
            lat = center.get("lat", 20.0)
            lon = center.get("lon", 0.0)
            zoom = 6
        else:
            lat, lon, zoom = 20.0, 0.0, 2
        url = self.build_map_html(center_lat=lat, center_lon=lon, zoom=zoom)

        # Open map in the system browser for reliable cross-platform behavior
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            # Fallback UI error if opening fails
            self.show_error("Could not open map in browser.")
        finally:
            # Hide snackbar (defensive: ensure it's closed after open attempt)
            try:
                # Some Flet versions will auto-close the snackbar after duration.
                # Set open False to remove it immediately.
                if hasattr(self.page, "snack_bar") and self.page.snack_bar:
                    self.page.snack_bar.open = False
                    self.page.update()
            except Exception:
                pass

    def on_webview_console(self, e):
        """Handle console messages from the WebView. Expect JSON payloads from the map. """
        try:
            # event object may expose different attributes depending on flet version
            msg = getattr(e, 'message', None) or getattr(e, 'text', None) or str(e)
            payload = json.loads(msg)
        except Exception:
            return

        if payload.get("type") == "click":
            lat = payload.get("lat")
            lon = payload.get("lon")
            if lat is None or lon is None:
                return
            # Schedule fetching weather for clicked location
            self.page.run_task(self.handle_map_click(lat, lon))

    async def handle_map_click(self, lat, lon):
        try:
            weather = await self.weather_service.get_weather_by_coordinates(lat, lon)
            await self.display_weather(weather)

            # Add marker for clicked location
            name = weather.get("name") or f"{lat:.2f},{lon:.2f}"
            popup = f"{name}: {weather.get('weather',[{}])[0].get('description','')}"
            self.map_markers.append({"lat": lat, "lon": lon, "label": name, "popup": popup})

            # If dialog is open, regenerate map and reload
            if self.map_dialog and self.map_webview:
                url = self.build_map_html(center_lat=lat, center_lon=lon, zoom=6)
                self.map_webview.url = url
                self.page.update()

        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception:
            self.show_error("Could not get weather for map location")
    
    def close_map(self, e=None):
        """Close the map dialog and cleanup references."""
        try:
            if self.map_dialog:
                try:
                    self.map_dialog.open = False
                except Exception:
                    pass
                self.page.dialog = None
            self.map_webview = None
            self.map_dialog = None
            self.page.update()
        except Exception:
            pass
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)

    def on_get_location(self, e):
        """Handle location button click — schedule location weather task."""
        self.page.run_task(self.get_location_weather)

    async def get_location_weather(self):
        """Get weather for current location."""
        # Clear search input
        self.city_input.value = ""
        
        # Show loading state
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()
        last_exc = None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Try a list of public IP->geo services until one returns lat/lon
                services = [
                    ("https://ipapi.co/json/", lambda d: (d.get("latitude"), d.get("longitude"))),
                    ("https://ipinfo.io/json", lambda d: tuple(map(float, d.get("loc", "").split(","))) if d.get("loc") else (None, None)),
                    ("http://ip-api.com/json/", lambda d: (d.get("lat"), d.get("lon"))),
                ]

                lat = lon = None
                for url, extractor in services:
                    try:
                        resp = await client.get(url)
                        resp.raise_for_status()
                        data = resp.json()
                        coords = extractor(data)
                        if coords and coords[0] is not None and coords[1] is not None:
                            lat, lon = coords[0], coords[1]
                            break
                    except Exception as e:
                        last_exc = e

                if lat is None or lon is None:
                    # Provide a helpful error message based on last exception or generic info
                    if last_exc:
                        raise RuntimeError(f"Geolocation failed: {last_exc}") from last_exc
                    raise RuntimeError("Geolocation services did not return coordinates")

                # Save geo metadata for richer display (extract common fields)
                geo_meta = {
                    "source": url,
                    "lat": lat,
                    "lon": lon,
                    "city": None,
                    "region": None,
                    "country": None,
                    "country_code": None,
                    "postal": None,
                    "ip": None,
                    "timezone": None,
                    "org": None,
                }
                # populate common keys depending on service
                try:
                    # ipapi.co
                    if "ipapi.co" in url:
                        geo_meta.update({
                            "city": data.get("city"),
                            "region": data.get("region"),
                            "country": data.get("country_name"),
                            "country_code": data.get("country_code"),
                            "postal": data.get("postal"),
                            "ip": data.get("ip"),
                            "timezone": data.get("timezone"),
                            "org": data.get("org"),
                        })
                    # ipinfo.io
                    elif "ipinfo.io" in url:
                        geo_meta.update({
                            "city": data.get("city"),
                            "region": data.get("region"),
                            "country": data.get("country"),
                            "country_code": data.get("country"),
                            "postal": data.get("postal"),
                            "ip": data.get("ip"),
                            "timezone": data.get("timezone"),
                            "org": data.get("org"),
                        })
                    # ip-api.com
                    elif "ip-api.com" in url:
                        geo_meta.update({
                            "city": data.get("city"),
                            "region": data.get("regionName"),
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "postal": data.get("zip"),
                            "ip": data.get("query"),
                            "timezone": data.get("timezone"),
                            "org": data.get("org"),
                        })
                except Exception:
                    pass

                self.last_geo_info = geo_meta

                # Fetch weather by coordinates
                weather = await self.weather_service.get_weather_by_coordinates(lat, lon)
                await self.display_weather(weather)
                
                # Get city name from weather data for forecast
                city_name = weather.get("name", "")
                if city_name:
                    # Fetch and display 5-day forecast
                    await self.display_forecast(city_name)

        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception as e:
            # Show the underlying error to help debugging (trim long messages)
            msg = str(e)
            if len(msg) > 240:
                msg = msg[:237] + "..."
            self.show_error(f"Could not get your location: {msg}")
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Clear geolocation info when doing manual search
        self.last_geo_info = None
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)

            # Display weather (await async display helper)
            await self.display_weather(weather_data)

            # Fetch and display 5-day forecast
            await self.display_forecast(city)

        except WeatherServiceError as e:
            # Known / expected errors from the service (user-friendly)
            self.show_error(str(e))

        except Exception:
            # Unexpected errors (avoid exposing raw trace to user)
            self.show_error("An unexpected error occurred. Please try again.")
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def display_weather(self, data: dict):
        """Display weather information (no Lottie)."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Add animation to container
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        self.current_temp = temp
        self.current_feels_like = feels_like

        # Fade in
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()
        
        # Build weather display - use simple "City, CC" format for geolocation
        if getattr(self, "last_geo_info", None) and self.last_geo_info.get("city"):
            city_display = self.last_geo_info.get("city", city_name)
            country_code = self.last_geo_info.get("country_code", country)
            display_location = f"{city_display}, {country_code}"
        else:
            # Manual search: Use standard format from API
            display_location = f"{city_name}, {country}"

        condition = data.get("weather", [{}])[0].get("main", "").lower()
        color_map = {
            "clear": ft.Colors.AMBER_200,
            "clouds": ft.Colors.BLUE_GREY_200,
            "rain": ft.Colors.BLUE_300,
            "drizzle": ft.Colors.BLUE_200,
            "thunderstorm": ft.Colors.DEEP_PURPLE_700,
            "snow": ft.Colors.CYAN_100,
            "mist": ft.Colors.GREY_300,
        }

        new_color = color_map.get(condition, ft.Colors.PURPLE_100)

        # Smooth transition
        self.weather_container.animate_bgcolor = ft.Animation(500, ft.AnimationCurve.EASE)
        self.weather_container.bgcolor = new_color

        # Use OpenWeatherMap png icon (works reliably)
        weather_icon_container = ft.Container(
            content=ft.Image(
                src=f"https://openweathermap.org/img/wn/{icon_code}@4x.png",
                width=150,
                height=150,
                fit=ft.ImageFit.CONTAIN,
            ),
        )

        weather_icon = weather_icon_container

        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    display_location,
                    size=32,
                    color=ft.Colors.GREY_700,
                    weight=ft.FontWeight.BOLD,
                ),
                
                weather_icon,

                ft.Text(
                    description,
                    size=20,
                    italic=True,
                    color=ft.Colors.GREY_700,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_300,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        self.weather_container.visible = True
        self.error_message.visible = False

        # Add marker for this city if coordinates available
        coord = data.get("coord", {})
        lat = coord.get("lat")
        lon = coord.get("lon")
        if lat is not None and lon is not None:
            popup = f"{city_name}: {description}"
            self.map_markers.append({"lat": lat, "lon": lon, "label": city_name, "popup": popup})
            # If map dialog is open, regenerate map and reload
            if self.map_dialog and self.map_webview:
                url = self.build_map_html(center_lat=lat, center_lon=lon, zoom=6)
                self.map_webview.url = url

        self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_500),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )

    async def display_forecast(self, city: str):
        """Fetch 5-day forecast and render five small summary cards."""
        try:
            forecast = await self.weather_service.get_forecast(city)
            items = forecast.get("list", [])

            if not items:
                self.forecast_container.visible = False
                self.page.update()
                return

            # Choose snapshots approx every 24 hours (every 8 entries)
            indices = [0, 8, 16, 24, 32]
            cards = []
            for i in indices:
                if i >= len(items):
                    break
                it = items[i]
                dt_txt = it.get("dt_txt", "")
                try:
                    dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                    label = dt.strftime("%a %d")
                except Exception:
                    label = dt_txt.split(" ")[0]

                temp = it.get("main", {}).get("temp")
                icon_code = it.get("weather", [{}])[0].get("icon", "01d")

                cards.append(self.create_forecast_card(icon_code, label, temp))

            # Render cards in a horizontally-scrollable row
            self.forecast_container.content = ft.Row(
                cards,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
            )
            self.forecast_container.visible = True
            self.page.update()

        except WeatherServiceError as e:
            self.show_error(str(e))

        except Exception:
            self.forecast_container.visible = False
            self.page.update()

    def create_forecast_card(self, icon_code: str, label: str, temp: float):
        """Create a small forecast card for a day snapshot."""
        temp_str = f"{temp:.0f}°C" if isinstance(temp, (int, float)) else "N/A"
        # Keep cards a consistent size that matches the weather details area visually
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, color=ft.Colors.BLUE_400, size=12),
                    ft.Container(
                        content=ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=48,
                            height=48,
                        ),
                        width=64,
                        height=64,
                        padding=6,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                    ),
                    ft.Text(temp_str, size=14, color=ft.Colors.PURPLE_200, weight=ft.FontWeight.BOLD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=10,
            width=120,
            height=160,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit and update display."""
        if self.current_temp is None:
            return  # nothing to convert yet

        # Switch unit
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            self.current_temp = (self.current_temp * 9/5) + 32
            self.current_feels_like = (self.current_feels_like * 9/5) + 32
        else:
            self.current_unit = "metric"
            self.current_temp = (self.current_temp - 32) * 5/9
            self.current_feels_like = (self.current_feels_like - 32) * 5/9

        # Refresh weather display
        self.update_temperature_display()

    def update_temperature_display(self):
        """Refresh only the temperature text without refetching API."""
        if not self.weather_container.content:
            return
        # Temperature is at index 3 and feels like at index 4 in the Column we build
        try:
            temp_text = self.weather_container.content.controls[3]
            feels_text = self.weather_container.content.controls[4]
        except Exception:
            return

        if self.current_unit == "metric":
            temp_text.value = f"{self.current_temp:.1f}°C"
            feels_text.value = f"Feels like {self.current_feels_like:.1f}°C"
        else:
            temp_text.value = f"{self.current_temp:.1f}°F"
            feels_text.value = f"Feels like {self.current_feels_like:.1f}°F"

        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)
