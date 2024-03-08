import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz  

API_KEY = '8695fb263a012590d8f7d78f437a8712'  

def get_weather_forecast(api_key, city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            timestamps = [datetime.fromtimestamp(forecast['dt']) for forecast in data['list']]
            temperatures = [forecast['main']['temp'] for forecast in data['list']]
            humidities = [forecast['main']['humidity'] for forecast in data['list']]
            wind_speeds = [forecast['wind']['speed'] for forecast in data['list']]
            rainfalls = [forecast['rain']['3h'] if 'rain' in forecast else 0 for forecast in data['list']]
            sunrise_times = [datetime.fromtimestamp(data['city']['sunrise'])] * len(timestamps)
            sunset_times = [datetime.fromtimestamp(data['city']['sunset'])] * len(timestamps)
            sunrise_ends = [sunrise + (sunset - sunrise) / 2 for sunrise, sunset in zip(sunrise_times, sunset_times)]
            sunset_starts = [sunset - (sunset - sunrise) / 2 for sunrise, sunset in zip(sunrise_times, sunset_times)]

            return timestamps, temperatures, humidities, wind_speeds, rainfalls, sunrise_times, sunset_times, sunrise_ends, sunset_starts
        else:
            messagebox.showerror("Error", f"Failed to fetch weather forecast data: {response.status_code}")
            return None, None, None, None, None, None, None, None, None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return None, None, None, None, None, None, None, None, None

def get_timezone(city):
    try:
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)

        if location:
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=location.latitude, lng=location.longitude)
            return timezone_str
        else:
            return None
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get timezone information: {str(e)}")
        return None

