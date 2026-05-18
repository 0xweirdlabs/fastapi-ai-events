from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


class ImpactedService(BaseModel):
    id: str
    label: str


class Score(BaseModel):
    method: str
    value: float
    scale: str | None = None


class NetworkExtension(BaseModel):
    category: Literal["network"] = "network"
    interface: str
    topology_element: str
    protocol: str | None = None

    def to_compact_dict(self) -> dict:
        return {"iface": self.interface, "topo": self.topology_element, "proto": self.protocol}


class HostExtension(BaseModel):
    category: Literal["host"] = "host"
    metric: str
    current_value: float
    threshold: float
    unit: str

    def to_compact_dict(self) -> dict:
        return {"metric": self.metric, "val": self.current_value, "thr": self.threshold, "unit": self.unit}


class KubernetesExtension(BaseModel):
    category: Literal["kubernetes"] = "kubernetes"
    cluster: str
    namespace: str
    resource_kind: str
    resource_name: str

    def to_compact_dict(self) -> dict:
        return {"cluster": self.cluster, "ns": self.namespace, "kind": self.resource_kind, "name": self.resource_name}


class DatabaseExtension(BaseModel):
    category: Literal["database"] = "database"
    impacted_services: list[ImpactedService] = Field(default_factory=list)

    def to_compact_dict(self) -> dict:
        return {"svcs": [{"id": s.id, "lbl": s.label} for s in self.impacted_services]}


class ServiceExtension(BaseModel):
    category: Literal["service"] = "service"
    reason: str

    def to_compact_dict(self) -> dict:
        return {"reason": self.reason}


class SecurityExtension(BaseModel):
    category: Literal["security"] = "security"
    security_type: Literal["detection", "cve"]
    attack_type: str | None = None
    source_ip: str | None = None
    target_ip: str | None = None
    affected_user: str | None = None
    cve_id: str | None = None
    affected_software: str | None = None
    affected_version: str | None = None
    scores: list[Score] = Field(default_factory=list)

    def to_compact_dict(self) -> dict:
        return {
            "sec_type": self.security_type,
            "atk": self.attack_type,
            "src_ip": self.source_ip,
            "tgt_ip": self.target_ip,
            "usr": self.affected_user,
            "cve": self.cve_id,
            "sw": self.affected_software,
            "ver": self.affected_version,
            "scores": [{"m": s.method, "v": s.value, "scale": s.scale} for s in self.scores],
        }


class StorageExtension(BaseModel):
    category: Literal["storage"] = "storage"
    storage_type: str
    volume: str | None = None
    capacity_used_pct: float | None = None
    bucket: str | None = None
    endpoint: str | None = None
    pvc_name: str | None = None
    namespace: str | None = None
    storage_class: str | None = None

    def to_compact_dict(self) -> dict:
        return {
            "stor_type": self.storage_type,
            "vol": self.volume,
            "cap_pct": self.capacity_used_pct,
            "bucket": self.bucket,
            "ep": self.endpoint,
            "pvc": self.pvc_name,
            "ns": self.namespace,
            "sc": self.storage_class,
        }


class InfrastructureExtension(BaseModel):
    category: Literal["infrastructure"] = "infrastructure"
    platform: str
    datacenter: str
    resource_type: str
    resource_id: str

    def to_compact_dict(self) -> dict:
        return {"platform": self.platform, "dc": self.datacenter, "res_type": self.resource_type, "res_id": self.resource_id}


class ApplicationExtension(BaseModel):
    category: Literal["application"] = "application"
    application_name: str
    version: str
    environment: str
    pipeline_tool: str | None = None
    pipeline_name: str | None = None
    run_id: str | None = None
    failed_task: str | None = None
    reason: str | None = None

    def to_compact_dict(self) -> dict:
        return {
            "app": self.application_name,
            "ver": self.version,
            "env": self.environment,
            "pipe_tool": self.pipeline_tool,
            "pipe": self.pipeline_name,
            "run_id": self.run_id,
            "task": self.failed_task,
            "reason": self.reason,
        }


AlarmExtension = Annotated[
    Union[
        NetworkExtension,
        HostExtension,
        KubernetesExtension,
        DatabaseExtension,
        ServiceExtension,
        SecurityExtension,
        StorageExtension,
        InfrastructureExtension,
        ApplicationExtension,
    ],
    Field(discriminator="category"),
]
