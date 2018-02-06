var express = require('express');
var router = express.Router();
var fs = require('fs-extra');
var path = require('path');

//Instantiating logger
var winston = require('winston');
var logger = new (winston.Logger)({
    transports: [
        new (winston.transports.Console)(),
        new (winston.transports.File)({
            filename: 'log/operations.log',
            timestamp: function() {
                var currentdate = new Date;
                var timestamp = currentdate.getFullYear() + "-"
                    + (currentdate.getMonth()+1)  + "-"
                    + currentdate.getDate() + "T"
                    + currentdate.getHours() + ":"
                    + currentdate.getMinutes() + ":"
                    + currentdate.getSeconds();
                return timestamp;
            },
            formatter: function(options) {
                // Return string will be passed to logger.
                return options.timestamp() +' ['+ options.level.toUpperCase() +'] '+ (options.message ? options.message : '') +
                    (options.meta && Object.keys(options.meta).length ? '\n\t'+ JSON.stringify(options.meta) : '' );
            },
            json:false
        })
    ]
});

/*
Creating new project
 */
router.post('/new/app', function (req, res) {
    var appName = req.body.name;
    var newAppDir = __dirname.replace("routes", "public" + path.sep + "resources" + path.sep + "new_app");

    var appDirNo = getMaxApp();
    var createdAppDir = getApplicationsDir() + path.sep + "app" + (appDirNo + 1);
    fs.ensureDir(createdAppDir);

    fs.copy(newAppDir, createdAppDir, function (err) {
        if (err) {
            logger.err("Error while creating new application directory", err);
            res.status(500).send();
        } else {
            var newAppFile = createdAppDir + path.sep + "app.json";
            fs.readFile(newAppFile, "utf-8", function (err, data) {
                if (err) {
                    logger.error("Error while reading app.json", err);
                    res.status(500).send();
                } else {
                    var newValue = data.replace("app_name", appName);
                    fs.writeFile(newAppFile, newValue, "utf-8", function (err) {
                        if (err) {
                            logger.error("Error while writing to app.json", err);
                            res.status(500).send();
                        } else {
                            logger.info("New app '" + appName + "' created.");
                            res.end('{"success" : "App created", "status" : 200}');
                        }
                    })
                }
            });
        }
    });
});

/*
Getting intents
 */
router.post('/intents', function (req, res) {
    var intents = getIntents();
    res.status(200).json(intents);
});


/*
If the intent does not exist, update the intent. Else, create new intent.
 */
router.post('/intent/update', function (req, res) {
    var intent = req.body;
    var intentName = intent.name;
    var systemIntents = getIntents();

    var isUpdatingIntent = false;
    systemIntents['intents'].forEach(function (systemIntent) {
        if (systemIntent['name'] === intentName) {
            isUpdatingIntent = true;
            systemIntent['initiative'] = intent.initiative;
            systemIntent['sample_utterances'] = intent.sample_utterances;
            systemIntent['slots'] = intent.slots;
        }
    });

    if (!isUpdatingIntent) {
        systemIntents['intents'].push(intent);
    }

    var intentsFilePath = getApplicationsDir() + path.sep + "app" + getMaxApp() + path.sep + "intents" + path.sep + "intents.json";
    fs.writeFile(intentsFilePath, JSON.stringify(systemIntents, null, 2), "utf-8", function (err) {
        if (err) {
            logger.error("Error while updating intents.json file", err);
            res.status(500).send();
        } else {
            logger.info("Intents updated");
            res.end('{"success" : "App created", "status" : 200}');
        }
    })
});

module.exports = router;

function getApplicationsDir() {
    return __dirname.replace("environment" + path.sep + "routes",
        "resources" + path.sep + "deployment" + path.sep + "applications");
}

function getMaxApp() {
    var apps = getDirectories(getApplicationsDir());
    var maxApp = 0;
    apps.forEach(function (app) {
        var appNo = app.replace("app", "");
        appNo = parseInt(appNo);
        if (appNo > maxApp) {
            maxApp = appNo;
        }
    });
    return maxApp;
}

function getDirectories(path) {
    return fs.readdirSync(path).filter(function (file) {
        return fs.statSync(path+'/'+file).isDirectory();
    });
}

function getIntents() {
    var intentsFilePath = getApplicationsDir() + path.sep + "app" + getMaxApp() + path.sep + "intents" + path.sep + "intents.json";
    var intents = fs.readFileSync(intentsFilePath);
    var intentsJson = JSON.parse(intents);
    return intentsJson;
}