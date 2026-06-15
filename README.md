# ioctester

IOC Tester és un software per gestionar tests "en viu" en màquines de prova, inicialment orientat a testejar els exercicis de l'alumnat de mòduls d'informàtica que realitzen les seves pràctiques sobre màquines virtuals, en particular sobre el sistema IsardVDI.

Aquest software permet crear una sèrie de tests que s'executaran al client que està visitant la web, via SSH (per això cal configurar les claus SSH del servidor i publicar la clau pública). Mostrarà els resultats parcials de cada prova, amb les sortides stdout i stderr, i un resum de totes les proves amb un percentatge de l'aconseguit.

Per configurar els tests cal anar al panell d'administració Django a http://elmeuserver/admin i crear al menys una categoria de proves i un Set de proves, dins el qual es podran introduïr els scripts.

Totes els intents de tests queden enregistrats al soft, tot i que de moment només son accessibles a l'admin panel, i no per a l'alumne que realitza els tests. Aquest només veu els darrers intents en la finestra principal sempre i quan no recarregui o netegi el text.

# Mètdoes d'identificació de l'alumne

Per identificar l'alumne:

  - **OAuth social login**: amb els proveïdors Google i Microsoft (cal configurar credencials a ```.env```). Es poden limitar els dominis vàlids dels emails. L'usuari es crearà si no existeix.
  - **API de IsardVDI**: identificació via adreça Mac del client (el client no ha de introduir res). Cal haver configurat ISARD_API_TOKEN amb un token vàlid d'administrador i configurar al CRON l'actualització de la taula d'adreces Mac amb la comanda ```python manage.py update_macs_from_isard```

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

Les SSH keys son necessàries per poder entrar al client
Generar SSH keys, si no estan ja generades, **amb passphrase buida**:

    $ ssh-keygen -t rsa

Copiar la clau pública

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


