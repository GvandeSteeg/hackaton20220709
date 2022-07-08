from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

labels = ["Data Import", "Assembly/Annotation", "Mapping/SNP_Calling", "RNA-Seq"]

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df_2020 = pd.read_csv("2020_results.csv", index_col=0)
df_2021 = pd.read_csv("2021_results.csv", index_col=0)
df_2022 = pd.read_csv("2022_results.csv", index_col=0)
full_df = pd.concat([df_2020, df_2021, df_2022])

data_import_requests_20 = df_2020["Data_Import"].sum()
assembly_20 = df_2020["Assembly"].sum()
annotation_20 = df_2020["Annotation"].sum()
map_20 = df_2020["Mapping"].sum()
snp_20 = df_2020["SNP_Calling"].sum()
rna_seq_20 = df_2020["RNA-seq"].sum()

sizes_20 = [
    data_import_requests_20,
    assembly_20,
    annotation_20,
    map_20,
    snp_20,
    rna_seq_20,
]
pie_df_2020 = pd.DataFrame(list(zip(labels, sizes_20)))

data_import_requests_21 = df_2021["Data_Import"].sum()
assembly_21 = df_2021["Assembly"].sum()
annotation_21 = df_2021["Annotation"].sum()
map_21 = df_2021["Mapping"].sum()
snp_21 = df_2021["SNP_Calling"].sum()
rna_seq_19 = df_2021["RNA-seq"].sum()

sizes_21 = [
    data_import_requests_21,
    assembly_21,
    annotation_21,
    map_21,
    snp_21,
    rna_seq_19,
]
pie_df_2021 = pd.DataFrame(list(zip(labels, sizes_21)))

fig_2020 = px.bar(df_2020, barmode="group", title="2020 SAPP usage per month")
fig_2021 = px.bar(df_2021, barmode="group", title="2021 SAPP usage per month")
line_fig = px.line(
    full_df,
    title="SAPP usage 2020-2022",
    labels={
        "value": "Usage",
    },
)
full_usage_fig = px.bar(full_df, barmode="group", title="SAPP usage per Month 2020-22")
pie_2020_fig = px.pie(pie_df_2020, values=1, names=0, title="2020 pie chart")
pie_2021_fig = px.pie(pie_df_2021, values=1, names=0, title="2021 pie chart")
app.layout = html.Div(
    children=[
        html.H1(children="Rhadamanthys"),
        html.Div(children="Iudicetur cor tuum"),
        dcc.Graph(id="2020_graph", figure=fig_2020),
        dcc.Graph(id="2021_graph", figure=fig_2021),
        dcc.Graph(id="full_usage_graph", figure=full_usage_fig),
        dcc.Graph(id="2020_piechart", figure=pie_2020_fig),
        dcc.Graph(id="2021_piechart", figure=pie_2021_fig),
        dcc.Graph(id="line_graph_sapp_full", figure=line_fig),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
