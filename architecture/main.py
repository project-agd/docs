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

    with Diagram("architecture", show=False, graph_attr=graph_attrs, node_attr=node_attrs, edge_attr=edge_attrs):

        # Queue
        recommend_system_api_queue = SQS("Recommendation API Queue")
        eks_to_dynamodb_queue = SQS("Processing Queue")

        # `main`
        with Cluster("Web service"):
            router = VPCRouter("VPC Router")
            with Cluster("Private VPC") as private_vpc:
                with Cluster("Database Cluster"):
                    db_master = Aurora("Web DB Master")
                    db_master - [Aurora("Web DB RO")]
            with Cluster("Public VPC") as public_vpc:
                source = EKS("k8s source : spring boot")
                with Cluster("Event Workers"):
                    workers = [ECS("worker1"),
                               ECS("worker2"),
                               ECS("worker3")]
                source >> workers

            workers >> router >> db_master
        workers >> recommend_system_api_queue
        workers >> eks_to_dynamodb_queue

        # `rec_sys`
        with Cluster("Recommendation API") as rec_sys_vpc:
            cvpn = ClientVpn("ec2 client VPN")
            s3_model = S3("Trained Model")
            with Cluster("Private VPC"):
                with Cluster("Train & Optimize"):
                    dynamodb = Dynamodb("Training Data")
                    sagemaker_training = Sagemaker("Training")
                with Cluster("Deploy"):
                    sagemaker_hosting = Sagemaker("Hosting")
                    rec_sys_workers = [
                        Lambda("API with golang"),
                        Lambda("API with golang"),
                        Lambda("API with golang"),
                    ]
                with Cluster("Processing"):
                    processing_workers = [
                        Lambda("processing worker"),
                        Lambda("processing worker"),
                        Lambda("processing worker"),
                    ]

            dynamodb >> sagemaker_training >> s3_model >> sagemaker_hosting
            recommend_system_api_queue >> rec_sys_workers >> sagemaker_hosting
            eks_to_dynamodb_queue >> processing_workers >> dynamodb

        # `local`
        with Cluster("Local RTX3080 Linux"):
            local_linux = Ubuntu("Local training PC")
            local_linux >> cvpn >> dynamodb
            local_linux >> s3_model

        # `frontend`
        with Cluster("Frontend"):
            bucket_vue = S3("vue project")
            cloudfront = CloudFront("Cloudfront")
            client = Mobile("Web")
            bucket_vue >> cloudfront >> client >> workers
