# Airpost

## Inspiration
In most of the major cities, the population increases rapidly every year, and the demand for package deliveries is following the same pattern. According to the New York Times, nearly 1.5 million packages are delivered daily in New York City. This is causing many traffic issues and negatively affects our lives. We deserve that the ambulance arrives at the patient location on time and saves his life. To solve this problem and improve our life, we can move most of the daily packages deliveries to fly in the air. If we are able to convert at least 1/3 of the current delivery rate to be done via drones, this will have a significant improvement on the traffic and improve our life. In the USA, AWS wavelength and Verizon provide powerful computing power at the edge with a low latency link between the servers and the devices connected to Verizon network. We can benefit from this by deploying applications to AWS wavelength zones that can exchange data between drones and remote web-based flight controllers in almost real-time.

## What it does
Airpost is an application that allows remote pilots to plan, control, and track drone flights in almost real-time. The main application is deployed to a G4 instance in the AWS wavelength zone inside the Verizon network. This provides powerful computing power for machine learning algorithms at the edge. Also, it provides a low latency link between the drone, the instance, and the web-based remote flight controller. The remote flight controller can be accessed from a mobile, tablet, or laptop web browser, but the device must be connected to the Verizon network.

**Connect and control the Drone**

First, the remote pilot will use the web-based remote flight controller to log in and connect to his drone. Once the connection is established, the remote pilot can type an address to generate a flight path. Also, the pilot can request flight authorization or check airspace advisories for the flight. Then, the remote pilot can start the flight by arming the drone and take off. Then, the pilot can watch the camera stream and pause the autopilot by manually control the drone in certain cases. Also, there will be a map showing the current location of the drone.
 
**How the connection works**

The simulated drone has pixhawk flight controller which can control the drone over MAVLink using python code. Also, the drone is connected to the Verizon network using Monarch Go Pi Hat and ThingSpace. Since the drone has a raspberry pi, we can use Flask-python to create a server to receive remote commands and stream the camera feed. The G4 instance can analyze the video data using machine learning or just pass it to the web-based remote flight controller. The remote pilot will use the web controller to watch the flight and to send commands back to the drone. Finally, our G4 instance can send the data to the AWS region for data analytics or perform further machine learning training.

## How we built it
This demo uses DroneKit-SITL simulator to run a simulated copter based autopilot and communicate with it over MAVProxy. This simulated copter can be controlled from the remote web controller same as the real drone. First, I launched g4dn.2xlarge (Ubuntu Server 20.04 LTS) instance in AWS wavelength NY subnet. Then I assigned a carrier IP address to it and did the following steps:
```
# Update the instance
sudo apt-get update
sudo apt update
```
Install the required packages to run our application and the simulated drone.
```
sudo apt-get install python3-dev python3-opencv python3-wxgtk4.0 python3-pip python3-matplotlib python3-lxml python3-pygame build-essential

sudo pip3 install PyYAML mavproxy dronekit dronekit-sitl

sudo pip3 install pymavlink==2.4.8
```
Now, you can run the simulated drone and share the connection via MAVProxy.
```
dronekit-sitl copter

mavproxy.py --master tcp:127.0.0.1:5760 --out udp:127.0.0.1:14551 --out udp:(127.0.0.1):14550
```
Now, you can write and run python script to control the drone using the web controller. You can clone the code and run it to test the application.
```
git clone https://github.com/khaled-11/airpost
cd airpost
python3 app.py
```
It should work now! Go to your http://carrier-ip:5000 and you will see the login page. You can use Airpost:789555 and test the control panel. If you want to add a domain name and use SSL certificate, point the domain to the caarier IP and follow the following optional steps:
```
# Install Nginx
sudo apt install nginx

# Enable Firewall and allow ports
sudo ufw enable
sudo ufw allow 'Nginx FULL'
sudo ufw allow 5000
sudo ufw allow 'OpenSSH'

# Avoid hash bucket memory
sudo nano /etc/nginx/nginx.conf
# Uncomment # server_names_hash_bucket_size 64;

# Create site available
sudo nano /etc/nginx/sites-available/domain.com

# Add the following
server {
    server_name domain.com www.domain.com;
    listen [::]:443 ssl http2 ipv6only=on;
    listen 443 http2 ssl;
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    location / {
        proxy_pass http://private-ip:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Link it to the enabled sites:
sudo ln -s /etc/nginx/sites-available/domain.com /etc/nginx/sites-enabled/

# Install SSL if needed
sudo apt-get install openssl
sudo mkdir /etc/nginx/ssl/
cd /etc/nginx/ssl/

# Generate request
sudo openssl req -new -newkey rsa:2048 -nodes -keyout domain.key -out domain.csr
```
After you generate the certificate signing request, use it to generate the SSL certificate then copy the certificate to the /etc/nginx/ssl/ folder.


## Challenges we ran into

## Accomplishments that we're proud of

## What we learned

## What's next for Airpost
