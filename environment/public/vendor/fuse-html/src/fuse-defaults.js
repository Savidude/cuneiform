(function ($)
{
    $('document').ready(function ()
    {
        $('input.form-control, textarea.form-control').fuseMdInput();

        /**
         * Centered ripples
         */
        $('.btn-toolbar .btn-group .btn:not(.dropdown-toggle), .radio-icon, .checkbox-icon, .custom-control-indicator, .pagination .page-link, .btn-icon, .btn-fab, .ripple-centered, .ripple-center').fuseRipple({fromCenter: true});

        /**
         * Deafult ripples
         */
        $('.ripple, .btn:not(.no-ripple), .radio-icon, .checkbox-icon, .custom-control-indicator, .pagination .page-link, .dropdown-item').fuseRipple();

        $(window).on('fuse::barInit fuse::barClosed fuse::asideFolded fuse::asideUnfolded', function (id, instance)
        {
            window.dispatchEvent(new Event('resize'));
        });
    });

    $(window).on('load', function ()
    {
        setTimeout(function ()
        {
            $('.fuse-cloak').removeClass('fuse-cloak');
            $('[fuse-cloak]').removeAttr('fuse-cloak');
        });
    });

})(jQuery);