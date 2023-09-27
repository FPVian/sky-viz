from diagrams import Diagram, Edge, Cluster
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.compute import AppServices, ContainerInstances
from diagrams.azure.web import AppServiceCertificates, AppServicePlans, AppServices
from diagrams.azure.database import DatabaseForPostgresqlServers
from diagrams.generic.compute import Rack

'''
Docs:
    https://diagrams.mingrammer.com/docs/nodes/azure
    https://www.graphviz.org/documentation/
'''


filepath = "src/skyviz/static/architecture-diagram"

graph_attr = {  # https://diagrams.mingrammer.com/docs/guides/diagram
    "fontsize": "45",
    "bgcolor": "#17202A",  # "transparent",
    "pad": "0.75",
}

node_attr = {
            # "fixedsize": "True",  # delete
            "fontcolor": "#EEEEEE",
            # "fontname": "calibri",
            # "fontsize": "13.0",
            # "height": "1.0",
            # "imagepos": "tc",
            # "imagescale": "True",
            # "labelloc": "b",
            # "shape": "rectangle",
            # "style": "filled",
            # "width": "1.0",
}

cluster_attr = {
    "fontcolor": "#EEEEEE",
    # "fontsize": "12.0",
    # "fontname": "calibri",
    # "labeljust": "1",
    # "labelloc": "b",  # ?
    "margin": "25",  # 30.0?
    # "style": "rounded",
    # "pencolor": "#AEB6BE",
    "bgcolor": "transparent",
}

with Diagram("SkyViz Architecture", filename=filepath, show=False, graph_attr=graph_attr, node_attr=node_attr):
    with Cluster("Data Flow", graph_attr=cluster_attr):
        adsb_api = Rack("ADS-B Exchange API", fillcolor="lightblue", style="filled")
        container_app = ContainerInstances("Python ETL Container")
        postgres = DatabaseForPostgresqlServers("Postgres DB")
        web_app = AppServices("Streamlit Web App UI")
    
    log_analytics = LogAnalyticsWorkspaces("Log Analytics Alerts")

    adsb_api >> container_app >> postgres >> web_app
    [container_app, postgres, web_app] >> log_analytics
