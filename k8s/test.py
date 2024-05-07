from client import client
from nodestat import KubeResources

if __name__ == "__main__":
    resource = KubeResources(client.CoreV1Api())
    print(resource.getNodes())