def show_weather_forecast(api_key, city, stats_label, wind_speed_text, humidity_text, celsius_text, fahrenheit_text, sunrise_text, sunset_text, rainfall_label, current_time_label):
    try:
        timestamps, temperatures_celsius, humidities, wind_speeds, rainfalls, sunrise_times, sunset_times, sunrise_ends, sunset_starts = get_weather_forecast(api_key, city)
        if timestamps and temperatures_celsius and humidities and wind_speeds and rainfalls and sunrise_times and sunset_times and sunrise_ends and sunset_starts:
            temperatures_fahrenheit = [(temp * 9/5) + 32 for temp in temperatures_celsius]
            
            fig, axes = plt.subplots(3, 1, figsize=(8, 14))
            fig.suptitle(f"Weather Forecast for {city}", fontsize=16)

            axes[0].plot(timestamps, temperatures_celsius, color='red', label='Temperature (°C)')
            axes[0].plot(timestamps, temperatures_fahrenheit, color='orange', label='Temperature (°F)')
            axes[0].legend()
            axes[0].set_ylabel('Temperature')

            axes[1].plot(timestamps, humidities, color='blue')
            axes[1].set_ylabel('Humidity')

            axes[2].plot(timestamps, wind_speeds, color='green', label='Wind Speed (m/s)')
            axes[2].bar(timestamps, rainfalls, color='purple', label='Rainfall (mm)')
            axes[2].legend()
            axes[2].set_ylabel('Wind Speed / Rainfall')

            time_format = "%H:%M:%S"

            avg_temp_celsius = sum(temperatures_celsius) / len(temperatures_celsius)
            avg_temp_fahrenheit = (avg_temp_celsius * 9/5) + 32
            max_temp_celsius = max(temperatures_celsius)
            max_temp_fahrenheit = (max_temp_celsius * 9/5) + 32
            min_temp_celsius = min(temperatures_celsius)
            min_temp_fahrenheit = (min_temp_celsius * 9/5) + 32
            avg_humidity = sum(humidities) / len(humidities)
            avg_wind_speed = sum(wind_speeds) / len(wind_speeds)
            avg_rainfall = sum(rainfalls) / len(rainfalls)

            stats_text = (f"Average Temperature (Celsius): {avg_temp_celsius:.2f} °C\n"
                          f"Average Temperature (Fahrenheit): {avg_temp_fahrenheit:.2f} °F\n"
                          f"Maximum Temperature (Celsius): {max_temp_celsius:.2f} °C\n"
                          f"Maximum Temperature (Fahrenheit): {max_temp_fahrenheit:.2f} °F\n"
                          f"Minimum Temperature (Celsius): {min_temp_celsius:.2f} °C\n"
                          f"Minimum Temperature (Fahrenheit): {min_temp_fahrenheit:.2f} °F\n"
                          f"Average Humidity: {avg_humidity:.2f} %\n"
                          f"Average Wind Speed: {avg_wind_speed:.2f} m/s\n"
                          f"Average Rainfall: {avg_rainfall:.2f} mm")

            stats_label.config(text=stats_text, font=("Helvetica", 12))

            wind_speed_text.config(state=tk.NORMAL)
            wind_speed_text.delete(1.0, tk.END)
            wind_speed_text.insert(tk.END, f"Average Wind Speed: {avg_wind_speed:.2f} m/s\n")
            wind_speed_text.insert(tk.END, f"Maximum Wind Speed: {max(wind_speeds):.2f} m/s\n")
            wind_speed_text.insert(tk.END, f"Minimum Wind Speed: {min(wind_speeds):.2f} m/s")
            wind_speed_text.config(state=tk.DISABLED)

            humidity_text.config(state=tk.NORMAL)
            humidity_text.delete(1.0, tk.END)
            humidity_text.insert(tk.END, f"Average Humidity: {avg_humidity:.2f} %\n")
            humidity_text.insert(tk.END, f"Maximum Humidity: {max(humidities):.2f} %\n")
            humidity_text.insert(tk.END, f"Minimum Humidity: {min(humidities):.2f} %")
            humidity_text.config(state=tk.DISABLED)

            celsius_text.config(state=tk.NORMAL)
            celsius_text.delete(1.0, tk.END)
            for temp_celsius in temperatures_celsius:
                celsius_text.insert(tk.END, f"{temp_celsius:.2f} °C\n")
            celsius_text.config(state=tk.DISABLED)

            fahrenheit_text.config(state=tk.NORMAL)
            fahrenheit_text.delete(1.0, tk.END)
            for temp_fahrenheit in temperatures_fahrenheit:
                fahrenheit_text.insert(tk.END, f"{temp_fahrenheit:.2f} °F\n")
            fahrenheit_text.config(state=tk.DISABLED)

            sunrise_text.config(state=tk.NORMAL)
            sunrise_text.delete(1.0, tk.END)
            sunrise_text.insert(tk.END, f"Sunrise Time: {sunrise_times[-1].strftime(time_format)}\n")
            sunrise_text.insert(tk.END, f"Sunrise Ends: {sunrise_ends[-1].strftime(time_format)}\n")
            sunrise_text.config(state=tk.DISABLED)

            sunset_text.config(state=tk.NORMAL)
            sunset_text.delete(1.0, tk.END)
            sunset_text.insert(tk.END, f"Sunset Time: {sunset_times[-1].strftime(time_format)}\n")
            sunset_text.insert(tk.END, f"Sunset Starts: {sunset_starts[-1].strftime(time_format)}\n")
            sunset_text.config(state=tk.DISABLED)

            rainfall_label.config(text=f"Rainfall: {sum(rainfalls):.2f} mm" if sum(rainfalls) > 0 else "No Rainfall")
            
            timezone_str = get_timezone(city)
            current_time = datetime.now(pytz.timezone(timezone_str))  
            current_time_label.config(text=f"Current Time in {city}: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({timezone_str})",
                                      font=("Helvetica", 12))

            plt.tight_layout()
            plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display weather forecast: {str(e)}")

