!function ($) {

    "use strict";

    var Typed = function (el, options) {

        // chosen element to manipulate text
        this.el = $(el);
        // options
        this.options = $.extend({}, $.fn.typed.defaults, options);

        // text content of element
        this.text = this.el.text();

        // typing speed
        this.typeSpeed = this.options.typeSpeed;

        // amount of time to wait before backspacing
        this.backDelay = this.options.backDelay;

        // input strings of text
        this.strings = this.options.strings;

        // character number position of current string
        this.strPos = 0;

        // current array position
        this.arrayPos = 0;

        // current string based on current values[] array position
        this.string = this.strings[this.arrayPos];

        // number to stop backspacing on.
        // default 0, can change depending on how many chars
        // you want to remove at the time
        this.stopNum = 0;

        // Looping logic
        this.loop = this.options.loop;
        this.loopCount = this.options.loopCount;
        this.curLoop = 1;
        if (this.loop === false) {
            // number in which to stop going through array
            // set to strings[] array (length - 1) to stop deleting after last string is typed
            this.stopArray = this.strings.length - 1;
        }
        else {
            this.stopArray = this.strings.length;
        }

        // All systems go!
        this.init();
        this.build();
    }

    Typed.prototype = {

        constructor: Typed

        , init: function () {
            // begin the loop w/ first current string (global self.string)
            // current string will be passed as an argument each time after this
            this.typewrite(this.string, this.strPos);
        }

        , build: function () {
            //this.el.after("<span id=\"typed-cursor\">|</span>");
        }

        // pass current string state to each function
        , typewrite: function (curString, curStrPos) {

            // varying values for setTimeout during typing
            // can't be global since number changes each time loop is executed
            var humanize = Math.round(Math.random() * (100 - 30)) + this.typeSpeed;
            var self = this;

            // ------------- optional ------------- //
            // backpaces a certain string faster
            // ------------------------------------ //
            // if (self.arrayPos == 1){
            // 	self.backDelay = 50;
            // }
            // else{ self.backDelay = 500; }

            // containg entire typing function in a timeout
            setTimeout(function () {

                // make sure array position is less than array length
                if (self.arrayPos < self.strings.length) {

                    // start typing each new char into existing string
                    // curString is function arg
                    self.el.text(self.text + curString.substr(0, curStrPos));

                    // check if current character number is the string's length
                    // and if the current array position is less than the stopping point
                    // if so, backspace after backDelay setting
                    if (curStrPos > curString.length && self.arrayPos < self.stopArray) {
                        clearTimeout(clear);
                        var clear = setTimeout(function () {
                            self.backspace(curString, curStrPos);
                        }, self.backDelay);
                    }

                    // else, keep typing
                    else {
                        // add characters one by one
                        curStrPos++;
                        // loop the function
                        self.typewrite(curString, curStrPos);
                        // if the array position is at the stopping position
                        // finish code, on to next task
                        if (self.loop === false) {
                            if (self.arrayPos === self.stopArray && curStrPos === curString.length) {
                                // animation that occurs on the last typed string
                                // fires callback function
                                var clear = self.options.callback();
                                clearTimeout(clear);
                            }
                        }
                    }
                }
                // if the array position is greater than array length
                // and looping is active, reset array pos and start over.
                else if (self.loop === true && self.loopCount === false) {
                    self.arrayPos = 0;
                    self.init();
                }
                else if (self.loopCount !== false && self.curLoop < self.loopCount) {
                    self.arrayPos = 0;
                    self.curLoop = self.curLoop + 1;
                    self.init();
                }

                // humanized value for typing
            }, humanize);

        }

        , backspace: function (curString, curStrPos) {

            // varying values for setTimeout during typing
            // can't be global since number changes each time loop is executed
            var humanize = Math.round(Math.random() * (100 - 30)) + this.typeSpeed;
            var self = this;

            setTimeout(function () {

                // ----- this part is optional ----- //
                // check string array position
                // on the first string, only delete one word
                // the stopNum actually represents the amount of chars to
                // keep in the current string. In my case it's 14.
                // if (self.arrayPos == 1){
                //	self.stopNum = 14;
                // }
                //every other time, delete the whole typed string
                // else{
                //	self.stopNum = 0;
                // }

                // ----- continue important stuff ----- //
                // replace text with current text + typed characters
                self.el.text(self.text + curString.substr(0, curStrPos));

                // if the number (id of character in current string) is
                // less than the stop number, keep going
                if (curStrPos > self.stopNum) {
                    // subtract characters one by one
                    curStrPos--;
                    // loop the function
                    self.backspace(curString, curStrPos);
                }
                // if the stop number has been reached, increase
                // array position to next string
                else if (curStrPos <= self.stopNum) {
                    clearTimeout(clear);
                    var clear = self.arrayPos = self.arrayPos + 1;
                    // must pass new array position in this instance
                    // instead of using global arrayPos
                    self.typewrite(self.strings[self.arrayPos], curStrPos);
                }

                // humanized value for typing
            }, humanize);

        }

    }

    $.fn.typed = function (option) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('typed')
                , options = typeof option == 'object' && option
            if (!data) $this.data('typed', (data = new Typed(this, options)))
            if (typeof option == 'string') data[option]()
        });
    }

    $.fn.typed.defaults = {
        strings: ["These are the default values...", "You know what you should do?", "Use your own!", "Have a great day!"],
        // typing and backspacing speed
        typeSpeed: 0,
        // time before backspacing
        backDelay: 500,
        // loop
        loop: false,
        // false = infinite
        loopCount: false,
        // ending callback function
        callback: function () {
            null
        }
    }


}(window.jQuery);

