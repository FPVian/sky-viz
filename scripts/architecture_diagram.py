from diagrams import Diagram, Edge
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.compute import AppServices, ContainerInstances
from diagrams.azure.web import AppServiceCertificates, AppServicePlans, AppServices
from diagrams.azure.database import DatabaseForPostgresqlServers

'''
Docs:
    https://diagrams.mingrammer.com/docs/nodes/azure
    https://www.graphviz.org/documentation/
'''


filepath = "src/skyviz/static/architecture-diagram"

graph_attr = {  # https://diagrams.mingrammer.com/docs/guides/diagram
    "fontsize": "45",
    "bgcolor": "transparent"
}

with Diagram("SkyViz Architecture", filename=filepath, show=False, graph_attr=graph_attr):
    flight_data = "website"
    container_app = ContainerInstances("Python Container")
    postgres = DatabaseForPostgresqlServers()
    web_app = AppServices("Streamlit Web App")
    log_analytics = LogAnalyticsWorkspaces("Log Analytics")

    container_app >> Edge() >> postgres >> web_app  # last edge is bidirectional
    [container_app, postgres, web_app] >> log_analytics