def display_heat_map(city):
    try:
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)

        if location:
            m = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)
            folium.Marker([location.latitude, location.longitude], popup=city).add_to(m)
            heat_data = [[location.latitude, location.longitude, 1]]
            HeatMap(heat_data).add_to(m)

            legend_html = """
            <div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; font-size:14px;">
              <p>Heat Map Legend</p>
              <p><span style="background-color: #00ff00; padding: 2px 6px;"></span> Low</p>
              <p><span style="background-color: #ffcc00; padding: 2px 6px;"></span> Moderate</p>
              <p><span style="background-color: #ff0000; padding: 2px 6px;"></span> High</p>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            m.save('heat_map.html')
            webbrowser.open('heat_map.html')
        else:
            messagebox.showerror("Error", "Location not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display heat map: {str(e)}")

def open_website():
    webbrowser.open("https://www.create.xyz/app/7f951d74-8eee-47c8-b186-67bab744100c")

def main():
    root = tk.Tk()
    root.title("Weather Forecast App")

    input_frame = ttk.Frame(root, padding=10)
    button_frame = ttk.Frame(root, padding=10)
    stats_frame = ttk.Frame(root, padding=10)

    input_frame.pack(fill=tk.BOTH, expand=True)
    button_frame.pack(fill=tk.BOTH, expand=True)
    stats_frame.pack(fill=tk.BOTH, expand=True)

    city_label = ttk.Label(input_frame, text="Enter City:")
    city_label.grid(row=0, column=0, padx=5, pady=5)

    city_entry = ttk.Entry(input_frame, width=30)
    city_entry.grid(row=0, column=1, padx=5, pady=5)

    get_weather_button = ttk.Button(button_frame, text="Get Weather Forecast",
                                    command=lambda: show_weather_forecast(API_KEY, city_entry.get(), stats_label, wind_speed_text, humidity_text, celsius_text, fahrenheit_text, sunrise_text, sunset_text, rainfall_label, current_time_label))
    get_weather_button.grid(row=0, column=0, padx=5, pady=5)

    show_heat_map_button = ttk.Button(button_frame, text="Locate",
                                      command=lambda: display_heat_map(city_entry.get()))
    show_heat_map_button.grid(row=0, column=1, padx=5, pady=5)

    open_weather_map_button = ttk.Button(button_frame, text="Complete Weather Map",
                                         command=lambda: webbrowser.open(
                                             "https://openweathermap.org/weathermap?basemap=map&cities=true&layer=windspeed&lat=16.5383&lon=80.6136&zoom=5"))
    open_weather_map_button.grid(row=0, column=2, padx=5, pady=5)

    open_website_button = ttk.Button(button_frame, text="Web Dashboard", command=open_website)
    open_website_button.grid(row=0, column=3, padx=5, pady=5)

    stats_label = ttk.Label(stats_frame, text="", font=("Helvetica", 12), wraplength=400)
    stats_label.pack()

    wind_humidity_frame = ttk.Frame(stats_frame)
    wind_humidity_frame.pack(pady=10)

    wind_speed_label = ttk.Label(wind_humidity_frame, text="Wind Speed Information", font=("Helvetica", 12, "bold"))
    wind_speed_label.grid(row=0, column=0, padx=5, pady=5)

    wind_speed_text = tk.Text(wind_humidity_frame, height=5, width=30, state=tk.DISABLED)
    wind_speed_text.grid(row=1, column=0, padx=5, pady=5)

    humidity_label = ttk.Label(wind_humidity_frame, text="Humidity Information", font=("Helvetica", 12, "bold"))
    humidity_label.grid(row=0, column=1, padx=5, pady=5)

    humidity_text = tk.Text(wind_humidity_frame, height=5, width=30, state=tk.DISABLED)
    humidity_text.grid(row=1, column=1, padx=5, pady=5)

    temperature_frame = ttk.Frame(stats_frame)
    temperature_frame.pack(pady=10)

    celsius_label = ttk.Label(temperature_frame, text="Temperature Information (Celsius)", font=("Helvetica", 12, "bold"))
    celsius_label.grid(row=0, column=0, padx=5, pady=5)

    celsius_text = tk.Text(temperature_frame, height=5, width=30, state=tk.DISABLED)
    celsius_text.grid(row=1, column=0, padx=5, pady=5)

    fahrenheit_label = ttk.Label(temperature_frame, text="Temperature Information (Fahrenheit)", font=("Helvetica", 12, "bold"))
    fahrenheit_label.grid(row=0, column=1, padx=5, pady=5)

    fahrenheit_text = tk.Text(temperature_frame, height=5, width=30, state=tk.DISABLED)
    fahrenheit_text.grid(row=1, column=1, padx=5, pady=5)

    sun_info_frame = ttk.Frame(stats_frame)
    sun_info_frame.pack(pady=10)

    sunrise_label = ttk.Label(sun_info_frame, text="Sunrise Information", font=("Helvetica", 12, "bold"))
    sunrise_label.grid(row=0, column=0, padx=5, pady=5)

    sunrise_text = tk.Text(sun_info_frame, height=5, width=30, state=tk.DISABLED)
    sunrise_text.grid(row=1, column=0, padx=5, pady=5)

    sunset_label = ttk.Label(sun_info_frame, text="Sunset Information", font=("Helvetica", 12, "bold"))
    sunset_label.grid(row=0, column=1, padx=5, pady=5)

    sunset_text = tk.Text(sun_info_frame, height=5, width=30, state=tk.DISABLED)
    sunset_text.grid(row=1, column=1, padx=5, pady=5)

    rainfall_label = ttk.Label(stats_frame, text="", font=("Helvetica", 12))
    rainfall_label.pack()

    current_time_label = ttk.Label(stats_frame, text="", font=("Helvetica", 12))
    current_time_label.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