$(document.body).ready(function () {

    // toggle navigation
    $('.nav-toggle').click(function () {
        $('.inner').toggleClass('open');
    });

    // smooth scrolling
    $(function () {
        $('a[href*="#"]:not([href="#"])').click(function () {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                if (target.length) {
                    setTimeout(function () {
                        $('html, body').animate({
                            scrollTop: target.offset().top
                        }, 1000);
                    }, 600);
                    return false;
                }
            }
        });
    });

    var hi = $('.titanic'),
        header = $('header'),
        underline = $('.underline'),
        portfolioBox = $('.portfolio-sec'),
        project = $('.project'),
        navLink = $('.nav-link'),
        skillsBox = $('.skills-sec'),
        skills = $('.skill'),
        arrow = $('#arrow'),
        w = $(window),
        fz;

    portfolioBox.css({
        'marginBottom': $('footer').height()
    })

    TweenMax.from(hi, 5, {
        y: 140,
        opacity: 0,
        ease: Elastic.easeOut
    })

    $('.nav-link').click(function () {
        $('.inner').toggleClass('open');
    });

    $('nav li')
        .mouseenter(function (e) {
            var underline = $(this).find('div.underline'),
                width = $(this).find('span').width();
            TweenMax.to(underline, .1, {
                width: width
            });
        })
        .mouseleave(function (e) {
            var underline = $(this).find('div.underline');
            TweenMax.to(underline, .1, {
                width: 0
            });
        })

    w.scroll(function (e) {
        var wScroll = $(this).scrollTop(),
            wHeight = $(this).height();
        if (wScroll >= (header.height() - hi.height()) / 2) {

            // hi.css({
            // 	'position': 'absolute',
            // 	'top': '100%',
            // 	'transform': 'translate(-50%, -100%)'
            // })
            // TweenMax.to(hi, .5, {
            // 	color: '#333'
            // })

            // TweenMax.to(header, .5, {
            // 	backgroundColor: '#fff'
            // })

        }
        if (wScroll < (header.height() - hi.height()) / 2) {
            // hi.css({
            // 	'position': 'fixed',
            // 	'top': '50%',
            // 	'transform': 'translate(-50%, -50%)'
            // })
            // TweenMax.to(hi, .5, {
            // 	color: '#fff'
            // })


            // TweenMax.to(header, .5, {
            // 	backgroundColor: '#333'
            // })
        }
    })

    w.resize(function () {
        portfolioBox.css({
            'marginBottom': $('footer').height()
        })
    })

    $('#portfolio').waypoint(function () {
        // $('footer').css({
        // 	'display': 'block'
        // })
        TweenMax.staggerTo(project, .25, {
            'opacity': 1,
            x: 0
        }, .25)
    }, {
        offset: 300
    })


    portfolioBox.waypoint(function () {


    })

    skillsBox.waypoint(function () {
        skills.filter('.toR').css({
            'opacity': 1,
            'transform': 'translateX(0)'
        });
        skills.filter('.toL').css({
            'opacity': 1,
            'transform': 'translateX(0)'
        });
        skills.eq(1).css({
            'opacity': 1,
            'transform': 'translateY(0)'
        });
        skills.eq(4).css({
            'opacity': 1
        });
        skills.eq(7).css({
            'opacity': 1,
            'transform': 'translateY(0)'
        });


    })

    arrow.click(function () {
        $('body').animate({
            scrollTop: 0
        }, 1000);
    });

});