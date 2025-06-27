#  Asynchronous Task Processing System using  Pulumi-AWS Multi-EC2 Deployment

##  Project Overview
> Unlike monolithic deployments, this design runs each component in **separate EC2 instances** within a shared VPC , created and managed automatically using Pulumi:
- Node.js + Express + EJS (Frontend API)
- RabbitMQ (Task Queue Broker)
- Redis (Result backend + Pub/Sub)
- Worker Nodes (task processors)
- Redis Commander (UI for live monitoring)
- Multi-EC2 deployment using Pulumi + Docker


All EC2s are Dockerized and orchestrated using `docker-compose` profiles.


##  Architecture Diagram

<div align="center">
  <img src="assets/Service.svg" alt="Implementation Diagram" width="800">
</div>




## How the System is Structured

###  Infrastructure (via `Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2/__main__.py`)

1. **Virtual Private Cloud (VPC) – `10.0.0.0/16`**
   A dedicated Virtual Private Cloud is created to host all components of the system within a secure, logically isolated AWS network.

DNS hostname and resolution support are enabled to allow services to communicate via service names rather than hardcoded IPs, simplifying connectivity across EC2 instances.

2. **Public Subnet – `10.0.1.0/24`**
   A public subnet is defined within the VPC, accommodating up to 256 IP addresses.The flag `map_public_ip_on_launch=True` ensures that each EC2 instance launched within this subnet automatically receives a public IP, enabling direct SSH and HTTP access over the internet.

3. **Internet Gateway**
Allows EC2s to access the internet (e.g., apt, pip, git, Docker).

4. **Route Table**
   - Routes all  outbound internet traffic (`0.0.0.0/0`) through the Internet Gateway.

5. **Security Group Configuration (Firewall)**
A centralized Security Group is configured with both inbound and outbound rules. It allows access to:
     - SSH (22)
     - API Frontend (5000)
     - RabbitMQ: AMQP (5672), UI (15672)
     - Redis UI (8081)
This makes each service publicly accessible for its specific function while retaining security boundaries.

6. **SSH Key Pair**
   - Reads `~/.ssh/id_rsa.pub` to create a key pair for secure login.

7. **Docker Startup Scripts per EC2**
   - Uses a `make_script()` function to:
     - Install Docker & Compose
     - Clone GitHub repo
    - Injects rabbitmq_ip and redis_ip into celeryconfig.py
    - Builds and runs only the necessary service using docker-compose --profile <service>


8. **EC2 Instances Launched:**
A total of six EC2 instances are launched, each assigned a specific responsibility:
   - `rabbitmq-ec2`
   - `redis-ec2`
   - `api-ec2`
   - `worker1-ec2`
   - `worker2-ec2`
   - `redis-ec2`

