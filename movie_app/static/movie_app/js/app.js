document.addEventListener("DOMContentLoaded", function() {

    if (document.querySelector('.container-slider-style')) {
        let sliderContainer = document.querySelector('.container-slider-style');
        
        let sliderIndex = tns({
            container : sliderContainer.firstElementChild,
            slideBy : 1,
            speed : 400,
            nav : false,
            autoplay : true,
            autoplayTimeout : 5000,
            autoplayButtonOutput : false,
            controlsContainer : sliderContainer.lastElementChild,
            prevButton : sliderContainer.lastElementChild.firstElementChild,
            nextButton : sliderContainer.lastElementChild.lastElementChild,
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

    function setVisibleSearch (element) {
        
        let buttonMore = element.previousElementSibling.firstElementChild.querySelector('.button-more');
        let buttonLess = element.previousElementSibling.firstElementChild.querySelector('.button-less');
        
        if (element.dataset.is_valid == 'False') {
            element.classList.remove('display-none');
            buttonLess.classList.remove('display-none');
            buttonMore.classList.add('display-none');
        };

        buttonMore.addEventListener('click', function(){
            element.classList.remove('display-none');
            buttonLess.classList.remove('display-none');
            buttonMore.classList.add('display-none');
        })
        buttonLess.addEventListener('click', function(){
            element.classList.add('display-none');
            buttonLess.classList.add('display-none');
            buttonMore.classList.remove('display-none');
        })
    }

    if (document.querySelector('#form-person-search')) {
        
        setVisibleSearch(document.querySelector('#form-person-search'));
    }

    if (document.querySelector('#form-movie-search')) {
        
        setVisibleSearch(document.querySelector('#form-movie-search'));
    }


    function addSlider(element) {
        
        let containerSlider = element.querySelector('.card-slider-row-style');
        let buttonsSlider = element.querySelector('.card-slider-button-style')
        let prevButtonSlider = element.querySelector('.prev');
        let nextButtonSlider = element.querySelector('.next');

        if (! prevButtonSlider.classList.contains('display-none-important')) {
            prevButtonSlider.classList.add('display-none-important')
        }
        if (nextButtonSlider.classList.contains('display-none-important')) {
            nextButtonSlider.classList.remove('display-none-important')
        }

        let slider = tns({
            container : containerSlider,
            speed : 400,
            nav : false,
            loop : false,
            fixedWidth: 150,
            gutter : 25,
            controlsContainer : buttonsSlider,
            prevButton : prevButtonSlider,
            nextButton : nextButtonSlider,
        });
        
        slider.events.on('transitionEnd', function(){
            let info = slider.getInfo();
            if (info.prevButton.hasAttribute('disabled')) {
                info.prevButton.classList.add('display-none-important');
            }
            else {
                info.prevButton.classList.remove('display-none-important');
            }
            if (info.nextButton.hasAttribute('disabled')) {
                info.nextButton.classList.add('display-none-important');
            }
            else {
                info.nextButton.classList.remove('display-none-important');
            }
        });
    }
    
    if (document.querySelector('#characters')) {
        addSlider(document.querySelector('#characters').nextElementSibling);
    }

    if (document.querySelector('#movies')) {
        let allButtons = document.querySelectorAll('[data-button]')
        let allCards = document.querySelectorAll('[data-card]');

        setVisible(allButtons[0]);
        
        allButtons.forEach(function(element) {
            element.addEventListener('click', function(e){
                setVisible(e.target);
            });
        });
        
        function setVisible(e){
            allButtons.forEach(function(element) {
                if (element == e){
                    element.nextElementSibling.classList.remove('display-none');
                    element.classList.add('display-none')
                }
                else {
                    element.nextElementSibling.classList.add('display-none')
                    element.classList.remove('display-none')   
                }
            });

            allCards.forEach(function(element) {
                if (element.dataset.card == e.dataset.button) {
                    element.classList.remove('display-none');
                    addSlider(element);
                }
                else {
                    element.classList.add('display-none');
                }
            });
        }   
    };

    if (document.querySelector('#form-character-container')){
        
        let containerForm = document.querySelector("#form-character-container");
        let addButton = containerForm.querySelector("#button-character-add");
        let totalForms = containerForm.querySelector("#id_step4-TOTAL_FORMS");
        let headerForm = containerForm.querySelector('#header-character');
        let allForms = containerForm.querySelectorAll('.form-character-row');

        let formNum = allForms.length;

        addButton.addEventListener('click', addForm);

        allForms.forEach(function(element) {
            if (element.querySelector('input[type=checkbox]').checked){
                element.querySelector('input[type=checkbox]').checked = false;
            };
            element.querySelector('.button-delete-character-style').addEventListener('click', deleteForm);
        });

        let baseForm = allForms[0].cloneNode(true)
        baseForm.querySelector('input[type=text]').removeAttribute('value');
        baseForm.lastElementChild.lastElementChild.removeAttribute('value');
        deleteError(baseForm.querySelector('select'));
        deleteError(baseForm.querySelector('input[type=text]'));
        if (baseForm.firstElementChild.tagName == 'p'){
            baseForm.removeChild(baseForm.firstElementChild);
        }

        let lastForm = allForms[formNum-1]
        if (formNum > 1 && lastForm.querySelector('select').value == '' && lastForm.querySelector('input[type=text]').value == '') {
            containerForm.removeChild(lastForm);
            formNum--
            totalForms.setAttribute('value', `${formNum}`)
        }

        function addForm(e) {
            
            e.preventDefault();

            let newForm = baseForm.cloneNode(true);
            let formRegex = RegExp(`step4-(\\d){1}-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `step4-${formNum}-`);
            newForm.querySelector('.button-delete-character-style').addEventListener('click', deleteForm);
            
            newForm.querySelector('select').value = '';
            
            containerForm.insertBefore(newForm, containerForm.lastElementChild);
            headerForm.classList.remove('display-none');

            formNum++;
            totalForms.setAttribute('value', `${formNum}`)
        }

        function deleteForm(e) {
            
            let deleteElement = e.target.parentElement.parentElement;
            if (deleteElement.lastElementChild.lastElementChild.value) {
                deleteElement.querySelector('input[type=checkbox]').checked = true;
                deleteElement.classList.add('display-none');
            }
            else {
                deleteElement.parentElement.removeChild(deleteElement);
            }
            if (containerForm.querySelectorAll('.form-character-row').length == containerForm.querySelectorAll('.form-character-row.display-none').length) {
                headerForm.classList.add('display-none');
            }
        }

        function deleteError(element) {
            
            if (element.parentElement.childElementCount > 1) {
                element.classList.remove('is-invalid');
                element.parentElement.removeChild(element.parentElement.lastElementChild);
            };
        }
    }


    function setVisibleText (contentText, indexToCut) {

        let textHidden = contentText.parentElement.querySelector('.text-hidden');
        let dotsElement = contentText.parentElement.querySelector('.dots');
        let buttonMore = contentText.parentElement.querySelector('.button-more');
        let buttonLess = contentText.parentElement.querySelector('.button-less');
        textHidden.textContent = contentText.textContent.slice(indexToCut);
        contentText.textContent = contentText.textContent.slice(0, indexToCut);
        buttonMore.classList.remove('display-none');
        dotsElement.classList.remove('display-none')
    
        buttonMore.addEventListener('click', function(){
            textHidden.classList.remove('display-none');
            buttonLess.classList.remove('display-none');
            buttonMore.classList.add('display-none');
            dotsElement.classList.add('display-none')
        })
        buttonLess.addEventListener('click', function(){
            textHidden.classList.add('display-none');
            buttonLess.classList.add('display-none');
            buttonMore.classList.remove('display-none');
            dotsElement.classList.remove('display-none')
        })
    }

    if (document.querySelectorAll('.text-content').length) {
        document.querySelectorAll('.text-content').forEach(function(element) {
            if (element.parentElement.classList.contains('text-comment-style')){
                let indexToCut = 500 + element.textContent.slice(500).indexOf(' ');
                if (indexToCut >= 500) {
                    setVisibleText(element, indexToCut)
                }
            }
            else {
                let indexToCut = 1000 + element.textContent.slice(1000).indexOf(' ');
                if (indexToCut >= 1000) {
                    setVisibleText(element, indexToCut)
                }
            }
        });
    }

});