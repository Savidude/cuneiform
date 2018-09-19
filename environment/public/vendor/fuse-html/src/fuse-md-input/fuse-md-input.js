(function ($)
{

    $.fn.fuseMdInput = function ()
    {
        initialize(this);
    }

    function initialize(selectorEl)
    {
        var inputs = selectorEl;
        for ( var i = 0, input; input = inputs[i]; i++ )
        {
            toggleHasValueClass($(input));
        }

        inputs.on('blur', onInputBlur);

        inputs.on('focus', onInputFocus)
    }

    function onInputBlur(input)
    {
        var el = $(this);
        toggleHasValueClass(el);
        removeFocusGroupClass(el);
    }

    function onInputFocus(input)
    {
        var el = $(this);
        addHasValueInputClass(el);
        addFocusGroupClass(el);
    }

    function toggleHasValueClass(el)
    {
        if ( el.val().length !== 0 )
        {
            addHasValueInputClass(el);
        }
        else
        {
            removeHasValueInputClass(el);
        }
    }

    function addHasValueInputClass(el)
    {
        el.addClass('md-has-value');
    }

    function removeHasValueInputClass(el)
    {
        el.removeClass('md-has-value');
    }

    function addFocusGroupClass(el)
    {
        if ( !el.parent().hasClass('form-group') )
        {
            return;
        }
        el.parent('.form-group').addClass('md-focus');
    }

    function removeFocusGroupClass(el)
    {
        if ( !el.parent().hasClass('form-group') )
        {
            return;
        }
        el.parent('.form-group').removeClass('md-focus');
    }

})(jQuery);
