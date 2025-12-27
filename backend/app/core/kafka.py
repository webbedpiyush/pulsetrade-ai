"""
Kafka configuration for Confluent Cloud.

Handles producer/consumer setup with SASL/SSL authentication.
"""
import os
from confluent_kafka import Producer, Consumer
from functools import lru_cache


def get_kafka_config() -> dict:
    """Get base Kafka configuration for Confluent Cloud."""
    return {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': os.getenv('KAFKA_API_KEY'),
        'sasl.password': os.getenv('KAFKA_API_SECRET'),
    }


@lru_cache()
def get_producer() -> Producer:
    """
    Get singleton Kafka producer.
    
    Uses lru_cache to ensure only one producer instance exists.
    """
    config = get_kafka_config()
    config.update({
        'client.id': 'pulsetrade-ingestor',
        'acks': 'all',
    })
    return Producer(config)


def get_consumer(group_id: str = 'ai-processor-group') -> Consumer:
    """
    Get Kafka consumer for a specific consumer group.
    
    Args:
        group_id: Consumer group ID for offset tracking
    
    Returns:
        Configured Consumer instance
    """
    config = get_kafka_config()
    config.update({
        'group.id': group_id,
        'auto.offset.reset': 'latest',
        'enable.auto.commit': True,
    })
    return Consumer(config)


# Topic names
TOPIC_CRYPTO_TRADES = 'crypto-trades'
TOPIC_ALERTS = 'crypto-alerts'
