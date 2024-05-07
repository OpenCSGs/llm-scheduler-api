from fastapi import APIRouter
from k8s.client import client

router = APIRouter(prefix="/k8s/workload")

@router.get("/")
def index():
    return "Workload Index"

@router.get("/namespaces")
def namespaces():
    api = client.CoreV1Api()
    data = []
    namespaces = api.list_namespace()

    # namespace list parsing logic
    for item in namespaces.items:
        data.append(item.metadata.name)

    return data


@router.get("/deployments/")
def deployments(namespace: str | None = None):
    """Get deployments, Pods and logs Meta data.
    Note:
        for example: http://api_server:port/workload/deployments/?namespace=develop
    """

    api = client.AppsV1Api()
    data = []
    try:
        deployments = api.list_deployment_for_all_namespaces(watch=False)
        for deployment in deployments.items:
            deploymentdata = {}
            deploymentdata['images'] = []
            if namespace == deployment.metadata.namespace:
                deploymentdata['name'] = deployment.metadata.name
                deploymentdata['namespace'] = deployment.metadata.namespace
                deploymentdata['labels'] = deployment.metadata.labels
                for container in deployment.spec.template.spec.containers:
                    deploymentdata['images'].append(container.image)
                deploymentdata['status'] = {
                    'replicas': deployment.status.replicas,
                    'available_replicas': deployment.status.available_replicas,
                    'ready_replicas': deployment.status.ready_replicas,
                    'unavailable_replicas': deployment.status.unavailable_replicas,
                    'updated_replicas': deployment.status.updated_replicas
                }
                data.append(deploymentdata)
            if not namespace:
                deploymentdata['name'] = deployment.metadata.name
                deploymentdata['namespace'] = deployment.metadata.namespace
                deploymentdata['labels'] = deployment.metadata.labels
                for container in deployment.spec.template.spec.containers:
                    deploymentdata['images'].append(container.image)
                deploymentdata['status'] = {
                    'replicas': deployment.status.replicas,
                    'available_replicas': deployment.status.available_replicas,
                    'ready_replicas': deployment.status.ready_replicas,
                    'unavailable_replicas': deployment.status.unavailable_replicas,
                    'updated_replicas': deployment.status.updated_replicas
                }
                data.append(deploymentdata)
        return data
    except Exception as e:
        response = {'error': f'Exception. Details: {e}.'}
        return response, 500


@router.get("/pods/")
def pods(namespace: str | None = None):
    api = client.CoreV1Api()
    data = []
    try:
        pods = api.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            poddata = {}
            if namespace == pod.metadata.namespace:
                poddata['name'] = pod.metadata.name
                poddata['pod_ip'] = pod.status.pod_ip
                poddata['node_ip'] = pod.status.host_ip
                poddata['node_name'] = pod.spec.node_name
                poddata['namespace'] = pod.metadata.namespace
                poddata['status'] = pod.status.phase
                poddata['start_time'] = pod.status.start_time
                poddata['labels'] = pod.metadata.labels
                data.append(poddata)
            if not namespace:
                poddata['name'] = pod.metadata.name
                poddata['pod_ip'] = pod.status.pod_ip
                poddata['node_ip'] = pod.status.host_ip
                poddata['node_name'] = pod.spec.node_name
                poddata['namespace'] = pod.metadata.namespace
                poddata['status'] = pod.status.phase
                poddata['start_time'] = pod.status.start_time
                poddata['labels'] = pod.metadata.labels
                data.append(poddata)
        return data

    except Exception as e:
        response = {'error': f'Exception. Details: {e}.'}
        return response, 500

@router.get("/pod/logs/")
def pod_logs(pod: str, namespace: str, tail_lines: str):
    """Get pod logs
        for example: http://api_server:port/workload/pod/logs/?namespace=xxx&pod=xxx&tail_lines=5
    """
    api = client.CoreV1Api()
    if not pod or not namespace or not tail_lines:
        response = {'error': 'Incorrect request arguments.'}
        return response, 400

    try:
        logs = api.read_namespaced_pod_log(
            name=pod,
            namespace=namespace,
            tail_lines=int(tail_lines),
            timestamps=True
        )
        return logs
    except Exception as e:
        response = {'error': f'Exception. Details: {e}.'}
        return response, 500

@router.get("/services/")
def list_service(namespace: str | None = None):
        api_instance = client.CoreV1Api()
        services = []
        try:
            response = api_instance.list_service_for_all_namespaces()
            for service in response.items:
                if namespace == service.metadata.namespace:
                    services.append({
                    'uid': service.metadata.uid,
                    'name': service.metadata.name,
                    'annotations': service.metadata.annotations,
                    'namespace': service.metadata.namespace,
                    'labels': service.metadata.labels,
                    'created_at': service.metadata.creation_timestamp,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip,
                    'external_ip': service.spec.external_i_ps,
                    'ports': [
                        {
                            'name': port.name,
                            'node_port': port.node_port,
                            'port': port.port,
                            'protocol': port.protocol,
                            'target_port': port.target_port
                        } for port in service.spec.ports
                    ]
                })
                if not namespace:
                    services.append({
                    'uid': service.metadata.uid,
                    'name': service.metadata.name,
                    'annotations': service.metadata.annotations,
                    'namespace': service.metadata.namespace,
                    'labels': service.metadata.labels,
                    'created_at': service.metadata.creation_timestamp,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip,
                    'external_ip': service.spec.external_i_ps,
                    'ports': [
                        {
                            'name': port.name,
                            'node_port': port.node_port,
                            'port': port.port,
                            'protocol': port.protocol,
                            'target_port': port.target_port
                        } for port in service.spec.ports
                    ]
                })
            return services
        except Exception as e:
            response = {'error': f'Exception. Details: {e}.'}
            return response, 500


from pydantic import BaseModel
import base64
import os.path
from kubernetes import utils


class Item(BaseModel):
    data: str

@router.post("/workloads/")
def workloads(item: Item):
        # api_instance = client.AppsV1Api()
        k8s_client = client.ApiClient()

        try:
            decoded = base64.b64decode(item.data.split(",")[1])
            dirname = os.path.join(os.path.dirname(__file__), '../../../', 'uploads')
            filename = item.data.split(",")[2].split(":")[1]

            output_file = open(os.path.join(dirname, filename), 'wb')
            output_file.write(decoded)
            output_file.close()

            utils.create_from_yaml(k8s_client, os.path.join(dirname, filename))
            os.remove(os.path.join(dirname, filename))

            return { "succeed": "true" }
            
        except Exception as e:
            response = {'error': f'Exception. Details: {e}.'}
            return response, 500