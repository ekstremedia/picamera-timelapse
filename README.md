# picamera-timelapse

If you install this on a freshly install Raspberry Pi 4/5, the first thing you need to do is to update the system and then reboot:

    sudo apt update && sudo apt full upgrade -y

    sudo reboot

Install python3 and required modules.

I use colored, PyYaml and PiCamera2 modules in these scripts.

    sudo apt install python3 python3-yaml python3-colored python3-picamera2 -y

## Image storage folder (apache)

For the folders to store the images, I install apache webserver and store the images in folders there. You dont have to, but it is very beneficial, because you can easily visit the pi on your local network to view the files.

    sudo apt install apache2 -y

Then change ownership to the /var/www/html folder to your current user (pi)

    sudo chown -R pi:www-data /var/www/html

Next, change the permissions so that the pi user and Apache can write to the directory:

    sudo chmod -R 775 /var/www/html/images

## Locale

To get your own locale for the overlay date and text, install the locale by running `raspi-config` or install from command line. 

For my locale, nb_NO:

Edit the locale settings file, and uncomment your locale

    sudo nano /etc/locale.gen

After making the changes, generate the locale and update it:

    sudo locale-gen
    sudo update-locale LANG=nb_NO.UTF-8


    
