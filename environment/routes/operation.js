var express = require('express');
var router = express.Router();
var fs = require('fs-extra');
var path = require('path');

var spawn = require('child_process').spawn;

var formidable = require('formidable');
var extract = require('extract-zip');

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
            if (!isUpdatingIntent) {
                // Creating Cuneiform file
                var intentsDirPath = getApplicationsDir() + path.sep + "app" + getMaxApp() + path.sep + "intents";
                var cuneiformFilePath = intentsDirPath + path.sep + intentName + ".cu";
                fs.writeFile(cuneiformFilePath, "", "utf-8", function (err) {
                    if (err) {
                        logger.error("Error while creating cuneiform file file", err);
                        res.status(500).send();
                    } else {
                        res.end('{"success" : "Intent Created", "status" : 200}');
                    }
                })
            }
            res.end('{"success" : "Intent updated", "status" : 200}');
        }
    })
});

/*
Searching intents by name
 */
router.post('/intent/get', function (req, res) {
    var intents = getIntents();
    var intentName = req.body.name;
    var result;

    intents['intents'].forEach(function (intent) {
        if (intent.name === intentName) {
            result = intent;
        }
    });

    if (result !== undefined) {
        res.status(200).json(result);
    } else {
        res.status(404).send();
    }
});

/*
Communication interface with the responder
 */
router.post('/responder', function (req, res) {
    var input_data = {};
    input_data['sessionid'] = req.body.sessionid;
    input_data['message'] = req.body.message;

    var py = spawn("python3", [getResponder()]);
    var responseData;
    py.stdout.on("data", function (data) {
        responseData = JSON.parse(data.toString());
        /*
        Expected format of responseData
            responseData = {"sessionid": sessionId, "response": "Sample Response"}
         */

    });
    py.stdout.on("end", function () {
        if (responseData !== undefined) {
            res.status(200).json(responseData);
        } else {
            res.status(500).send();
        }
    });

    py.stdin.write(JSON.stringify(input_data));
    py.stdin.end();
});

/*
Getting intent data from the UI and converting into cuneiform file
 */
router.post('/intent/:name/save', function (req, res) {
    var name = req.params.name;
    var code = req.body;

    var intentsDirPath = getApplicationsDir() + path.sep + "app" + getMaxApp() + path.sep + "intents";
    var cuneiformFilePath = intentsDirPath + path.sep + name + ".cu";
    fs.writeFile(cuneiformFilePath, code, "utf-8", function (err) {
        if (err) {
            logger.error("Error while updating cuneiform file", err);
            res.status(500).send();
        } else {
            logger.info("Cuneiform file updated");
            res.set('Content-Type', 'application/json');
            res.end('{"success" : "File updated", "status" : 200}');
        }
    })
});

/*
Getting intent code data
 */
router.post('/intent/code', function (req, res) {
    var name = req.body.name;
    var input_data = {};
    input_data['name'] = name;

    var py = spawn("python3", [getIntentAST()]);
    var intent_data;
    py.stdout.on("data", function (data) {
        intent_data = JSON.parse(data.toString());
    });
    py.stdout.on("end", function () {
        if (intent_data !== undefined) {
            res.status(200).json(intent_data);
        } else {
            res.status(500).send();
        }
    });

    py.stdin.write(JSON.stringify(input_data));
    py.stdin.end();
});

/*
Uploading Cuneiform application
 */
router.post('/upload/app', function (req, res) {
    var form = new formidable.IncomingForm();
    form.parse(req, function (err, fields, files) {
        var oldPath = files.application.path;
        var newPath = getApplicationsDir() + path.sep + "app" + (getMaxApp() + 1) + ".zip";
        fs.rename(oldPath, newPath, function (err) {
            if (err) {
                logger.err("Error while uploading application", err);
            } else {
                var newAppDir = getApplicationsDir() + path.sep + "app" + (getMaxApp() + 1);
                extract(newPath, {dir: getApplicationsDir()}, function (err) {
                    if (err) {
                        logger.err("Error while renaming directory", err);
                    } else {
                        var apps = getDirectories(getApplicationsDir());
                        apps.forEach(function (app) {
                            if (!app.startsWith("app")) {
                                fs.rename(getApplicationsDir() + path.sep + app, newAppDir, function (err) {
                                    if (err) {
                                        logger.err("Error while renaming directory", err);
                                    } else {
                                        fs.remove(newPath, function (err) {
                                            if (err) {
                                                logger.err("Error while removing zip file", err);
                                            } else {
                                                res.redirect('/app')
                                            }
                                        })
                                    }
                                });
                            }
                        });
                    }
                });
            }
        });
    });
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

function getResponder() {
    return __dirname.replace("environment" + path.sep + "routes",
        "responder" + path.sep + "responder.py");
}

function getIntentAST() {
    return __dirname.replace("environment" + path.sep + "routes",
        "manager" + path.sep + "ast.py");
}