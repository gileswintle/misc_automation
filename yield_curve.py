from pandas_datareader.data import DataReader as dr
import pandas as pd
import numpy as np
import plotly.express as px
import datetime, requests
from datetime import date, timedelta

from time_series_utils import *

import plotly
plotly.io.orca.config.executable = '/Users/gileswintle/Dropbox/Docs/Python/cassian_formatting/venv/lib/python3.8/site-packages/orca/orca.py'

pd.set_option("precision", 2)
pd.options.display.float_format = "{:,.0f}".format
pd.set_option("display.max_columns", 1000)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)

'''
https://www.econdb.com/main-indicators?freq=Q&country=FR&transform=2&dateStart=2019-01-01&dateEnd=2021-01-01&view=country-profile
EU open data portal
https://data.europa.eu/euodp/data/apiodp/

quandl API key: eJ25DEW-a4neCuhsFAVr

Banque de France:
Client secret: J1xX0hP7sD2yO3hM8iX2gD8dU1wJ5aH4vK6fF6cO5vT4pS0xL2
Client id: e9deeee0-7c17-44bf-a0c9-60296e11c51b

'''

pd.set_option("precision", 2)
pd.options.display.float_format = "{:,.2f}".format
pd.set_option("display.max_columns", 10000)
pd.set_option("display.max_rows", 10000)
pd.set_option("display.width", 10000)

BOF_KEY = 'e9deeee0-7c17-44bf-a0c9-60296e11c51b'




def yield_curve_us(start='2020-01-02', end=False):
    if end == False:
        end = start
    syms = ['DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS10']
    df = dr(syms, 'fred', start=start, end=end)
    if df.empty:
        return [np.nan]
    names = dict(zip(syms, ['1yr', '2yr', '3yr', '5yr', '10yr']))
    df = df.rename(columns=names)
    df = df.interpolate()
    if start == end:
        return df.iloc[0, :]
    else:
        return df


def us_yield_curve_range(date):
    df = pd.DataFrame(columns=['1yr', '2yr', '3yr', '5yr', '10yr'])
    date_ = datetime.datetime.fromisoformat(date)
    curves = [date_, date_ - datetime.timedelta(days=90), date_ - datetime.timedelta(days=180), date_ - datetime.timedelta(days=360)]
    curves = [d.strftime("%Y-%m-%d") for d in curves]
    names = [f't={date}', 't-90 days', 't-180 days', 't-360 days']
    for curve, name in zip(curves, names):
        cur_curve = [np.nan]
        while pd.isnull(cur_curve[0]): #keep running is API returns and error, wind back one day if no values for the date chosen
            try:
                cur_curve = yield_curve_us(start=curve)
                curve = datetime.datetime.fromisoformat(curve) - datetime.timedelta(days=1)
                curve = curve.strftime("%Y-%m-%d")
            except KeyError:
                pass
        df.loc[name] = cur_curve
    return df

def us_yield_curve_range_chart(date=False, save_file=False):
    if date == False:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    df = us_yield_curve_range(date)
    print(df)
    fig = px.line(df.T, render_mode="svg")
    fig.update_layout(
        title="US treasury yield curve",
        xaxis_title="Maturity",
        yaxis_title="YTM %",
        legend_title="",
        yaxis_tickformat=',.1f',
    )
    if save_file:
        fig.update_layout(

            # title="",
            autosize=False,
            width=750,
            height=460,
        )

        fig.write_image(save_file)
    else:
        fig.show()

def cpi_fr(start='2020-01-02'):
    df = dr('ticker=CPIFR', 'econdb', start=start)
    print(df)

def ir_10y_fr(start='2020-01-02'):
    df = dr('ticker=Y10YDFR', 'econdb', start=start)
    print(df)

