// https://stackoverflow.com/a/41017165
"use strict";
var page = require('webpage').create(),
    system = require('system'),
    mustQuit = false,
    canShow = false,
    underAttack = false,
    address, delay;

if (system.args.length < 3 || system.args.length > 5) {
    console.log('Usage: delay.js URL delay');
    phantom.exit(1);
} else {
    address = system.args[1];
    delay = system.args[2];

    page.open(address, function (status) {
        if (status !== 'success') {
            phantom.exit(1);
        } else {
            window.setTimeout(function () {
                if (underAttack && canShow) {
                    console.log(page.content);
                    phantom.exit();
                } else {
                    phantom.exit(503);
                }
            }, delay);
            window.setTimeout(function () {
                if (mustQuit) {
                    phantom.exit(429);
                } else if (!underAttack && canShow) {
                    console.log(page.content);
                    phantom.exit();
                }
            }, 1);
        }
    });

    page.onResourceReceived = function (response) {
        switch (response.status) {
            case 200:
                canShow = true;
                break;
            case 429:
                mustQuit = true;
                break;
            case 503:
                underAttack = true;
                break;
        }
    };
}
