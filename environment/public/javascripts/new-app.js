var isTryVisible = true;
var currentIntent;

$( document ).ready(function() {
    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/intents",
        success: function (result) {
            // console.log(JSON.stringify(result, null, 2));
            addIntentNavs(result);
            showIntentEnvironment(result.intents[0]);
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
});

function addIntentNavs(intents) {
    var intentArray = intents.intents;
    intentArray.forEach(function (intent) {
        var navLi = document.createElement('li');
        navLi.classList.add("nav-item");
        navLi.onclick = function () {
            showIntentEnvironment(intent);
        };

        var navA = document.createElement('a');
        navA.classList.add("nav-link");
        navA.classList.add("ripple");
        navA.innerHTML = intent.name;
        navLi.appendChild(navA);

        var sideNav = document.getElementById("sidenav");
        sideNav.appendChild(navLi);
    });
}

function showIntentEnvironment(intent) {
    currentIntent = intent.name;
    var intentName = document.getElementById("intent-name");
    intentName.innerHTML = intent.name;
}

function createNewIntent() {
    window.location = '/new-intent';
}

function getIntentProperties() {
    window.location = '/intent/' + currentIntent;
}

var animationEnd = (function(el) {
    var animations = {
        animation: 'animationend',
        OAnimation: 'oAnimationEnd',
        MozAnimation: 'mozAnimationEnd',
        WebkitAnimation: 'webkitAnimationEnd'
    };

    for (var t in animations) {
        if (el.style[t] !== undefined) {
            return animations[t];
        }
    }
})(document.createElement('div'));

function toggleTry() {
    if (isTryVisible) {
        $('#properties').addClass('animated slideOutRight').one(animationEnd, function () {
            $(this).removeClass('animated slideOutRight');
            $(this).hide()
        });
    } else {
        $('#properties').show();
        $('#properties').addClass('animated slideInRight').one(animationEnd, function () {
            $(this).removeClass('animated slideInRight');
        });
    }
    isTryVisible = !isTryVisible
}