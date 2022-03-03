# calliope-explore

Manual preparation steps:

* Obtain all images and place them in `assets/img`

## Development

Requires a Python 3.8 interpreter and pipenv.

```
pipenv install
pipenv run python app.py
```

## Production

Deploying to an `aarch64` instance running the Ubuntu 20.04 image on Oracle cloud.

```
apt install python3 python3-pip supervisor certbot python3-certbot-nginx
sudo pip3 install pipenv
cd app
pipenv install
sudo cp config/calliope-explore.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo cp config/nginx-calliope-explore /etc/nginx/sites-enabled/
sudo service nginx reload
```

Open firewall:

```
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

Don't forget to also open the firewall on the cloud side, by editing the network config in the Oracle cloud console!

```
sudo certbot --nginx -d explore.callio.pe
```

Everything should now work...
