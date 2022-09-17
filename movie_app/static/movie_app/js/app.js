document.addEventListener("DOMContentLoaded", function() {

    if (document.querySelector('#container-slider')) {

        let sliderIndex = tns({
            container : '#container-slider',
            slideBy : 1,
            speed : 400,
            nav : false,
            autoplay : true,
            autoplayTimeout : 5000,
            autoplayButtonOutput : false,
            controlsContainer : '#container-buttons',
            prevButton : '#container-button-prev',
            nextButton : '#container-button-next',
            gutter : 20,
            responsive : {
                1700: {
                    items : 6
                },
                1400: {
                    items : 5
                },
                1100: {
                    items : 4
                },
                800: {
                    items : 3
                },
                500: {
                    items : 2
                },
                200: {
                    items : 1
                }
            },
        });
        
        sliderIndex.events.on('transitionEnd', function(){
            sliderIndex.play();
        });
    }

});