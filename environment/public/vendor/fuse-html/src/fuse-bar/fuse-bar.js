(function ($)
{
    var backdropEl = false;
    var fuseBar;

    window.fuseBar = fuseBar = {
        instances: {},
        toggle   : toggleBar,
        closeAll : closeAll
    };

    /**
     * Get Instance by id
     */
    function instanceById(id)
    {
        return fuseBar.instances[id]
    }

    /**
     * Toggle Bar
     */
    function toggleBar(id)
    {
        var instance = instanceById(id);

        if ( !instance.isActive )
        {
            return;
        }

        if ( instance.opened )
        {
            closeBar(id);
        }
        else
        {
            openBar(id);
        }
    }

    /**
     * Close Bar
     */
    function closeBar(id, onInit)
    {
        var dfd = jQuery.Deferred();

        var instance = instanceById(id);

        instance.el.css({
            transform: ''
        });


        if ( onInit )
        {
            resolve();
        }
        else
        {
            setTimeout(resolve, 300);
        }

        function resolve()
        {
            instance.el.removeClass('fuse-bar-open');
            instance.el.addClass('fuse-bar-closed');
            dfd.resolve('closed');
        }


        instance.opened = false;

        if ( backdropEl )
        {
            backdropEl.fadeOut(function ()
            {
                $(this).remove();
            });
        }

        triggerEvent('fuse::barClosed', [id, instance]);

        return dfd.promise();
    }

    /**
     * Open Bar
     */
    function openBar(id)
    {
        closeAll().then(function ()
        {
            var instance = instanceById(id);

            instance.el.css({
                transform: 'translate3D(0,0,0)'
            });

            instance.el.removeClass('fuse-bar-closed');
            instance.el.addClass('fuse-bar-open');

            instance.opened = true;

            backdropEl = $('<div class="fuse-bar-backdrop fuse-bar-backdrop-' + id.replace(' ', '-') + '"></div>');

            backdropEl.hide();

            instance.el.after(backdropEl);

            backdropEl.fadeIn();

            backdropEl.on('click', function (ev)
            {
                ev.preventDefault();
                ev.stopPropagation();
                closeBar(id);
            });

            triggerEvent('fuse::barOpened', [id, instance]);
        });
    }

    /**
     * Wait document ready to initialize
     */
    $('document').ready(function ()
    {

        $('[data-fuse-bar]').each(function (ev)
        {
            register($(this));
        });

        $('[data-fuse-bar-toggle]').on('click', function (ev)
        {
            var id = $(this).data('fuse-bar-toggle');

            toggleBar(id);
        });

        $('[data-fuse-bar-close]').on('click', function (ev)
        {
            var id = $(this).data('fuse-bar-close');
            closeBar(id);
        });


        $(window).on('fuse::matchMediaChanged', watchMatchMediaChange);

    });

    /**
     * Initialize
     */
    function init(instance)
    {
        instance.el.addClass('fuse-bar');
        instance.el.addClass('position-' + instance.position);
        instance.isActive = true;
        triggerEvent('fuse::barInit', [instance.id, instance]);
    }

    /**
     * Destroy
     */
    function destroy(instance)
    {
        instance.el.removeClass('fuse-bar');
        instance.el.removeClass('position-' + instance.position);
        instance.isActive = false;
        triggerEvent('fuse::barDestroy', [instance.id, instance]);
    }

    /**
     * Register
     */
    function register(barEl)
    {
        var id = barEl.data('fuse-bar');
        var mediaStep = barEl.data('fuse-bar-media-step');
        var position = barEl.data('fuse-bar-position');

        fuseBar.instances[id] = {
            id       : id,
            el       : barEl,
            mediaStep: mediaStep || false,
            opened   : false,
            isActive : false,
            position : position || 'left'
        };

        instanceCheck(fuseBar.instances[id]);
    }

    /**
     * Watch Media steps to initialize
     */
    function watchMatchMediaChange(ev, currentStep, isOrBelow, isOrAbove)
    {
        $.each(fuseBar.instances, function (id, instance)
        {
            instanceCheck(instance);
        });

        closeAll();
    }

    /**
     * Check Instance Init or Destroy
     * @param instance
     */
    function instanceCheck(instance)
    {
        if ( instance.mediaStep )
        {
            if ( window.fuseMatchMedia.isOrBelow(instance.mediaStep) )
            {
                init(instance);
            }
            else
            {
                destroy(instance);
            }
        }
        else
        {
            init(instance);
            closeBar(instance.id, true);
        }
    }

    $(window).on('resize', onResize);

    function onResize()
    {
    }

    function closeAll()
    {
        var promises = [];

        $.each(fuseBar.instances, function (id, instance)
        {
            if ( instance.opened )
            {
                promises.push(closeBar(id));
            }
        });

        return $.when.apply($, promises);
    }

    /**
     * Trigger Event
     */
    function triggerEvent(event, data)
    {
        setTimeout(function ()
        {
            $(window).trigger(event, data);
        }, 300)
    }
})(jQuery);