def house_prices(start='2018-01-01'):
    df = dr('ticker=HOUFR', 'econdb', start=start)
    df = to_day_ind(df, start=start)
    df_ = dr('ticker=HOUUK', 'econdb', start=start)
    df_ = to_day_ind(df_, start=start)
    df.index.name = 'Date'
    df.columns=['FR']
    df['UK'] = df_.iloc[:,0]
    df_ = dr('ticker=HOUUS', 'econdb', start=start)
    df_ = to_day_ind(df_, start=start)
    df['US'] = df_.iloc[:, 0]

    df = rebase_ind(df, col_nos=[0, 1, 2])
    fig = px.line(df, x=df.index, y=['FR', 'UK', 'US'], render_mode="svg")
    fig.show()

def econdb(start='2018-01-01', tickers=['HOUFR', 'HOUUK', 'HOUUS'], names=['FR', 'UK', 'US'], title='House prices', rebase_data=True, create_index=False, inplace=True, divisor=100):
    df_out = pd.DataFrame()
    col_nos = range(0,len(tickers))
    for ticker, name in zip(tickers, names):
        df = dr(f'ticker={ticker}', 'econdb', start=start)
        df = to_day_ind(df, start=start)
        df_out[name] = df.iloc[:,0]
    df_out.index = df.index
    df_out.index.name = 'Date'
    df_out.dropna(inplace=True)
    if create_index:
        df_out = create_ind(df_out, col_nos=col_nos, inplace=inplace, divisor=divisor)
    if rebase_data and create_index == False:
        df_out = rebase_ind(df_out, col_nos=col_nos, inplace=inplace)
    fig = px.line(df_out, x=df_out.index, y=names, render_mode="svg", title=title)
    fig.update_layout(legend=dict(
        title=''
    ))
    fig.show()
    return df_out

def euro_yield_curve():
    a = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/irt_euryld_d.tsv.gz&unzip=true'
    b = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/teimf060.tsv.gz&unzip=true'

    yc = requests.get(a)
    print(yc.text)
    with open('temp.csv', 'w') as f:
        f.write(yc.text)
    df = pd.read_csv('temp.csv', sep='\t', )
    print(df)


def covid_data():
    today = date.today()
    yesterday = today - timedelta(days=500)
    countries = ['france', 'united-kingdom', 'germany', 'italy', 'poland', 'united-states']
    '''NEED TO ADJUST FOR POPULATION'''
    df_out = pd.DataFrame()
    for c, country in enumerate(countries):
        print('getting: ', country)
        endpoint = f"https://api.covid19api.com/country/{country}/status/confirmed"
        params = {"from": str(yesterday), "to": str(today)}
        response = requests.get(endpoint, params=params).json()
        try:
            ind = [day.get("Date", 0) for day in response]
        except AttributeError:
            print (response)
            break
        cases_lst = [day.get("Cases", 0) for day in response]
        df = pd.DataFrame(data=cases_lst, index=ind, columns=['A'])
        df = df.groupby(df.index).sum()
        df_out[country.title()] = df['A']

    cols = df_out.columns
    fig = px.line(df_out, x=df_out.index, y=cols, render_mode="svg", title='Covid confirmed cases')
    fig.update_layout(legend=dict(
        title=''
    ))
    fig.show()

    print(df_out)


def BOF_catalog():
    endpoint = f"https://api.webstat.banque-france.fr/webstat-en/v1/catalogue?format=json&client_id=e9deeee0-7c17-44bf-a0c9-60296e11c51b"
    params = {"accept": 'application/json'}
    response = requests.get(endpoint, params=params).json()
    df = pd.DataFrame(response)
    df.to_excel('bof_catalog.xlsx')
    print(df)

def BOF_cat_series(category):
    endpoint = f'https://api.webstat.banque-france.fr/webstat-en/v1/catalogue/{category}?format=json&client_id={BOF_KEY}'
    params = {"accept": 'application/json'}
    response = requests.get(endpoint, params=params).json()
    df = pd.DataFrame(response)
    df.to_excel('bof_cat_series.xlsx')
    print(df)


