/*
 * wip ripple effect
 */
;(function ($, window, document, undefined)
{
    // Create the defaults once
    var pluginName = 'fuseRipple',
        defaults = {
            duration  : 300,//ms
            fromCenter: false
        };

    var TagWrapper = {

        // Wrap <input> tag so it can perform the effect
        input: function (element)
        {

            var parent = element.parentNode;

            // If input already have parent just pass through
            if ( parent.tagName.toLowerCase() === 'span' && parent.classList.contains('fuse-ripple-ready') )
            {
                return;
            }

            // Put element class and style to the specified parent
            var wrapper = document.createElement('span');
            wrapper.className = element.className + ' fuse-ripple-input-wrapper';
            element.className = 'fuse-ripple-input';

            // Put element as child
            parent.replaceChild(wrapper, element);
            wrapper.appendChild(element);

            // Apply element color and background color to wrapper
            /*  var elementStyle = window.getComputedStyle(element, null);
             var color = elementStyle.color;
             var backgroundColor = elementStyle.backgroundColor;

             wrapper.setAttribute('style', 'color:' + color + ';background:' + backgroundColor);
             element.setAttribute('style', 'background-color:rgba(0,0,0,0);');*/

        },

        // Wrap <img> tag so it can perform the effect
        img: function (element)
        {

            var parent = element.parentNode;

            // If input already have parent just pass through
            if ( parent.tagName.toLowerCase() === 'span' && parent.classList.contains('fuse-ripple-ready') )
            {
                return;
            }

            // Put element as child
            var wrapper = document.createElement('span');
            parent.replaceChild(wrapper, element);
            wrapper.appendChild(element);

        }
    };

    // The actual plugin constructor
    function Plugin(element, options)
    {
        this.element = element;

        // the default options for future instances of the plugin
        this.options = $.extend({}, defaults, options);

        this._defaults = defaults;
        this._name = pluginName;

        this.init();
    }

    Plugin.prototype = {

        init: function ()
        {
            var body = document.body;
            var self = this;
            var el;

            el = self.element;

            var tagName = self.element.tagName.toLowerCase();

            if ( ['input', 'img'].indexOf(tagName) !== -1 )
            {
                TagWrapper[tagName](self.element);
                el = self.element.parentElement;
            }

            if ( !$(el).hasClass('fuse-ripple-ready') )
            {
                $(el).addClass('fuse-ripple-ready');
            }

            el.addEventListener('mousedown', triggerRippleEvent);

            function triggerRippleEvent(ev)
            {
                ev.stopPropagation();
                self.triggerRipple(el, self.options, ev);
            }
        },

        triggerRipple: function (element, options, ev)
        {

            var el = $(element);

            // Remove the previous ripple before starting to a new one
            var rippleExist = el.find('.fuse-ripple').length > 0;

            if ( rippleExist )
            {
                el.find('.fuse-ripple').remove();
            }

            // Create ripple
            var ripple = $('<div class="fuse-ripple">');

            // Get click coordinate and element width
            var pos = el.offset();
            var relativeY = 0;
            var relativeX = 0;

            // Support for touch devices
            if ( 'touches' in ev && ev.touches.length )
            {
                relativeY = (ev.touches[0].pageY - pos.top);
                relativeX = (ev.touches[0].pageX - pos.left);
            }
            //Normal case
            else
            {
                relativeY = (ev.pageY - pos.top);
                relativeX = (ev.pageX - pos.left);
            }

            var elWidth = el.outerWidth();
            var elHeight = el.outerHeight();

            // Calculate ripple diameter
            var surfaceDiameter = Math.sqrt(Math.pow(elWidth, 2) + Math.pow(elHeight, 2));

            // Calculate ripple initial size
            var initialSize = (Math.max(elWidth, elHeight)) * 0.6;

            var scale = 'scale(1)';
            var translateX = parseInt(relativeX - (initialSize / 2));
            var translateY = parseInt(relativeY - (initialSize / 2));
            var translate = 'translate(' + translateX + 'px ,' + translateY + 'px)';

            if ( options.fromCenter )
            {
                translate = 'translate(' + parseInt(elWidth * 0.2) + 'px ,' + parseInt(elHeight * 0.2) + 'px)';
            }

            var transform = scale + ' ' + translate;
            var scaleRatio = surfaceDiameter / initialSize;
            var endScale = 'scale(' + scaleRatio + ')';
            var endTranslate = 'translate(' + (elWidth - initialSize) * .5 / scaleRatio + 'px ,' + (elHeight - initialSize) * .5 / scaleRatio + 'px)';
            var endTransform = endScale + ' ' + endTranslate;
            var endTransition = 'opacity ' + options.duration + 'ms linear, transform  ' + options.duration + 'ms cubic-bezier(0.4, 0, 0.2, 1)';

            if ( options.fromCenter )
            {
            }

            var startStyle = {
                width    : initialSize + 'px',
                height   : initialSize + 'px',
                transform: transform,
                opacity  : 1
            };

            var endStyle = {
                opacity   : '0',
                transform : endTransform,
                transition: endTransition,
            };

            $(ripple).css(startStyle);
            el.append(ripple);

            setTimeout(function ()
            {
                $(ripple).css(endStyle);
            });

            setTimeout(function ()
            {
                el.find(ripple).remove();
            }, options.duration);

        }
    };

    // Plugin wrapper around the constructor,
    // preventing against multiple instantiations
    $.fn[pluginName] = function (options)
    {
        return this.each(function ()
        {
            if ( !$.data(this, 'plugin_' + pluginName) )
            {
                $.data(this, 'plugin_' + pluginName,
                    new Plugin(this, options));
            }
        });
    };

})(jQuery, window, document);
