(function ($)
{
    var service,
        body,
        mediaStepsArr = ['xs', 'sm', 'md', 'lg', 'xl'],
        mediaSteps = {
            xl: '(min-width: 1200px)',
            lg: '(min-width: 992px)',
            md: '(min-width: 768px)',
            sm: '(min-width: 576px)',
            xs: '(min-width: 0px)'
        },
        currentStep,
        oldStep;

    /**
     * Wait document ready to initialize
     */
    $('document').ready(function ()
    {
        init();
    });

    /**
     * Initialize
     */
    function init()
    {
        body = $('body');

        currentStep = getCurrentStep();

        matchMediaChanged();

        function listener()
        {
            currentStep = getCurrentStep();

            $(window).trigger('fuse::windowResized', [currentStep, isOrBelow, isOrAbove]);

            if ( oldStep !== currentStep )
            {
                matchMediaChanged();
            }
        }

        $(window).on('resize', debounce(listener, 400));

        service = {
            watchMatchMedia         : init,
            triggerMatchMediaChanged: matchMediaChanged,
            getCurrentStep          : getCurrentStep,
            isOrAbove               : isOrAbove,
            isOrBelow               : isOrBelow
        };

        window.fuseMatchMedia = service;
    }

    /**
     * Get Current Media Step
     */
    function getCurrentStep()
    {
        var breaker = false;
        var response;

        $.each(mediaSteps, function (step, value)
        {
            if ( !breaker && window.matchMedia(value).matches )
            {
                response = step;
                breaker = true;
            }
        });

        return response;
    }

    /**
     * Match Media Change
     */
    function matchMediaChanged()
    {
        body.addClass('media-step-' + currentStep);
        body.removeClass('media-step-' + oldStep);

        oldStep = currentStep;

        $(window).trigger('fuse::matchMediaChanged', [currentStep, isOrBelow, isOrAbove]);
    }

    /**
     * Check is or above
     */
    function isOrAbove(step)
    {
        var stepVal = mediaStepsArr.indexOf(step),
            currentVal = mediaStepsArr.indexOf(currentStep);

        return currentVal >= stepVal;
    }

    /**
     * Check is or below
     */
    function isOrBelow(step)
    {
        var stepVal = mediaStepsArr.indexOf(step),
            currentVal = mediaStepsArr.indexOf(currentStep);

        return currentVal <= stepVal;
    }

    /**
     * Debounce
     */
    function debounce(func, wait, immediate)
    {
        var timeout;
        return function ()
        {
            var context = this, args = arguments;
            var later = function ()
            {
                timeout = null;
                if ( !immediate ) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if ( callNow ) func.apply(context, args);
        };
    };
})(jQuery);
