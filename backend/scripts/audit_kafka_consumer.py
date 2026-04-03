#!/usr/bin/env python3
"""Consume limp.audit from Kafka and append rows to Cassandra (limp.audit_logs).

Run as a dedicated process (see docker-compose `audit-consumer`)."""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_consumer")


def main() -> None:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "")
    topic = os.environ.get("KAFKA_AUDIT_TOPIC", "limp.audit")
    group = os.environ.get("KAFKA_CONSUMER_GROUP", "limp-audit-cassandra")
    hosts = [
        h.strip() for h in os.environ.get("CASSANDRA_HOSTS", "").split(",") if h.strip()
    ]
    keyspace = os.environ.get("CASSANDRA_KEYSPACE", "limp")

    if not bootstrap or not hosts:
        logger.error("KAFKA_BOOTSTRAP_SERVERS and CASSANDRA_HOSTS are required")
        sys.exit(1)

    from cassandra.cluster import Cluster
    from kafka import KafkaConsumer

    cluster = Cluster(contact_points=hosts, connect_timeout=30)
    session = cluster.connect()
    session.set_keyspace(keyspace)

    insert_cql = """
        INSERT INTO audit_logs (day, event_id, django_audit_id, user_id, action, model_name, object_id, payload)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[s.strip() for s in bootstrap.split(",")],
        group_id=group,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )

    logger.info("Consuming topic=%s group=%s", topic, group)

    for msg in consumer:
        try:
            v = msg.value
            day = v.get("day") or "unknown"
            eid = uuid.UUID(v["event_id"])
            session.execute(
                insert_cql,
                (
                    day,
                    eid,
                    int(v["django_audit_id"]),
                    int(v["user_id"]) if v.get("user_id") is not None else None,
                    v.get("action"),
                    v.get("model_name"),
                    v.get("object_id"),
                    json.dumps(v.get("payload"), default=str),
                ),
            )
        except Exception:
            logger.exception("Failed to process message")

    cluster.shutdown()


if __name__ == "__main__":
    main()
