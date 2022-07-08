const zIndex = 1040 + 10 * $('.modal:visible').not(this).length;
$(this).css('z-index', zIndex);
setTimeout(() => $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack'));