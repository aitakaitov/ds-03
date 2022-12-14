#
# *** Demo 4 - Zookeeper
# Create 1 Zookeeper node and N clients.
#

VAGRANTFILE_API_VERSION = "2"
# set docker as the default provider
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'
# disable parallellism so that the containers come up in order
ENV['VAGRANT_NO_PARALLEL'] = "1"
ENV['FORWARD_DOCKER_PORTS'] = "1"
# minor hack enabling to run the image and configuration trigger just once
ENV['VAGRANT_EXPERIMENTAL']="typed_triggers"

unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

# Names of Docker images built:
ZOONODE_IMAGE  = "ds/demo-4/zoonode:0.1"
CLIENT_IMAGE   = "ds/demo-4/client:0.1"
ZOONAVIGATOR_IMAGE = "elkozmon/zoonavigator:latest"
# Subnet to use:
SUBNET = "10.0.1."

BASE_PORT = 5000

# Node definitions
CLIENT  = { :nameprefix => "client-",
            :subnet => SUBNET,
            :ip_offset => 10,
            :image => CLIENT_IMAGE,
            :config => "client/client.cfg"
          }

# Number of clients to start:
NUM_LEVELS = 3
CLIENTS_COUNT = 2 ** NUM_LEVELS - 1

# Number of the root node - e.g. "2" => client-2 is the root
ROOT_NUMBER = 3

# Common configuration
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Before the 'vagrant up' command is started, build docker images:
  config.trigger.before :up, type: :command do |trigger|
    trigger.name = "Build docker images"
    trigger.ruby do |env, machine|
        # --- start of Ruby script ---
        # Build Zoonode image:
        puts "Building Zoonode image:"
        `docker build zoonode -t "#{ZOONODE_IMAGE}"`
        # Build client node image:
        puts "Building client node image:"
        `docker build client -t "#{CLIENT_IMAGE}"`
        # --- end of Ruby script ---
    end
  end

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.ssh.insert_key = false

  # Definition of Zoonode
  config.vm.define "zoonode" do |s|
    s.vm.network "private_network", ip: "#{SUBNET}100"
    s.vm.hostname = "zoonode" 
    s.vm.provider "docker" do |d|
      d.image = ZOONODE_IMAGE
      d.name = "zoonode"
      d.has_ssh = true
    end
    s.vm.post_up_message = "Node 'zoonode' up and running. You can access the node with 'vagrant ssh zoonode'}"
  end

  # Definition of N client nodes
  (1..CLIENTS_COUNT).each do |i|
    port = BASE_PORT + i
    node_ip_addr = "#{CLIENT[:subnet]}#{CLIENT[:ip_offset] + i}"
    node_name = "#{CLIENT[:nameprefix]}#{i}"
    is_root = "False"
    if (i == ROOT_NUMBER) then
        is_root = "True"
    end if
    # Definition of client node
    config.vm.define node_name do |s|
      s.vm.network "private_network", ip: node_ip_addr
      s.vm.hostname = node_name
      s.vm.network "forwarded_port", guest: port, host: port
      s.vm.provider "docker" do |d|
        d.image = CLIENT[:image]
        d.name = node_name
        d.has_ssh = true
        d.env = { "ZOOKEEPER_IP" => "#{SUBNET}100", "NODE_IP" => node_ip_addr, "IS_ROOT" => is_root, "PORT" => "#{port}" }
      end
      s.vm.post_up_message = "Node #{node_name} up and running. You can access the node with 'vagrant ssh #{node_name}'}"
    end
  end
end

# EOF

