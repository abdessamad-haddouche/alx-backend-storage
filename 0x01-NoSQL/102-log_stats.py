#!/usr/bin/env python3
"""
Log stats - new version
"""
from pymongo import MongoClient


if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    logs_collection = client.logs.nginx

    total_logs = logs_collection.count_documents({})
    print(f"{total_logs} logs")

    methods = logs_collection.aggregate([
        {"$group": {"_id": "$method", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    print("Methods:")
    for method in methods:
        print(f"    method {method['_id']}: {method['count']}")

    status_checks = logs_collection.count_documents({"method": "GET", "path": "/status"})
    print(f"{status_checks} status check")

    ips = logs_collection.aggregate([
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    print("IPs:")
    for ip in ips:
        print(f"    {ip['_id']}: {ip['count']}")

