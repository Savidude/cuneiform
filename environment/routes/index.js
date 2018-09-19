var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Cuneiform Home' });
});

/* GET app page */
router.get('/app', function(req, res, next) {
    res.render('app', { title: 'Development Environment - Cuneiform' });
});

/*
Get new intent settings page
 */
router.get('/new-intent', function(req, res, next) {
    res.render('intent', { title: 'Intent Settings - Cuneiform' });
});

/*
Get settings page for intent by name
 */
router.get('/intent/:name', function(req, res, next) {
    var name = req.params.name;
    res.render('intent-edit', { title: 'Intent Settings - Cuneiform', intent_name: name });
});

module.exports = router;
