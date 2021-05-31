#!/usr/bin/env python3

from diagrams import Diagram, Cluster
from diagrams.aws.compute import EKS, ECS, Lambda
from diagrams.aws.database import Aurora, Dynamodb
from diagrams.aws.integration import SQS
from diagrams.aws.ml import Sagemaker
from diagrams.aws.network import CloudFront, VPCRouter, ClientVpn
from diagrams.aws.storage import S3
from diagrams.generic.device import Mobile
from diagrams.generic.os import Ubuntu

if __name__ == "__main__":
    graph_attrs = {
        "pad": "2.0",
        "splines": "ortho",
        "nodesep": "0.65",
        "ranksep": "1",
        "fontname": "Sans-Serif",
        "fontsize": "11",
        "fontcolor": "#2D3436",
    }

    node_attrs = {
        "shape": "box",
        "style": "ortho",
        "fixedsize": "true",
        "width": "1.5",
        "height": "1.5",
        "labelloc": "b",
        "imagescale": "true",
        "fontname": "Sans-Serif",
        "fontsize": "11",
        "fontcolor": "#2D3436",
    }

    edge_attrs = {
        "color": "#7B8894",
    }

    with Diagram("architecture-20210531", show=False, graph_attr=graph_attrs, node_attr=node_attrs, edge_attr=edge_attrs):

        # `main`
        with Cluster("Web service"):
            router = VPCRouter("VPC Router")
            with Cluster("Private VPC") as private_vpc:
                with Cluster("Database Cluster"):
                    db_master = Aurora("Web DB Master")
                    db_master - [Aurora("Web DB RO")]
            with Cluster("Public VPC") as public_vpc:
                source_main = EKS("k8s source : spring boot")
                with Cluster("Main"):
                    workers_main = [ECS("worker1"),
                               ECS("worker2"),
                               ECS("worker3")]
                source_main >> workers_main

                source_recsys = EKS("k8s source : fast api")
                with Cluster("Recommender"):
                    workers_recsys = [ECS("worker1"),
                               ECS("worker2"),
                               ECS("worker3")]
                source_recsys >> workers_recsys

            workers_main >> router >> db_master
            workers_recsys >> router >> db_master

        # `frontend`
        with Cluster("Frontend"):
            bucket_vue = S3("vue project")
            cloudfront = CloudFront("Cloudfront")
            client = Mobile("Web")
            bucket_vue >> cloudfront >> client >> workers_main
            bucket_vue >> cloudfront >> client >> workers_recsys
