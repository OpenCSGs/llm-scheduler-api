

from kubernetes.client.rest import ApiException
from kubernetes import client
import re
import math
label_selector = '!node-role.kubernetes.io/master'


class KubeResources:
    def __init__(self, kubeClient: client):
        self.__kubeClient = kubeClient
        self.__getNodeData()

    def __getNodeData(self):
        allData = []
        try:
            nodes = self.__kubeClient.list_node()
            for node in nodes.items:
                nodeName = node.metadata.name
                nodeData = NodeData(nodeName, node.status.capacity, self.__parseState(node.status.conditions))
                pod_templates = self.__kubeClient.list_pod_for_all_namespaces(
                    field_selector='spec.nodeName=%s,status.phase!=Failed,status.phase!=Succeeded' % nodeName)

                for template in pod_templates.items:
                    name = template.metadata.name

                    requests = self.__parseResourceRequestsForAllContainers(template.spec.containers)
                    nodeData.addCpuRequest(name, requests["cpu"])
                    nodeData.addMemRequest(name, requests["mem"]/1024)

                    limits = self.__parseResourceLimitsForAllContainers(template.spec.containers)
                    nodeData.addCpuLimit(name, limits["cpu"])
                    nodeData.addMemLimit(name, limits["mem"]/1024)

                allData.append(nodeData)

            self.__nodeData = allData
        except ApiException as e:
            print("Error when attempting to read node data: %s\n" % e)

    def __parseState(self, conditions):
        for c in conditions:
            if c.type == 'Ready':
                if c.status == 'True':
                    return 'Ready'
                else:
                    return 'Not Ready'
        return 'Not Ready'

    def __parseResourceRequestsForAllContainers(self, containers):
        cpuRequests = 0
        memRequests = 0

        for container in containers:
            if container.resources is None or container.resources.requests is None:
                continue

            requests = container.resources.requests
            if "cpu" in requests:
                cpuRequests += Parsers.parseCpuResourceValue(requests["cpu"])
            if "memory" in requests:
                memRequests += Parsers.parseMemoryResourceValue(requests["memory"])

        return {"cpu": cpuRequests, "mem": memRequests}

    def __parseResourceLimitsForAllContainers(self, containers):
        cpuLimits = 0
        memLimits = 0

        for container in containers:
            if container.resources is None or container.resources.limits is None:
                continue

            limits = container.resources.limits
            if "cpu" in limits:
                cpuLimits += Parsers.parseCpuResourceValue(limits["cpu"])
            if "memory" in limits:
                memLimits += Parsers.parseMemoryResourceValue(limits["memory"])

        return {"cpu": cpuLimits, "mem": memLimits}

    def getClusterUsage(self):
        result = {}
        result['totalCpuRequests'] = NodeData.totalCpuRequests
        result['totalCpuLimits'] = NodeData.totalCpuLimits
        result['totalMemRequests'] = NodeData.totalMemRequests/1024
        result['totalMemLimits'] = NodeData.totalMemLimits/1024
        result['totalCpuCapacity'] = NodeData.totalCpuCapacity
        result['totalMemCapacity'] = NodeData.totalMemCapacity/1024
        return result

    def getNodes(self):
        nodes = []
        for node in self.__nodeData:
            nodes.append({'hostname': node.name, 'state': node.state, 'cores': '-', 'gres': '-',
                         'cpus': node.cpu, 'real_memory': int(node.memCapacity/1024)})
        return nodes


class NodeData:
    totalCpuRequests = 0
    totalCpuLimits = 0
    totalMemRequests = 0
    totalMemLimits = 0
    totalCpuCapacity = 0
    totalMemCapacity = 0
    totalUsedMemory = 0
    totalUsedCpu = 0

    def __init__(self, nodename, capacity, state):
        self.cpuRequests = {}
        self.memRequests = {}
        self.cpuLimits = {}
        self.memLimits = {}
        self.name = nodename
        self.state = state
        self.cpu = int(capacity["cpu"])
        self.cpuCapacity = int(capacity["cpu"]) * 1000
        self.memCapacity = Parsers.parseMemoryResourceValue(capacity["memory"])
        self.totalCpuRequests = 0
        self.totalMemRequests = 0
        self.totalCpuLimits = 0
        self.totalMemLimits = 0

        NodeData.totalCpuCapacity += self.cpuCapacity
        NodeData.totalMemCapacity += self.memCapacity

    def addCpuRequest(self, podName, cpuRequest):
        NodeData.totalCpuRequests += cpuRequest
        self.totalCpuRequests += cpuRequest
        self.cpuRequests[podName] = cpuRequest

    def addCpuLimit(self, podName, cpuLimit):
        NodeData.totalCpuLimits += cpuLimit
        self.totalCpuLimits += cpuLimit
        self.cpuLimits[podName] = cpuLimit

    def addMemRequest(self, podName, memRequest):
        NodeData.totalMemRequests += memRequest
        self.totalMemRequests += memRequest
        self.memRequests[podName] = memRequest

    def addMemLimit(self, podName, memLimit):
        NodeData.totalMemLimits += memLimit
        self.totalMemLimits += memLimit
        self.memLimits[podName] = memLimit


class Parsers():
    @staticmethod
    def parseMemoryResourceValue(value):
        match = re.match(r'^([0-9]+)(E|Ei|P|Pi|T|Ti|G|g|Gi|M|Mi|m|K|k|Ki){0,1}$', value)
        if match is None:
            return int(value)
        amount = match.group(1)
        eom = match.group(2).capitalize()

        calc = {
            "Ki": 1,
            "K": 1000,
            "Mi": math.pow(1024, 1),
            "M": 1000000,
            "Gi": math.pow(1024, 2),
            "G": 1000000000
        }

        return int(amount) * calc.get(eom)

    @staticmethod
    def parseCpuResourceValue(value):
        match = re.match(r'^([0-9]+)m$', value)
        if match is not None:
            return int(match.group(1))
        return int(value) * 1000
