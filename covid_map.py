import pandas as pd
import plotly.express as px
import json

# Load the GeoJSON file
with open("countries.geo.json", "r") as f:
    geojson_data = json.load(f)

# Load the vaccination data
country_vaccinations = pd.read_csv("country_vaccinations.csv")
population_data = pd.read_csv("population_by_country_2020.csv")

# Prepare the vaccination data
vaccination_data_grouped = country_vaccinations.groupby("country").agg({"total_vaccinations": "sum"}).reset_index()

# Create dictionaries for mapping
vaccination_dict = dict(zip(vaccination_data_grouped["country"], vaccination_data_grouped["total_vaccinations"]))
population_dict = dict(zip(population_data["Country (or dependency)"], population_data["Population (2020)"]))

# Add vaccination totals and population to GeoJSON
for feature in geojson_data["features"]:
    country_name = feature["properties"]["name"]
    feature["properties"]["vaccination_total"] = vaccination_dict.get(country_name, None)
    feature["properties"]["Population(2020)"] = population_dict.get(country_name, None)
    if feature["properties"]["vaccination_total"] is not None and feature["properties"]["Population(2020)"] is not None:
        feature["properties"]["vaccination_rate"] = (
            feature["properties"]["vaccination_total"] / feature["properties"]["Population(2020)"]
        )
    else:
        feature["properties"]["vaccination_rate"] = None

# Prepare the data for the map
map_data = pd.DataFrame({
    'name': [feature["properties"]["name"] for feature in geojson_data["features"]],
    'vaccination_total': [feature["properties"].get("vaccination_total") for feature in geojson_data["features"]],
    'population': [feature["properties"].get("Population(2020)") for feature in geojson_data["features"]],
    'vaccination_rate': [feature["properties"].get("vaccination_rate") for feature in geojson_data["features"]],
})

# Create the interactive choropleth map
fig = px.choropleth(
    map_data,
    geojson=geojson_data,
    locations="name",
    featureidkey="properties.name",
    color="vaccination_rate",
    hover_name="name",
    hover_data=["vaccination_total", "population", "vaccination_rate"],
    color_continuous_scale=px.colors.sequential.Plasma,
    projection="natural earth",
    title="COVID-19 Vaccination Rates by Country"
)

fig.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="lightgrey")
fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})

# Show the graph
fig.show()
