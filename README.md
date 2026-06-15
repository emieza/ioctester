# ioctester

IOC Tester és un software per gestionar tests "en viu" en màquines de prova, inicialment orientat a testejar els exercicis de l'alumnat de mòduls d'informàtica que realitzen les seves pràctiques sobre màquines virtuals, en particular sobre el sistema IsardVDI.

Aquest software permet crear una sèrie de tests que s'executaran al client que està visitant la web, via SSH (per això cal configurar les claus SSH del servidor i publicar la clau pública). Mostrarà els resultats parcials de cada prova, amb les sortides stdout i stderr, i un resum de totes les proves amb un percentatge de l'aconseguit.

Per configurar els tests cal anar al panell d'administració Django a http://elmeuserver/admin i crear al menys una categoria de proves i un Set de proves, dins el qual es podran introduïr els scripts.

Totes els intents de tests queden enregistrats al soft, tot i que de moment només son accessibles a l'admin panel, i no per a l'alumne que realitza els tests. Aquest només veu els darrers intents en la finestra principal sempre i quan no recarregui o netegi el text.

# Mètdoes d'identificació de l'alumne

Per identificar l'alumne:

  - **OAuth social login**: amb els proveïdors Google i Microsoft (cal configurar credencials a ```.env```). Es poden limitar els dominis vàlids dels emails. L'usuari es crearà si no existeix.
  - **API de IsardVDI**: identificació via adreça Mac del client (el client no ha de introduir res). Només funcionarà si tenim connexió directa entre client i servidor (la Mac no serà vàlida si no és així). Cal haver configurat ISARD_API_TOKEN amb un token vàlid d'administrador i configurar al CRON l'actualització de la taula d'adreces Mac amb la comanda ```python manage.py update_macs_from_isard```

Si es configura algun dels clients OAuth, al client no es mostrarà la identificació automàtica amb IsardVDI.

# Instal·lació sobre Debian 12 i 13

Actualitzem sistema abans de començar:

    # apt update
    # apt upgrade

Dependències del projecte

    # apt install python3-venv git apache2 libapache2-mod-wsgi-py3
    # apt install mariadb-server libmariadb-dev python3-dev gcc pkgconf

Dependències per al mòdul de Selenium (NodeJS, Firefox ESR i Selenium Driver):

    # apt install nodejs npm firefox-esr
    # npm i -g n selenium-webdriver
    # n lts

Les SSH keys son necessàries per tal que el tester pugui entrar al client i efectuar els tests.
Generar SSH keys, si no estan ja generades, **amb passphrase buida**:

    $ ssh-keygen -t rsa

Copiar la clau pública a l'arxiu ```.env```

Descàrrega del software del servidor. Es pot realitzar a l'usuari principal (per ex. ```ìsard```):

    git clone https://github.com/emieza/ioctester
    cd ioctester
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

Ajustar els paràmetres a l'arxiu ```.env```:
    SECRET_KEY=...random sequence...
    SERVER_SSH_PUBKEY=""

Ajustar els paràmetres optatius de OAuth si es vol configurar el social login.

Podem engegar el servidor en mode de desenvolupament al port 8000:

    (env) $ ./manage.py migrate
    (env) $ ./manage.py createsuperuser
    (env) $ ./manage.py runserver 0:8000

Per tal que el servidor sigui accessible pels clients cal configurar la xarxa adequadament.

## Xarxa LAN a IsardVDI

Per facilitar la connexió dels clients, cal configurar una xarxa compartida que permeti la connexió directa entre client i servidor. En IsardVDI s'aconsegueix compartint una 3a xarxa compartida entre el servidor i les VMs clients.

La configuració de xarxa en IsardVDI, tant del servidor com del client a testejar seria similar a:

  - Xarxa Default (enp1s0)
  - Xarxa Wireguard VPN (enp2s0)
  - Xarxa compartida (enp3s0)

A la xarxa compartida és on caldrà instal·lar un DHCP server al servidor per facilitar les IPs als clients i que accedeixin al IOC Tester.

El servidor el configurarem amb una IP estàtica. Afegir a ```/etc/network/interfaces```:

    allow-hotplug enp3s0
    iface enp3s0 inet static
    address 192.168.30.1
    netmask 255.255.255.0

Reiniciem xarxa perquè els canvis prenguin efecte:

    systemctl restart networking.service

El més fàcil és instal·lar ```dnsmasq``` al servidor:

    apt install dnsmasq

Editar ```/etc/dnsmasq.conf``` i afegir, per exemple:

    dhcp-range=192.168.30.20,192.168.30.220,12h

Reiniciem servei:

    systemctl restart dnsmasq.service

Si els clients tenen ben configurada la xarxa i obtenen IP del servidor, podran connectar-se amb http://192.168.30.1:8000 (servidor de desenvolupament) o http://192.168.30.1 si està en producció amb Apache i MySQL.


## Desplegament amb Apache i MySQL/MariaDB

Si es vol un entorn multiusuari concurrent, cal configurar MySQL o MariaDB (no serveix SQLite):

    $ sudo mysql
    mysql> create database ioctester;
    mysql> create user ioctester@localhost identified by "mytesterpass";
    mysql> grant all on ioctester.* to ioctester@localhost;

Configurar a ```.env```:

    DATABASE_URL=mysql://ioctester:mytesterpass@localhost:3306/ioctester

...TODO... Configurar arxius de mod_wsgi a Apache2


# Selenium JS tests

Perquè funcionin els tests de Selenium amb JavaScript cal instal·lar els drivers:

    $ sudo npm install -g selenium-webdriver
    $ export NODE_PATH=/usr/lib/node_modules

Per saber el path que cal posar, es pot saber amb:

    $ sudo npm root -g

També caldrà disposar de Firefox ESR.

L'exemple típic de Selenium en JS podria ser:

```javascript
const {Builder, Browser, By, Key, until} = require("selenium-webdriver");
const firefox = require('selenium-webdriver/firefox');
const { spawn } = require("child_process");
const assert = require('assert');

const url = "http://%IP:8000";

(async function test_exemple() {
    // Configurem driver
    let firefoxOptions = new firefox.Options();
    let driver = null;
    driver = await new Builder()
            .forBrowser(Browser.FIREFOX)
            .setFirefoxOptions(firefoxOptions)
            .build();
    try {
        // testejem LOGIN CORRECTE usuari predefinit
        //////////////////////////////////////////////////////
        await driver.get(url+"/admin/");
        await driver.findElement(By.id("id_username")).sendKeys("isard");
        await driver.findElement(By.id("id_password")).sendKeys("pirineus");
        await driver.findElement(By.xpath("//input[@value='Log in']")).click();
        await driver.sleep(1000);

    var title = await driver.getTitle();
        let assertMessage = "Site administration | Django site admin";
        assert(title==assertMessage,"ERROR TEST: el superusuari 'admin' hauria d'entrar a la pagina '"+assertMessage);

        console.log("TEST OK");

    } finally {
        // tanquem browser
        await driver.quit();
    }

})();
```


