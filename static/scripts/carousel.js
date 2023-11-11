'use strict'

const flView = carousel.querySelector('.flicking-viewport')
const goodsSlide = carousel.querySelector('.goods-slide')
const goodsCard = goodsSlide.querySelector('a')

const slideWidth = goodsSlide.offsetWidth
const docWidth = document.documentElement.clientWidth
const goodsViewport = carousel.querySelector('.goods-viewport')
const goodsViewWidth = goodsViewport.offsetWidth

const dots = [...carouselNav.children]


// const offsetX = slideWidth - (docWidth - slideWidth) / 2
const offsetX = slideWidth - (goodsViewWidth - slideWidth) / 2

let activeDot = 1
let flag = false

// на больших экранах карусель некорректно работает
print([slideWidth, docWidth, offsetX, goodsViewWidth])

dots[activeDot].className = 'active'

dots.forEach((item, index, array) => {
    item.addEventListener('click', event => {
        //handle click
        // let offsetXChanged = 0

        if (item.className != 'active') {
            item.className = 'active'
            array[activeDot].className = ''
            activeDot = index
        }

        // если выбран последний слайд
        // if (index === array.length - 1)
        //     offsetXChanged = (slideWidth * index) - (docWidth - slideWidth) / 2

        // else if (index !== 0)    
        //     offsetXChanged = (slideWidth * index) - (docWidth - slideWidth) / 2

        const offsetXChanged = (slideWidth * index) - (goodsViewWidth - slideWidth) / 2
        flView.style.transform = `translateX(${-offsetXChanged}px)`
    })
});

flView.style.transform = `translateX(${-offsetX}px)`


function print(e) {
    console.log(e)
}