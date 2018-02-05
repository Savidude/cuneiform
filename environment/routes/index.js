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

module.exports = router;
