# ioctester

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


