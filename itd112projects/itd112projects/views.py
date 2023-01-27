import matplotlib
import numpy as np
from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import plotly.graph_objects as go



from django.shortcuts import render

def myhome(request):
    return render(request, 'myhome.html')
def geoplot(request):
    return render(request, 'geoplot.html')
def visualization(request):
    return render(request, 'visualization.html')

def geoplot(request):
    df = pd.read_csv('C:/Users/cayen/Desktop/ITD112 Datasetes/abnb.csv')
    df['text'] = df['name'] + '' + df['host_name'] + ', ' + df['neighbourhood'].astype(str)

    fig = go.Figure(data=go.Scattergeo(
        lon=df['longitude'],
        lat=df['latitude'],
        text=df['text'],
        mode='markers',
    ))

    fig.update_layout(
        geo_scope='usa',
    )
    lat_foc = 40.7127837
    lon_foc = -74.0059413

    fig.update_layout(
        title_x=0.5,
        title_y=0.9,
        geo=dict(
            projection_scale=60,  # this is kind of like zoom
            # this will center on the point
            center=dict(lat=lat_foc, lon=lon_foc),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=800,
    )

    # Generate the SVG plot as an HTML div element
    plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        'figure': plot_div,
    }
    return render(request, 'geoplot.html', context)

def visualization(request):
    # sets the default location into None, so it can return the overall calculation
    location = None

    if request.method == 'POST' and 'lugar' in request.POST:
        location = request.POST['lugar']

    # reads the csv file
    dataset = pd.read_csv('C:/Users/cayen/Desktop/ITD112 Datasetes/dengue.csv')

    dataset.rename({'loc': 'location', 'Region': 'region'},
                   axis=1, inplace=True)
    dataset.drop(index=dataset.index[0], inplace=True)

    # creates a new column, "year" thats splits the current date and store it in
    dataset['year'] = dataset['date'].str.split('/', expand=True)[2]
    dataset['year'] = dataset['year'].astype(int)
    dataset['cases'] = dataset['cases'].astype(float)
    dataset['deaths'] = dataset['deaths'].astype(float)

    # captures the unique location of the 'locationn column
    locations = pd.unique(dataset['location'])

    # a function that gets the overall result of case and deaths of a dengue
    def get_result(type):

        total = {}

        for loc in locations:
            location_df = dataset[dataset['location'] == loc]
            total_result = location_df[type].sum()
            total[loc] = total_result

        sorted_total = sorted(
            total.items(), key=lambda item: item[1], reverse=True)

        return sorted_total

    total_case_locations = get_result('cases')
    total_death_locations = get_result('deaths')

    boards = {
        'board_case': total_case_locations[:10],
        'board_deaths': total_death_locations[:10]
    }

    def show_region():

        table = pd.DataFrame(columns=['year', 'cases', 'deaths'])
        for year in pd.unique(dataset['year']):
            if location:
                rows = (dataset['year'] == year) & (dataset['location'] == location)
            else:
                rows = (dataset['year'] == year)
            cases = dataset[rows]['cases'].sum()
            deaths = dataset[rows]['deaths'].sum()
            table = table.append(
                {'year': year, 'cases': cases, 'deaths': deaths},
                ignore_index=True
            )
        sum_of_cases = table['cases'].sum()
        sum_of_deaths = table['deaths'].sum()

        fig = plt.figure()

        plt.plot(table['year'], table['cases'], label='Cases')
        plt.plot(table['year'], table['deaths'], label='Deaths')
        plt.xlabel('Year')
        plt.title(f'Dengue Records Year - 2016 - 2021')
        plt.ylabel('Cases/Deaths')
        plt.legend()

        imgdata = io.StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        context = {
            'data': imgdata.getvalue(),
            'cases': sum_of_cases,
            'deaths': sum_of_deaths,
            'location': 'Overall' if location is None else location,
        }

        return context

    context = show_region()
    context['locations'] = locations

    return render(request, 'visualization.html', {'context': context, 'boards': boards})







