from diagrams import Diagram, Cluster
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.compute import ContainerInstances
from diagrams.azure.web import AppServices
from diagrams.azure.database import DatabaseForPostgresqlServers
from diagrams.custom import Custom

from pathlib import Path

'''
Docs:
    https://diagrams.mingrammer.com/docs/nodes/azure
    https://www.graphviz.org/documentation/
'''

project_root = Path(__file__).resolve().parents[1]
output_filepath = f"{project_root}/src/skyviz/static/architecture_diagram"
adsb_exchange_logo = f"{project_root}/src/skyviz/static/adsb_exchange_logo.png"

graph_attr = {
    "fontcolor": "#BEBEBE",
    "fontsize": "38",
    "bgcolor": "transparent",  # #17202A
    "pad": "0.75",
    "labelloc": "t",
    # "nodesep": "1.2",
    # "ranksep": "0.8",
}

node_attr = {
    "fontcolor": "#EEEEEE",
}

cluster_attr = {
    "fontcolor": "transparent",
    "labeljust": "1",
    "margin": "25",
    "pencolor": "transparent",
    "bgcolor": "transparent",
}

edge_attr = {
    "penwidth": "2.0",
}

with Diagram(filename=output_filepath, graph_attr=graph_attr, node_attr=node_attr,
             edge_attr=edge_attr, show=False):
    with Cluster("Data Flow", graph_attr=cluster_attr):
        adsb_api = Custom("ADS-B Exchange API", adsb_exchange_logo)
        container_app = ContainerInstances("Python Container")
        postgres = DatabaseForPostgresqlServers("Postgres DB")
        web_app = AppServices("Streamlit Web App UI")
    
    log_analytics = LogAnalyticsWorkspaces("Log Analytics Alerts")

    adsb_api >> container_app >> postgres >> web_app
    [container_app, postgres, web_app] >> log_analytics