def banque_de_france(category='FM', series='FM.D.FR.EUR.FR2.BB.FRMOYTEC1.HSTA', start='2020-06-30', end='2020-06-30'):
    df = pd.DataFrame(columns=['Value'])
    endpoint = f'https://api.webstat.banque-france.fr/webstat-en/v1/data/{category}/{series}?format=json&detail=dataonly&startPeriod={start}&endPeriod={end}&client_id={BOF_KEY}'

    params = {"accept": 'application/json'}
    response = requests.get(endpoint, params=params).json()
    series = response['seriesObs']

    for i in series:
        series = i['ObservationsSerie']
        obs = series['observations']
        for ob in obs:
            entry = ob['ObservationPeriod']
            df.loc[entry['periodFirstDate']] = entry['value']
    if df.empty:
        return np.nan
    if start == end:
        return df.iloc[0, 0]
    else:
        return df

def fr_yield_curve(date):
    codes = ['FM.D.FR.EUR.FR2.BB.FRMOYTEC1.HSTA', 'FM.D.FR.EUR.FR2.BB.FRMOYTEC2.HSTA', 'FM.D.FR.EUR.FR2.BB.FRMOYTEC3.HSTA', 'FM.D.FR.EUR.FR2.BB.FRMOYTEC5.HSTA',
             'FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA']
    names = ['1yr', '2yr', '3yr', '5yr', '10yr']
    rates = []
    for code, name in zip(codes, names):
        rates.append(banque_de_france(category='FM', series=code, start=date, end=date))
    return names, rates

def fr_yield_curve_range(date):
    df = pd.DataFrame(columns=['1yr', '2yr', '3yr', '5yr', '10yr'])
    date_ = datetime.datetime.fromisoformat(date)
    curves = [date_, date_ - datetime.timedelta(days=90), date_ - datetime.timedelta(days=180), date_ - datetime.timedelta(days=360)]
    curves = [d.strftime("%Y-%m-%d") for d in curves]
    names = [f't={date}', 't-90 days', 't-180 days', 't-360 days']
    for curve, name in zip(curves, names):
        cur_curve = [np.nan]
        while pd.isnull(cur_curve[0]): #keep running is API returns and error, wind back one day if no values for the date chosen
            try:
                _, cur_curve = fr_yield_curve(curve)
                curve = datetime.datetime.fromisoformat(curve) - datetime.timedelta(days=1)
                curve = curve.strftime("%Y-%m-%d")
            except KeyError:
                pass
        df.loc[name] = cur_curve
    return df

def fr_yield_curve_range_chart(date=False, save_file=False):
    if date == False:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    df = fr_yield_curve_range(date)
    # print(df)
    fig = px.line(df.T, render_mode="svg")
    fig.update_layout(
        title="French treasury yield curve",
        xaxis_title="Maturity",
        yaxis_title="YTM %",
        legend_title="",
        yaxis_tickformat=',.1f',
    )

    if save_file:
        fig.update_layout(

            # title="",
            autosize=False,
            width=750,
            height=460,
        )

        fig.write_image(save_file)
    else:
        fig.show()





    # conn = http.client.HTTPSConnection("api.webstat.banque-france.fr")
    #
    # headers = { 'accept': "application/json" }
    #
    # conn.request("GET", "/webstat-en/v1/catalogue?client_id=e9deeee0-7c17-44bf-a0c9-60296e11c51b&format=json", headers=headers)
    #
    # res = conn.getresponse()
    # data = res.read()
    #
    # print(data.decode("utf-8"))


if __name__ == "__main__":
    # econdb(start='2011-01-01', tickers=['CPIFR', 'CPIUK', 'CPIUS'], names=['FR', 'UK', 'US'], title='CPI', rebase_data=False, create_index=True, inplace=True, divisor=10000)
    # econdb()
    # euro_yield_curve()
    # covid_data()
    # BOF_cat_series('BLS')
    # banque_de_france()
    # ir_10y_fr()
    # print(yield_curve_us('2021-03-08'))
    # euro_yield_curve()
    fr_yield_curve_range_chart(save_file="fr_yc.svg")
    us_yield_curve_range_chart(save_file="us_yc.svg")