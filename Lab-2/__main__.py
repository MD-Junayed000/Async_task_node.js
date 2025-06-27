import pulumi
import pulumi_aws as aws
import os

# Configuration
AMI_ID = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],
    filters=[{"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]}]
).id

# VPC
vpc = aws.ec2.Vpc("async-node-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "async-node-vpc"}
)

# Subnet
subnet = aws.ec2.Subnet("async-node-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": "async-node-subnet"}
)

# Internet Gateway
igw = aws.ec2.InternetGateway("async-node-igw",
    vpc_id=vpc.id,
    tags={"Name": "async-node-igw"}
)

# Route Table
route_table = aws.ec2.RouteTable("async-node-rt",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": igw.id}],
    tags={"Name": "async-node-rt"}
)

# Route Table Association
aws.ec2.RouteTableAssociation("async-node-rt-assoc",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Security Group
sec_group = aws.ec2.SecurityGroup("async-node-sg",
    vpc_id=vpc.id,
    description="Allow ports for async-node services",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5000, "to_port": 5000, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 5672, "to_port": 5672, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 15672, "to_port": 15672, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 6379, "to_port": 6379, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 8081, "to_port": 8081, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}],
    tags={"Name": "async-node-sg"}
)

# SSH Key Pair
key_pair = aws.ec2.KeyPair("async-node-key",
    public_key=open("/root/code/id_rsa.pub").read()
)

# Startup Script Generator
def make_script(service, rabbitmq_ip="", redis_ip=""):
    profiles = f"--profile rabbitmq --profile redis --profile {service}" if service in ["api", "worker", "redisui"] else f"--profile {service}"
    return f"""#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt update -y
apt install -y docker.io git curl
systemctl start docker
usermod -aG docker ubuntu
sleep 20
curl -L https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
cd /home/ubuntu
git clone https://github.com/MD-Junayed000/Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2.git
cd Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2
sed -i 's|<RABBITMQ_IP>|{rabbitmq_ip}|g' docker-compose.yml
sed -i 's|<REDIS_IP>|{redis_ip}|g' docker-compose.yml
echo \"==== STARTUP LOG for {service} ====" >> /home/ubuntu/startup.log
docker-compose {profiles} --profile {service} build >> /home/ubuntu/startup.log 2>&1
docker-compose {profiles} --profile {service} up -d >> /home/ubuntu/startup.log 2>&1
"""

# EC2 Launch Helper
def create_instance(name, script):
    return aws.ec2.Instance(name,
        ami=AMI_ID,
        instance_type="t2.micro",
        subnet_id=subnet.id,
        associate_public_ip_address=True,
        vpc_security_group_ids=[sec_group.id],
        key_name=key_pair.key_name,
        user_data=script,
        tags={"Name": name}
    )

# RabbitMQ EC2
rabbitmq_script = make_script("rabbitmq")
rabbitmq = create_instance("rabbitmq-ec2", rabbitmq_script)

# Redis EC2
redis_script = make_script("redis")
redis = create_instance("redis-ec2", redis_script)

# API EC2
api_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("api", ips[0], ips[1])
)
api = create_instance("api-ec2", api_script)

# Worker1 EC2
worker1_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("worker", ips[0], ips[1])
)
worker1 = create_instance("worker1-ec2", worker1_script)

# Worker2 EC2
worker2_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("worker", ips[0], ips[1])
)
worker2 = create_instance("worker2-ec2", worker2_script)

# Redis UI EC2
redisui_script = pulumi.Output.all(rabbitmq.public_ip, redis.public_ip).apply(
    lambda ips: make_script("redisui", ips[0], ips[1])
)
redisui = create_instance("redisui-ec2", redisui_script)


# Outputs
pulumi.export("API Public IP", api.public_ip)
pulumi.export("RabbitMQ Public IP", rabbitmq.public_ip)
pulumi.export("Redis Public IP", redis.public_ip)
pulumi.export("Worker1 IP", worker1.public_ip)
pulumi.export("Worker2 IP", worker2.public_ip)
pulumi.export("RedisUI Public IP", redisui.public_ip)
