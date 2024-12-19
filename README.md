# Radiosonde Auto-Rx Notifier  

This project listens for telemetry broadcast by [Radiosonde Auto-Rx](https://github.com/projecthorus/radiosonde_auto_rx) over UDP, processes the data, and sends notifications when radiosondes meet configurable criteria, such as being below a certain altitude and within a specific distance of a configured location.  

## Features  

- **Telemetry Source**: Listens to UDP broadcasts from Radiosonde Auto-Rx.  
- **Filtering**: Configurable thresholds for altitude and distance to filter telemetry data.  
- **Notifications**: Sends notifications through [Apprise](https://github.com/caronc/apprise) to services like Telegram, Email, Slack, etc.  
- **Automatic Data Maintenance**: Purges outdated telemetry data to maintain performance.  
- **Docker-ready**: Easily deploy using the provided Docker image.  

## Getting Started  

### Prerequisites  

- Radiosonde Auto-Rx must be configured to emit **Payload Summary** packets via UDP. Refer to the [Auto-Rx Configuration Guide](https://github.com/projecthorus/radiosonde_auto_rx/wiki/Configuration-Settings#horus-udp-payload-summary-output) for details.  
- Docker and Docker Compose (if running in a containerized environment)  

### Configuration  

On the first run, the application will automatically generate a config.yml file with the default structure in the data directory.

Example structure of the `config.yml`:

```yaml  
listener_location:  
  altitude: 0.0           # Altitude of the listener's location in meters  
  latitude: 0.0           # Latitude of the listener  
  longitude: 0.0          # Longitude of the listener  

notification_thresholds:  
  altitude_meters: 1000.0           # Notify when radiosondes are below this altitude (meters)  
  distance_km: 20.0                 # Notify when radiosondes are within this distance (kilometers)  
  landing_point_timeout_minutes: 5  # Specifies the duration (in minutes) of inactivity after which the landing point is sent. 0 = Disabled

notifications:  
  services:  
    - enabled: true  
      url: 'tgram://<bot_token>/<chat_id>'  

udp_broadcast:  
  enabled: true                  # Enable UDP broadcast listening  
  listen_port: 55673             # UDP port to listen on  
``` 
You can modify the `config.yml` to suit your requirements.

#### Notifications  

Notifications use [Apprise](https://github.com/caronc/apprise). This supports a wide variety of services.  

Example for Telegram:  
```yaml  
notifications:  
  services:  
    - enabled: true  
      url: 'tgram://123456789:ABCDefGhIJklMNOpQRStUvWxYZ1234567/987654321'  
```  

For more details on setting up notification URLs, refer to the [Apprise URL Documentation](https://github.com/caronc/apprise#urls).  

### Running Locally  

Ensure Radiosonde Auto-Rx is broadcasting **Payload Summary** packets. Then, run the script:  

```bash  
python main.py  
```  

### Running with Docker  

The project is Docker-ready and available as a pre-built image at [ch3p4ll3/radiosonde_auto_rx_notifier](https://hub.docker.com/r/ch3p4ll3/radiosonde_auto_rx_notifier).  

#### Docker Compose Example  

To deploy the service using Docker Compose, create a `docker-compose.yaml` file with the following content:  

```yaml  
services:  
  radiosonde_auto_rx_notifier:  
    image: ch3p4ll3/radiosonde_auto_rx_notifier:latest  
    container_name: radiosonde_auto_rx_notifier  
    network_mode: host  
    volumes:  
      - ./data:/code/data  
    environment:  
      - UID=1000  
      - GID=1000  
```  

### Docker Compose with Radiosonde Auto RX
```yaml
services:
  radiosonde_auto_rx:
    container_name: radiosonde_auto_rx
    devices:
      - /dev/bus/usb
    image: ghcr.io/projecthorus/radiosonde_auto_rx:latest
    network_mode: host
    restart: always
    volumes:
      - ~/radiosonde_auto_rx/station.cfg:/opt/auto_rx/station.cfg:ro
      - ~/radiosonde_auto_rx/log/:/opt/auto_rx/log

  radiosonde_auto_rx_notifier:
    image: ch3p4ll3/radiosonde_auto_rx_notifier:latest
    container_name: radiosonde_auto_rx_notifier
    network_mode: host
    volumes:
      - ./notifier_data:/code/data
    environment:
      - UID=1000
      - GID=1000
    restart: unless-stopped

```  

### Steps to Run  

1. Create a directory for your configuration:  
   ```bash  
   mkdir data  
   ```  
2. Run the service with Docker Compose:  
   ```bash  
   docker-compose up -d  
   ```  
3. On the first start, the `config.yml` file will be generated in the `data` directory.  
4. Modify the generated `config.yml` as needed, and restart the service.  

### Logs  

Logs are stored in `data/logs` by default (inside the container). 

## License  

This project is licensed under the GNU GPL v3. See the LICENSE file for details.