**The setup should show like this in AWS console:**
![image](https://github.com/user-attachments/assets/c31c31b8-0092-4e71-a949-4ae36f783f9a)

![image](https://github.com/user-attachments/assets/5d1253a1-b321-42c5-82c9-15403f1b213c)




### 🐳 Docker Application (`Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2/docker-compose.yml`)

6-node EC2 stack—one for each service in your Node.js async system:

1. api-ec2 (Express + Socket.IO)

2. rabbitmq-ec2 (RabbitMQ broker + management UI)

3. redis-ec2 (Redis + pub/sub + Redis-Commander)

4. worker1-ec2 (Node.js worker)

5. worker2-ec2 (Node.js worker)

6. redisui-ec2 (Live Redis Commander UI)

---
###  Optimized docker-compose.yml with profiles so each instance only spins up its assigned service:(Use profiles to isolate services)

```bash
version: "3.8"
services:
  api:
    build: .
    profiles: ["api"]
    command: npm run start
    ports:
      - "5000:5000"
    environment:
      RABBIT_URL: amqp://<RABBITMQ_IP>:5672
      REDIS_URL: redis://<REDIS_IP>:6379
    depends_on:
      - rabbitmq
      - redis

  worker:
    build: .
    profiles: ["worker"]
    command: npm run worker
    environment:
      RABBIT_URL: amqp://<RABBITMQ_IP>:5672
      REDIS_URL: redis://<REDIS_IP>:6379
    depends_on:
      - rabbitmq
      - redis

  rabbitmq:
    image: rabbitmq:3-management
    profiles: ["rabbitmq"]
    ports:
      - "5672:5672"
      - "15672:15672"

  redis:
    image: redis:7
    profiles: ["redis"]
    ports:
      - "6379:6379"

  redis-commander:
    image: rediscommander/redis-commander
    profiles: ["redisui"]
    ports:
      - "8081:8081"
    environment:
      REDIS_HOSTS: |
        local:<REDIS_IP>:6379

```



## 📦 Folder Structure

```

Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2/
  ├── __main__.py
  ├── Pulumi.yaml
  ├── Pulumi.dev.yaml
  └── requirements.txt
```

---

##  Step-by-Step Setup (Local + AWS EC2 Deployment) : 


###  1. Prerequisites (on your machine)
Make sure you’ve:

AWS CLI installed 

Pulumi CLI installed 

Docker installed and working

~~ At First from the lab generate the Credentials get the access ID and Secret keys
![image](https://github.com/user-attachments/assets/bcb9200f-93e4-4a6b-986c-55843b40648a)



~~ AWS Configuration from the terminal:
```bash

aws configure # Use credentials from Poridhi Lab or IAM keys

```
<div align="center">
  <img src="https://github.com/user-attachments/assets/10ab64ce-9d44-41cd-908e-cfc972b12b96" alt="image" width="700">
</div>




### 📁 2.Initialize Pulumi Project
```bash
mkdir Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2
cd Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2
pulumi new aws-python

```
For First-time login need to generate tokens:

<div align="center">
  <img src="https://github.com/user-attachments/assets/4e6dccad-d64e-4506-b02e-e59564b47a58" alt="image" width="700">
</div>



**Respond to prompts:**

* Project name: Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2

* Stack: dev (can create your new stack with name of desired)

* AWS region: ap-southeast-1 



![Screenshot 2025-06-03 232744](https://github.com/user-attachments/assets/34455207-428d-4fea-a2d2-64f1aec124ed)



## 3. Create Python Virtual Environment

On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.
-  1. Update your package index
```bash

sudo apt update
```
- 2. Install Python 3 and pip
```bash

sudo apt install -y python3 python3-pip
```
- 3. Install venv module for Python 3
```bash

sudo apt install -y python3-venv
```
>>If you're on Ubuntu 22.04 or later, these commands will work out of the box.

Then create a virtual environment:
```bash

python3 -m venv venv
```
- on Windows
```bash
venv\Scripts\activate
```
- OR # on Linux/Mac
```bash
source venv/bin/activate  
```

Install required packages:
```bash
pip install pulumi pulumi_aws
# or
pip install -r requirements.txt
```
## 4. Define Infrastructure (__main__.py):

Replace __main__.py with this:

***here the modified  docker-compose.yml are pushed into a new repo https://github.com/MD-Junayed000/Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2.git and clone directly into the __main__.py.***

```bash

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

```




### 5. Generating a valid SSH key and fixing the path.
***🔧 Step 1: Generate a Key Pair***

In the terminal (still in /root/code/):
```bash
ssh-keygen -t rsa -b 2048 -f /root/code/id_rsa -N ""
```
- This creates:

-- ✅ /root/code/id_rsa → private key

-- ✅ /root/code/id_rsa.pub → public key

***🔧 Step 2: Confirm the file exists***
```bash
ls -l /root/code/id_rsa.pub
```
should see a line like:
```bash
-rw------- 1 root root 426 Jun 4 10:23 /root/code/id_rsa.pub

```
![Screenshot 2025-06-04 004053](https://github.com/user-attachments/assets/ed907d21-a57b-4606-963d-36e1fd280903)

## 6. Deploy Infrastructure
```bash

pulumi up --yes
```
you should see a output like this:
<div align="center">
  <img src="https://github.com/user-attachments/assets/156566b6-aa64-4c0e-a498-336e49ea4c9d" alt="image" >
</div>


After ~2–3 minutes you’ll have five public IPs—point your browser at:

* ***API: http://<API_IP>:5000***

* ***RabbitMQ UI: http://<RABBIT_IP>:15672 (guest/guest)***

* ***Redis-Commander: http://<REDIS_IP>:8081***

Your two worker nodes will automatically connect, pull tasks from RabbitMQ, publish to Redis, and emit Socket.IO events back through the API node.

## 6. Monitor and Control:
SSH Into EC2 
```bash

ssh -i /root/code/id_rsa ubuntu@<public_ip>
```
🔒 Optional: Fix Permissions

If it still says “unprotected private key”, run:

```bash
chmod 400 /root/code/id_rsa
```
Then try again:

```bash
ssh -i /root/code/id_rsa ubuntu@<public_ip>
```

Then inside EC2 monitor which services are setup and there logs:

```bash

cat /home/ubuntu/startup.log
```
***View Worker Logs (per EC2)***
SSH into one of the worker EC2s to view logs:
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<Worker1 IP>  # worker1
ssh -i ~/.ssh/id_rsa ubuntu@<Worker2 IP>  # worker2
```
Then inside the instance:
```bash
cd ~/Asynchronous-Task-Processing-implemented-in-Node.js-for-Multi-EC2
docker ps                             # Get container ID
docker logs <container_id_or_name>   # See task logs
```
you should see a output like this:
![image](https://github.com/user-attachments/assets/bafc1bb5-39c6-406c-8809-082619a00a78)
![image](https://github.com/user-attachments/assets/7ab59f65-b273-49c4-8cb4-df7a9c6fbeef)



##  What Happens Behind the Scenes

- **Pulumi provisions** a full cloud network and injects broker/result IPs into each EC2.
- **Each EC2** builds only its required service with Docker Compose profiles.
- **Workers connect** to RabbitMQ on a separate instance and store results in Redis on another instance.
- **API web UI** Submit a task on the API UI and watch “Live Task Updates” stream in via Socket.IO.



##  Cleanup AWS Resources
```bash
pulumi destroy --yes
```
Pulumi will tear down the VPC, all EC2s, and related networking.
