//***************Submit button handler:***************
document.getElementById("weatherForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const city = document.getElementById("weatherlocation").value;

  const coords = await getCoordinates(city);
  if (coords.error) {
    alert("City not found");
    return;
  }

  const forecast = await getForecast(coords.latitude, coords.longitude);

  displayCurrentConditions(forecast);

  displayDailyForecast(forecast.daily);
});

//***************Call open meteo API***************
//geocoding
async function getCoordinates(city) {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${city}&count=1`;
  const res = await fetch(url);
  const data = await res.json();

  if (!data.results || data.results.length === 0) {
    return { error: "City not found" };
  }

  return data.results[0];
}

//***************Converts city into lat and long that open mateo needs***************
async function getForecast(lat, lon) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max,sunrise,sunset&temperature_unit=fahrenheit&timezone=auto`;

  const res = await fetch(url);
  return await res.json();
}

//***************Display current day's weather above the forcast boxes:***************
function displayCurrentConditions(forecast) {
  const box = document.getElementById("currentConditions");
  const cw = forecast.current_weather;

  const condition = mapWeatherCode(cw.weathercode);
  const icon = weatherIcon(cw.weathercode);

  box.innerHTML = `
      <h2 class="ui header">Current Conditions</h2>
      <p><strong>${icon} ${condition}</strong></p>
      <p><strong>Temperature:</strong> ${cw.temperature}°F</p>
      <p><strong>Wind:</strong> ${cw.windspeed} mph</p>
      <p><strong>Time:</strong> ${cw.time}</p>
    `;
}

//***************Show JSON data in little cards like the example here: https://cs.uky.edu/~soward/CS316/Examples/React/getForecast.html***************
function displayDailyForecast(daily) {
  const container = document.getElementById("dailyForecast");
  container.innerHTML = "";

  const daysToShow = 6; // ⭐ FIO docs say show next 5 days but cards include current date.
  //Don't want to get docked for not technically having the NEXT 5 days.

  for (let i = 0; i < daysToShow; i++) {
    const date = daily.time[i];
    const high = daily.temperature_2m_max[i];
    const low = daily.temperature_2m_min[i];
    const precip = daily.precipitation_probability_max[i];
    const sunrise = daily.sunrise[i];
    const sunset = daily.sunset[i];
    const weatherCode = daily.weathercode[i];

    const condition = mapWeatherCode(weatherCode);
    const icon = weatherIcon(weatherCode);

    const card = `
        <div class="ui raised card" style="padding: 10px; width: 180px;">
          <div class="content">
            <div class="header">${formatDate(date)}</div>
            <div class="meta">${icon} ${condition}</div>
            <div class="description">
              <p><strong>${high}°F ↓ ${low}°F</strong></p>
              <p>${precip}% chance of storm</p>
              <p>🌅 ${formatTime(sunrise)}</p>
              <p>🌙 ${formatTime(sunset)}</p>
            </div>
          </div>
        </div>
      `;

    container.innerHTML += card;
  }
}

//***************Helper Functions to format json data. I got this working with JSON data first***************
//like in this example: https://cs.uky.edu/~soward/CS316/Examples/JS/fetchW.html
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function formatTime(timeStr) {
  const d = new Date(timeStr);
  return d.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "numeric",
  });
}

// ***************Map Open-Meteo weather variables to human readable text***************
//https://open-meteo.com/en/docs

function mapWeatherCode(code) {
  const map = {
    0: "Clear",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Rain Showers",
    95: "Thunderstorms",
    96: "Thunderstorms Possible",
    99: "Thunderstorms Likely",
  };
  return map[code] || "Unknown";
}
//***************Emojis because I'm a basic bee. 🐝***************
function weatherIcon(code) {
  const icons = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌦️",
    55: "🌧️",
    61: "🌧️",
    63: "🌧️",
    65: "🌧️",
    71: "🌨️",
    73: "🌨️",
    75: "❄️",
    80: "🌦️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️",
  };
  return icons[code] || "❓";
}

//***************Reset all data via page refresh. This seems easiest. ***************
document.getElementById("resetalldata").addEventListener("click", () => {
  location.reload();
});
