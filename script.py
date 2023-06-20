import os
import subprocess
import sys


def check_docker_installed():
    try:
        subprocess.check_output(['docker', '--version'])
        subprocess.check_output(['docker-compose', '--version'])
    except FileNotFoundError:
        return False
    return True


def install_docker():
    print("Installing Docker and Docker Compose...")
    subprocess.run(['curl', '-fsSL', 'https://get.docker.com', '-o', 'get-docker.sh'])
    subprocess.run(['sudo', 'sh', 'get-docker.sh'], check=True)
    subprocess.run(['sudo', 'usermod', '-aG', 'docker', os.getlogin()], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', 'docker'], check=True)
    subprocess.run(['sudo', 'systemctl', 'start', 'docker'], check=True)
    subprocess.run(['sudo', 'curl', '-L', 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)', '-o', '/usr/local/bin/docker-compose'], check=True)
    subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/docker-compose'], check=True)
    subprocess.run(['docker', 'compose', '--version'], check=True)


def create_wordpress_site(site_name):
    print("Creating WordPress site...")
    os.makedirs(site_name, exist_ok=True)
    os.chdir(site_name)

    docker_compose = f"""
version: '3'
services:
  db:
    image: mysql:5.7
    volumes:
      - db_data:/var/lib/mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: wordpress
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress

  wordpress:
    depends_on:
      - db
    image: wordpress
    ports:
      - "8000:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
volumes:
  db_data:
"""
    with open('docker-compose.yml', 'w') as file:
        file.write(docker_compose)

    subprocess.run(['docker-compose', 'up', '-d'], check=True)


def add_hosts_entry(site_name):
    print("Adding /etc/hosts entry...")
    hosts_entry = f"127.0.0.1 {site_name}"
    with open('/etc/hosts', 'a') as file:
        file.write(hosts_entry)


def open_site_in_browser(site_name):
    print(f"Open http://{site_name} in your browser.")


def enable_disable_site(enable):
    print(f"{'Enabling' if enable else 'Disabling'} the site...")
    subprocess.run(['docker-compose', 'start' if enable else 'stop'], check=True)


def delete_site(site_name):
    print("Deleting the site...")
    subprocess.run(['docker-compose', 'down'], check=True)
    os.chdir('..')
    subprocess.run(['rm', '-rf', site_name])


def main():
    if not check_docker_installed():
        install_docker()
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Please provide a site name as a command-line argument.")
        sys.exit(1)

    site_name = sys.argv[1]

    create_wordpress_site(site_name)
    add_hosts_entry(site_name)
    open_site_in_browser(site_name)

    while True:
        choice = input("Enable/disable or delete the site? (e/d/q): ")
        if choice == 'e':
            enable_disable_site(enable=True)
        elif choice == 'd':
            delete_site(site_name)
            sys.exit(0)
        elif choice == 'q':
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

