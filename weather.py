import requests, pickle, datetime, os
import pandas as pd
import webbrowser


pd.set_option("precision", 2)
pd.options.display.float_format = "{:,.2f}".format
pd.set_option("display.max_columns", 1000)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)

urls = {
    'current_weather' : 'http://api.openweathermap.org/data/2.5/weather',
    '3hourly_forecast' : 'http://api.openweathermap.org/data/2.5/forecast',
}

css_table = '''
<style>

p{
  color:rgb(22, 22, 22);
  font-family: Tahoma, Verdana, Segoe, sans-serif;
  text-align: left;
  font-size: 10px;
  line-height: 11px;
}
table {
    border-collapse: collapse;
    width: 100%;
    border: 1px solid #ddd;
    font-family: Tahoma, Verdana, Segoe, sans-serif;
    font-size: 9px;
  }
  
  table th, table td {
    text-align: left; 
    padding: 3px;
  }
  
  table tr {
    border-bottom: 1px solid #ddd;
  }
  
  table tr.header{
    background-color: #f1f1f1;
  }
  
  table tr.header-b{
    /* Add a grey background color to the table header and on hover */
    background-color: #f1f1f1;
    font-weight: bold;
  }
  
  table tr:hover {
    /* Add a grey background color to the table header and on hover */
    background-color: #f1f1f1;
  }
  
  table select{
      border-color: #f1f1f1;
      width: 100px;
  }


</style>
'''


def download_weather(lat, lon, req_type = 'current_weather', save_p=True):
    params = {
        'appid' : '4a074e58501d60a0b6f7f0f517910faa',
        'lat' : lat,
        'lon' : lon,
        'units' : 'metric',
    }

    url = urls[req_type]

    response = requests.get(url, params)
    if save_p:
        pickle.dump(response, open("weather.p", "wb"))
    return response

def rain_24h(tolerance=5):
    # returns whether there is more than the tolerance (in mm) of rain expected in the next 24hours
    response = pickle.load(open("weather.p", "rb"))
    weather_proj = response.json()['list']
    def _3h(i):
        try:
            x = float(i['rain']['3h'])
        except KeyError:
            x = 0
        return x

    tf_rain = round(sum([_3h(p) for p in weather_proj][:8]), 2)
    rain = True if tf_rain > tolerance else False
    return rain, tf_rain


def print_weather(in_browser=False):
    response = pickle.load(open( "weather.p", "rb" ))
    rj = response.json()

    # print(response.headers)
    # print(rj)

    date_location = {
        'Date': response.headers['Date'],
        'City': rj['city']['name'],
        'lat': rj['city']['coord']['lat'],
        'lon': rj['city']['coord']['lon'],
        'Time zone': int(rj['city']['timezone']) / (60 * 60),
    }

    if response.json()['list']:
        for n, i in enumerate(rj['list']):
            # print(i)
            weather = {
                'Date': datetime.datetime.fromtimestamp(i['dt']).strftime("%d/%m : %Hh"),
                'Weather': i['weather'][0]['main'],
                'Weather description': i['weather'][0]['description'],
                'Temp (C)' : i['main']['temp'],
                'Min temp (C)': i['main']['temp_min'],
                'Max temp (C)': i['main']['temp_max'],
                'Humidity' : f"{i['main']['humidity']}%",
                'Wind speed (kmph)' : float(i['wind']['speed']) * 3.6,
                'Wind gust (kmph)' : float(i['wind']['gust']) * 3.6,
                'Cloud cover' : f"{i['clouds']['all']}%",
                'Visibility (m)': f"{i['visibility']:,.0f}",
                'Probability of rain': f"{i['pop']:,.0%}",

            }
            # some optional ones
            try:
                weather['Last 3h rain (mm)'] = i['rain']['3h']
            except KeyError:
                weather['Last 3h rain (mm)'] = 0

            if n == 0:
                df = pd.DataFrame(columns=weather.keys())

            for key in weather:
                # print(key, ':', weather[key])
                df.loc[weather['Date']] = weather
        df.drop(columns=['Date'], inplace=True)

        

        if in_browser:
            df = df.T
            # alignment and first col size
            css_table_ = css_table
            css_table_ +='''
            <style>
            table th:nth-child(1){
                min-width: 100px;
            }
            </style>'''
            no_cols = len(df.columns) + 2  # 1 index plus index col
            for c in range(no_cols):
                if c > 1:
                    css_table_ +='''
                    <style>
                      table td:nth-child(''' + str(c) + '''), th:nth-child(''' + str(c) + ''') {
                            text-align: right;
                        }
                    </style>
                    '''

            header_text = ''
            for key in date_location:
                header_text += f'<p>{key}:{date_location[key]}</p>'
            html_out = f'{css_table_} {header_text} {df.to_html()}'
            with open('weather.html', 'w') as f:
                f.write(html_out)
            # df.to_html(open('weather.html', 'w'))

            os.system('open weather.html')
            # webbrowser.open_new_tab('weather.html')

        else:
            header_text = ''
            for key in date_location:
                header_text += f'\{key}:{date_location[key]}'
            print(header_text)
            print(df)


def cl_weather():
    '''
    Download weather forcast for 2 spots
    and display in brower or terminal
    '''
    b = input("Open in the browser? y/n : ")
    if b == 'y':
        b = True
    else:
        b = False
    opt = input("1 for Le vesinet, 2 for La Trinité sur Mer: ")
    if opt == '2':
        print("getting weather for La Trinité sur Mer")
        download_weather(47.587491, -3.024695, req_type='3hourly_forecast')
    else:
        print("getting weather for Le Vesinet")
        download_weather(48.90128, 2.12095, req_type='3hourly_forecast')
    print_weather(in_browser=b)





if __name__ == "__main__":
    # download_weather(48.90128, 2.12095, req_type='3hourly_forecast'
    # download_weather(47.587491, -3.024695, req_type='3hourly_forecast')
    # download_weather(48.90128, 2.12095)
    # print_weather(in_browser=True)
    # print(rain_24h())
    cl_weather()